"""Reproducible local Wan2.2 benchmark. Start ComfyUI before running this script."""
import argparse
import json
import shutil
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'creative/ringfall/animation/wan-tests'
POSITIVE = (
    'Locked-off cinematic shot of a warm lunar observatory overlooking a ringed gas giant. '
    'Clearly visible broad cloud bands flow and curl across the gas giant atmosphere, '
    'while the planet silhouette and elegant rings remain stable. Two warm searchlights '
    'slowly sweep the ground around the distant colony, revealing the rocky terrain. '
    'A generous plume of translucent steam rises continuously from the coffee mug, '
    'curling into soft eddies and dispersing above the desk. The laptop radar scan turns steadily. '
    'Rich natural motion at several depths, quiet and unhurried, photorealistic materials, '
    'warm practical interior lighting, stable exposure. Camera and furniture remain still.'
)
NEGATIVE = (
    'camera movement, zoom, pan, shake, cuts, static video, frozen motion, timelapse, '
    'flicker, exposure changes, melting furniture, warped window, changing architecture, '
    'distorted planetary rings, extra mug handles, people, text overlays, watermark, '
    'smoke filling room, dust outside, oversaturation, cartoon'
)

def request(path, data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request('http://127.0.0.1:8188' + path, data=body,
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)

def graph(args):
    def node(kind, **inputs):
        return {'class_type': kind, 'inputs': inputs}
    return {
        '1': node('UNETLoader', unet_name='wan2.2_ti2v_5B_fp16.safetensors', weight_dtype='default'),
        '2': node('CLIPLoader', clip_name='umt5_xxl_fp8_e4m3fn_scaled.safetensors', type='wan', device='cpu'),
        '3': node('VAELoader', vae_name='wan2.2_vae.safetensors'),
        '4': node('CLIPTextEncode', clip=['2', 0], text=Path(args.positive_file).read_text(encoding='utf8') if args.positive_file else POSITIVE),
        '5': node('CLIPTextEncode', clip=['2', 0], text=Path(args.negative_file).read_text(encoding='utf8') if args.negative_file else NEGATIVE + ', searchlight beams, spotlight cones, light shafts, giant smoke plume'),
        '6': node('LoadImage', image=args.name + '-reference.png'),
        '7': node('Wan22ImageToVideoLatent', vae=['3', 0], width=args.width, height=args.height,
                  length=args.frames, batch_size=1, start_image=['6', 0]),
        '8': node('ModelSamplingSD3', model=['1', 0], shift=8.0),
        '9': node('KSampler', model=['8', 0], positive=['4', 0], negative=['5', 0],
                  latent_image=['7', 0], seed=args.seed, steps=args.steps, cfg=5.0,
                  sampler_name='uni_pc', scheduler='simple', denoise=1.0),
        '10': node('VAEDecodeTiled', samples=['9', 0], vae=['3', 0], tile_size=256,
                   overlap=64, temporal_size=16, temporal_overlap=4),
        '11': node('CreateVideo', images=['10', 0], fps=24.0),
        '12': node('SaveVideo', video=['11', 0], filename_prefix=args.name,
                   format='mp4', codec={'codec': 'h264'}),
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--name', default='ringfall-wan-test01')
    p.add_argument('--width', type=int, default=640)
    p.add_argument('--height', type=int, default=352)
    p.add_argument('--frames', type=int, default=49)
    p.add_argument('--steps', type=int, default=20)
    p.add_argument('--seed', type=int, default=24092026)
    p.add_argument('--positive-file')
    p.add_argument('--negative-file')
    p.add_argument('--input', default='creative/ringfall/04-laptop-refined.png')
    p.add_argument('--prepare-only', action='store_true')
    args = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / args.input,
                 ROOT / '.local/ComfyUI/input' / (args.name + '-reference.png'))
    workflow = graph(args)
    (OUT / f'{args.name}-api.json').write_text(json.dumps(workflow, indent=2), encoding='utf8')
    if args.prepare_only:
        return
    start = time.time()
    queued = request('/prompt', {'prompt': workflow, 'client_id': 'colony-local'})
    print(json.dumps(queued), flush=True)
    prompt_id = queued['prompt_id']
    (OUT / f'{args.name}-queue.json').write_text(json.dumps(queued, indent=2), encoding='utf8')
    while True:
        history = request('/history/' + prompt_id)
        if prompt_id in history:
            result = history[prompt_id]
            result['wall_seconds'] = time.time() - start
            (OUT / f'{args.name}-result.json').write_text(json.dumps(result, indent=2), encoding='utf8')
            print(json.dumps({'status': result['status'], 'wall_seconds': result['wall_seconds'],
                              'outputs': result.get('outputs')}), flush=True)
            if result['status']['status_str'] != 'success':
                raise RuntimeError('Generation failed; inspect result JSON and server log')
            return
        print(f'Waiting for local generation: {time.time() - start:.0f}s', flush=True)
        time.sleep(20)

if __name__ == '__main__':
    main()
