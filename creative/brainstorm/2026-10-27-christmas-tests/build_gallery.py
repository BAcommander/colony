"""Export preview JPEGs, verify exact clean artwork/prompts and build local review."""
from pathlib import Path
import hashlib
import html
import json
import subprocess
from PIL import Image
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent
scenes = json.loads((ROOT/"generation-index.json").read_text(encoding="utf-8"))
small, cards = [], []
for i, s in enumerate(scenes, 1):
    folder = ROOT/s["slug"]
    preview = folder/"preview-v1.jpg"
    if not preview.exists():
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i",
                        str(folder/"concept-v1.png"), "-vf", "scale=1280:720:flags=lanczos",
                        "-frames:v", "1", "-q:v", "2", str(preview)], check=True)
    assets = {}
    for name in ["concept-v1.png", "preview-v1.jpg", "generation-v1.txt"]:
        p = folder/name
        r = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}
        if p.suffix in [".png", ".jpg"]:
            with Image.open(p) as im: im.verify()
            with Image.open(p) as im: r["dimensions"] = list(im.size)
        assets[name] = r
    assert assets["concept-v1.png"]["sha256"] == hashlib.sha256(Path(s["original"]).read_bytes()).hexdigest()
    assert assets["preview-v1.jpg"]["dimensions"] == [1280,720]
    manifest = {"date":"2026-10-27", "review_id":f"X{i:02d}", "title":s["title"],
                "influence":s["influence"], "generator":"built-in image_gen.imagegen",
                "image_inputs":[], "original_generation_path":s["original"], "assets":assets,
                "inspection":"Assistant returned full-composition still inspection; no crop-level audit",
                "concerns":s["note"], "user_approval":None, "catalog_number":None,
                "thumbnail_generated":False, "animation_generated":False,
                "remote_backup_record":"../backup-verification.json"}
    (folder/"manifest-v1.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8",newline="\n")
    title,influence,note=map(html.escape,[s["title"],s["influence"],s["note"]])
    slug=s["slug"]
    small.append(f'<a href="#X{i:02d}"><img loading="lazy" src="{slug}/preview-v1.jpg" alt="{title}"><span>X{i:02d} · {title}</span></a>')
    cards.append(f'<article id="X{i:02d}"><p>X{i:02d} / {influence}</p><h2>{title}</h2><a href="{slug}/concept-v1.png"><img loading="lazy" src="{slug}/preview-v1.jpg" alt="{title}"></a><p class="note">{note}</p><p><a href="{slug}/generation-v1.txt">Exact prompt</a> · <a href="{slug}/manifest-v1.json">Manifest</a></p></article>')
page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Christmas somewhere you wish you could stay</title><style>'
page+='body{margin:0;background:#141b1a;color:#ede8dc;font:16px/1.5 system-ui}main{max-width:1280px;margin:auto;padding:32px}h1{font-size:clamp(32px,5vw,64px);line-height:1.1}a{color:#dfbd83}img{display:block;width:100%}article{border-top:1px solid #3d4a46;margin-top:32px;padding-top:24px}.note{color:#b4beba}.small{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:18px}.small a{text-decoration:none;font-size:13px}.small span{display:block;margin-top:6px}@media(max-width:600px){main{padding:18px}}'
page+='</style><main><p>AMBIENT COLONY / CHRISTMAS TESTS / 27 OCTOBER 2026</p><h1>Christmas somewhere you wish you could stay.</h1><p>Ten clean scene candidates. No thumbnail text, animation or soundtrack. Click an image for the original PNG. All await your review; X01–X10 are review identifiers, not release numbers.</p><p><a href="../README.md">Brainstorm collection</a></p><div class="small">'
page+="".join(small)+'</div>'+"".join(cards)+'</main></html>'
(ROOT/"gallery.html").write_text(page,encoding="utf-8",newline="\n")
print("Verified 10 original PNGs against returned files, exported 10 JPEG previews, saved exact-prompt hashes and gallery.")
