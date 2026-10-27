"""Build a combined local comparison gallery without duplicating original artwork."""
import hashlib
import html
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
from html.parser import HTMLParser
import os

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
collections = [REPO/"creative/concepts/four-worlds-2026-10-27",
               ROOT/"2026-10-27-three-worlds",
               ROOT/"2026-10-27-retro-worlds"]
small, cards, inventory = [], [], []
for collection in collections:
    scenes = json.loads((collection/"generation-index.json").read_text(encoding="utf-8"))
    for s in scenes:
        folder = collection/s["slug"]
        manifest = json.loads((folder/"manifest-v1.json").read_text(encoding="utf-8"))
        for filename, record in manifest["assets"].items():
            p = folder/filename
            assert hashlib.sha256(p.read_bytes()).hexdigest() == record["sha256"], p
        relative = Path(os.path.relpath(folder, ROOT)).as_posix()
        code = s["slug"].split("-")[0].upper()
        title, influence, headline = map(html.escape, [s["title"], s["influence"], s["headline"]])
        note = html.escape(manifest["review_note"])
        small.append(f'<a href="#{code}"><img loading="lazy" src="{relative}/thumbnail-v1.jpg" alt="{headline}"><span>{code} · {headline}</span></a>')
        cards.append(f'<article id="{code}"><p>{code} / {influence}</p><h2>{title}</h2>'
                     f'<div class="pair"><figure><a href="{relative}/concept-v1.png"><img loading="lazy" src="{relative}/concept-v1.png" alt="{title}"></a><figcaption>Clean scene</figcaption></figure>'
                     f'<figure><a href="{relative}/thumbnail-v1.png"><img loading="lazy" src="{relative}/thumbnail-v1.jpg" alt="{headline}"></a><figcaption>{headline}</figcaption></figure></div>'
                     f'<p class="note">{note}</p><p><a href="{relative}/generation-v1.txt">Scene prompt</a> · <a href="{relative}/thumbnail-prompt-v1.txt">Thumbnail prompt</a> · <a href="{relative}/manifest-v1.json">Manifest</a></p></article>')
        inventory.append({"review_id": code, "title": s["title"], "folder": relative,
                          "source_influence": s["influence"], "headline": s["headline"],
                          "status": "candidate; individual user verdict pending"})
page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ambient Colony · 30 brainstorms</title><style>'
page += 'body{margin:0;background:#12171b;color:#eee8dc;font:16px/1.5 system-ui}main{max-width:1540px;padding:32px;margin:auto}h1{font-size:clamp(32px,5vw,64px);line-height:1.1}a{color:#e3b579}article{border-top:1px solid #40484e;margin-top:28px;padding-top:24px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0}img{width:100%;display:block}figcaption{padding:8px 0}.note,.intro{color:#b3bfc4}.small{display:grid;grid-template-columns:repeat(auto-fit,240px);gap:20px}.small a{font-size:12px;text-decoration:none}.small img{width:240px;height:135px}.small span{display:block;margin-top:6px}@media(max-width:800px){.pair{grid-template-columns:1fr}main{padding:18px}}'
page += '</style><main><p>AMBIENT COLONY / BRAINSTORM / 27 OCTOBER 2026</p><h1>Ten influences. Thirty places.</h1><p class="intro">Clean scenes and thumbnail adaptations. A1–J3 are review IDs, not release numbers. Click to enlarge. Individual selection and geometry review remain pending. First twelve received positive set-level feedback; later pairs await specific review.</p><p><a href="README.md">Details, research history and learnings</a></p><h2>Thumbnail-size comparison</h2><div class="small">'
page += "".join(small)+'</div>'+"".join(cards)+'</main></html>'
(ROOT/"gallery.html").write_text(page, encoding="utf-8", newline="\n")
(ROOT/"catalog.json").write_text(json.dumps(inventory, indent=2)+"\n", encoding="utf-8", newline="\n")
class LinkCheck(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key not in ("src", "href") or not value or value.startswith("#"):
                continue
            parts = urlsplit(value)
            if parts.scheme:
                continue
            target = ROOT/unquote(parts.path)
            assert target.exists(), target
LinkCheck().feed(page)
print(f"Verified hashes and gallery targets for {len(inventory)} pairs. Combined gallery saved.")
