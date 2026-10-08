"""Check the authoritative scene plan and the frozen local dependencies."""
from pathlib import Path
import json, hashlib
from PIL import Image
H=Path(__file__).resolve().parent
R=H.parents[1]
def main():
    c=json.loads((H/'scene-plan-v1.json').read_text())
    source=R/c['source']['path']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==c['source']['sha256']
    assert list(Image.open(source).size)==c['source']['dimensions']
    for name in ['ambient_effects.py','dust_transport.py','periodic_transport.py']:
        assert (H/'dependencies'/name).is_file()
    assert c['duration']==60 and c['fps']==30
    print('Source, dimensions, timing and frozen dependencies verified')
if __name__=='__main__': main()
