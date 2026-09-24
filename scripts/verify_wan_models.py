"""Verify local model size and SHA256 against the official HF repository metadata."""
import hashlib
import json
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parents[1]
records = []
for folder in ('diffusion_models', 'text_encoders', 'vae'):
    url = 'https://huggingface.co/api/models/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/tree/main/split_files/' + folder
    with urllib.request.urlopen(url) as response:
        entries = json.load(response)
    for path in (root / '.local/ComfyUI/models' / folder).glob('*.safetensors'):
        remote = next(x for x in entries if x['path'].endswith('/' + path.name))
        digest = hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()
        expected = remote.get('lfs', {}).get('oid')
        valid = path.stat().st_size == remote['size'] and digest == expected
        record = {'file': path.name, 'bytes': path.stat().st_size, 'sha256': digest,
                  'expected_sha256': expected, 'verified': valid}
        records.append(record)
        print(json.dumps(record), flush=True)
        if not valid:
            raise RuntimeError('Model verification failed')
(root / 'creative/ringfall/animation/wan-tests/model-manifest.json').write_text(
    json.dumps(records, indent=2), encoding='utf8')
