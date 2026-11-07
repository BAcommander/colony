"""Check restored inputs; optionally rebuild into new outputs without touching accepted files."""
from pathlib import Path
import argparse, datetime, hashlib, importlib, json, shutil, sys, uuid
import numpy, scipy
import build_mix as mix
P=Path(__file__).resolve().parent
R=P.parents[1]
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build',action='store_true',help='Render a new full hour and listening reviews; allow at least 10 GB free')
    ap.add_argument('--scene-review',action='store_true',help='Also rebuild the two-minute scene check after the hour')
    a=ap.parse_args()
    manifest=json.loads((P/'source-manifest.json').read_text(encoding='utf-8'))
    for item in manifest['sources']:
        src=P/'sources'/Path(item['preserved_path'].replace('\\','/')).name
        assert src.is_file() and sha(src)==item['sha256'],str(src)
        item['preserved_path']=str(src)
    wind=R/'music/sfx-library/assets/wind-soft-exterior-01.mp3'
    assert sha(wind)=='324470a6fa73b57ef021edca2ddd6f4c20a6319bd0148bc2ea0f4f71c8d19a34'
    assert mix.FF,'ffmpeg must be on PATH'
    runtime=json.loads((P/'runtime-snapshot.json').read_text(encoding='utf-8'))
    env={'numpy':numpy.__version__,'scipy':scipy.__version__,'python':sys.version.split()[0],
         'ffmpeg_sha256':sha(Path(mix.FF))}
    same=(env['numpy']==runtime['numpy'] and env['scipy']==runtime['scipy'] and env['python']=='3.12.10' and env['ffmpeg_sha256']==runtime['tools']['ffmpeg']['sha256'])
    if a.scene_review:
        video=R/'music/crater-rim-animation-v5/Crater-Rim-Survey-v5-60s-loop.mp4'
        assert sha(video)=='63553fc01d87c8e629d3f8268b511255877e14d155b2f0deb10481fe2a497be1'
    print(json.dumps({'source_preflight':'passed','recorded_runtime_matches':same,'environment':env,'will_render':a.build}),flush=True)
    if not a.build:return
    assert same,'Use the recorded Python/dependency/FFmpeg versions for a faithful restoration'
    assert shutil.disk_usage(R).free>10*1024**3,'Allow at least 10 GB free for the independent reconstruction'
    run_id=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    run=R/'.local/crater-rim-audio-rebuilds'/run_id
    mix.H=run/'records';mix.H.mkdir(parents=True,exist_ok=False)
    (mix.H/'review').mkdir()
    mix.C=run/'cache'
    mix.E=R/'exports/14-crater-rim-survey'/('audio-restored-'+run_id)
    mix.save(mix.H/'source-manifest.json',manifest)
    mix.main()
    if a.scene_review:
        review=importlib.import_module('make_scene_review');review.main()
    original=json.loads((P/'delivery-validation.json').read_text(encoding='utf-8'))
    expected={Path(x['file'].replace('\\','/')).name:x['sha256'] for x in original['outputs']}
    actual=json.loads((mix.H/'delivery-validation.json').read_text(encoding='utf-8'))
    checks=[{'file':x['file'],'matches_accepted_sha256':x['sha256']==expected[Path(x['file']).name]} for x in actual['outputs']]
    report={'status':'passed' if all(x['matches_accepted_sha256'] for x in checks) else 'hash_difference_review_required',
            'records':str(mix.H),'exports':str(mix.E),'accepted_files_unchanged':True,'outputs':checks}
    mix.save(mix.H/'restoration-result.json',report)
    print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
