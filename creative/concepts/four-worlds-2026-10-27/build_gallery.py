"""Create file inventory, standard thumbnail JPEGs and a local comparison gallery."""
import hashlib
import html
import json
from pathlib import Path
import subprocess
import sys
import imageio_ffmpeg
from PIL import Image

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
scenes = json.loads((ROOT / "generation-index.json").read_text(encoding="utf-8"))
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
notes = [
    "Strong workshop/hull scale contrast. Dense machinery and wet paving need fine-geometry review; thumbnail adds warmer sky.",
    "Readable institutional scale, but landscape looks terrestrial. Confirm sealed booth glazing before animation; thumbnail adds sunset.",
    "Layered civic life and warm radio corner. Inspect bridge supports and fine town geometry; thumbnail adds warmer sky.",
    "Clear retrofuturist mess/green-bridge distinction. Fine hatch, seats and controls remain unreviewed at crop scale.",
    "Strong green-console/storm-pad contrast. Generator added a craft not requested in brief; inspect craft and pad before selection.",
    "Immense machinery, but visual density may reduce small-size clarity. Glass/pressure boundary needs explicit fine review.",
    "Strong monumental silhouette and dust wall. Hard reflective floor and extreme gate scale need review.",
    "Quiet reservoir scale reads more like a historic cistern than overt sci-fi. Gallery water separation needs detail review.",
    "Clear coastal refuge, but source-specific identity is less immediate than the storm gate. Inspect terrace support/glazing.",
    "Rock-walled canteen establishes working settlement. Ship and furniture are dense; spin-gravity context is proposed, not verified from still.",
    "Ordered cabin versus red colony. Habitat silhouettes are generic; fine pressure connections and hangar geometry need review.",
    "Clear construction subject but ship silhouette resembles canteen freighter. Thumbnail adds many stars and stronger warmth."
]
notes = [s.get("note", notes[i] if i < len(notes) else "") for i, s in enumerate(scenes)]
cards = []
small = []
for i, s in enumerate(scenes):
    folder = ROOT / s["slug"]
    jpg = folder / "thumbnail-v1.jpg"
    if not jpg.exists():
        subprocess.run([ffmpeg, "-v", "error", "-i", str(folder/"thumbnail-v1.png"),
                        "-vf", "scale=1280:720:flags=lanczos", "-frames:v", "1",
                        "-q:v", "2", str(jpg)], check=True)
    assets = {}
    for name in ["concept-v1.png", "thumbnail-v1.png", "thumbnail-v1.jpg",
                 "generation-v1.txt", "thumbnail-prompt-v1.txt"]:
        p = folder/name
        record = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}
        if p.suffix in [".png", ".jpg"]:
            with Image.open(p) as im:
                im.verify()
            with Image.open(p) as im:
                record["dimensions"] = list(im.size)
        assets[name] = record
    assert assets["thumbnail-v1.jpg"]["dimensions"] == [1280, 720]
    assert assets["thumbnail-v1.jpg"]["bytes"] < 2_000_000
    manifest = {"date": "2026-10-27", "title": s["title"], "influence": s["influence"],
                "headline": s["headline"], "catalog_number": None,
                "generator": "built-in image_gen.imagegen",
                "clean_inputs": [], "thumbnail_inputs": ["concept-v1.png",
                "C:/Colony/final/01-ringfall-observatory/thumbnail-v1.png (style only)"],
                "assets": assets, "assistant_inspection": "returned full-composition clean and thumbnail stills",
                "review_note": notes[i], "user_approval": None,
                "thumbnail_is_pixel_preserved": False, "remote_backup_verified": False}
    (folder/"manifest-v1.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8", newline="\n")
    title, headline, note = map(html.escape, [s["title"], s["headline"], notes[i]])
    slug = s["slug"]
    code = slug.split("-")[0].upper()
    cards.append(f'<article id="{code}"><header><span>{code} · {html.escape(s["influence"])}</span><h2>{title}</h2></header>'
                 f'<div class="pair"><figure><a href="{slug}/concept-v1.png"><img loading="lazy" src="{slug}/concept-v1.png" alt="{title} clean artwork"></a><figcaption>Clean scene</figcaption></figure>'
                 f'<figure><a href="{slug}/thumbnail-v1.png"><img loading="lazy" src="{slug}/thumbnail-v1.jpg" alt="{headline} thumbnail"></a><figcaption>Thumbnail · {headline}</figcaption></figure></div>'
                 f'<p class="note">{note}</p><p class="links"><a href="{slug}/generation-v1.txt">Scene prompt</a> · <a href="{slug}/thumbnail-prompt-v1.txt">Thumbnail prompt</a> · <a href="{slug}/manifest-v1.json">Manifest</a></p></article>')
    small.append(f'<a href="#{code}"><img src="{slug}/thumbnail-v1.jpg" alt="{headline}"><span>{code} · {headline}</span></a>')
page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ambient Colony · Brainstorm</title><style>'
page += 'body{margin:0;background:#14181b;color:#e9e6df;font:16px/1.5 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:32px}h1{font-size:clamp(30px,5vw,64px);line-height:1.05;margin:12px 0}a{color:#e5b879}header span,.note,.intro{color:#b3b9bc}article{border-top:1px solid #41474c;padding:28px 0;margin-top:24px}h2{font-size:26px;margin:6px 0 20px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}figure{margin:0}img{width:100%;display:block}figcaption{padding:8px 0;color:#bdc3c5}.note{font-size:14px;max-width:1000px}.links{font-size:13px}.small{display:grid;grid-template-columns:repeat(auto-fit,240px);gap:20px}.small img{width:240px;height:135px;object-fit:cover}.small a{text-decoration:none;font-size:12px}.small span{display:block;margin-top:6px}@media(max-width:800px){.pair{grid-template-columns:1fr}main{padding:20px}}'
page += '</style><main><p>AMBIENT COLONY / CONCEPT REVIEW / 27 OCTOBER 2026</p><h1>Scene and thumbnail studies.</h1><p class="intro">Clean scenes beside generated thumbnail adaptations. All candidates await specific review. No release numbers, video or audio. Click any image for the original. Marketing images can change lighting and geometry; clean plates remain separate.</p><h2>Small-size thumbnail comparison · 240 × 135</h2><div class="small">'
page += "".join(small)+'</div>'+"".join(cards)+'</main></html>'
(ROOT/"gallery.html").write_text(page, encoding="utf-8", newline="\n")
print(f"Verified {len(scenes)} clean PNGs, {len(scenes)} thumbnail PNGs and {len(scenes)} JPEGs; gallery and manifests saved.")
