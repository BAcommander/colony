"""Halve only the rain amplitude; preserve the approved music loop and v1."""
from pathlib import Path
import sys,json,math,hashlib,subprocess,ast
import numpy as np
sys.path.insert(0,'C:/dev/SpeedySlideShow')
from colony import render as R
from colony.sfx import SfxSettings,mix_graph
from dataclasses import asdict
ROOT=Path('G:/AI/colony');REPORT=ROOT/'final/08-rainline-relay/music/long-source-v1'
old=json.loads((REPORT/'one-hour-delivery-v1.json').read_text())
dry=Path(old['files'][0]['path']); expected=old['files'][0]['sha256']
assert hashlib.sha256(dry.read_bytes()).hexdigest()==expected
settings=SfxSettings(**{**old['sfx'],'gain_db':old['sfx']['gain_db']+20*math.log10(.5)})
FF=R.get_ffmpeg_path();SR=48000
preview=REPORT/'Rainline-rain-mix-preview-v2-half-volume.mp3'
wet=ROOT/'exports/08-rainline-relay/Rainline-Relay-1-Hour-with-Rain-v2-half-volume.mp3'
assert not preview.exists() and not wet.exists()
R.preview_audio([str(dry)],str(preview),sfx=settings)
print('New 4:20 preview rendered.',flush=True)
graph=mix_graph(R.build_audio_graph([0],0,first_input=0),settings,3600,1)
subprocess.run([FF,'-n','-v','error','-i',str(dry),'-stream_loop','-1','-i',str(REPORT/'rain-loop-28s-v1.wav'),
 '-filter_complex',graph,'-map','[aout]','-t','3600','-c:a','libmp3lame','-b:a','192k',str(wet)],check=True)
# Reuse the full sample-count / finite / loudness checks without running v1 production.
tree=ast.parse((REPORT/'make_rainline_hour.py').read_text())
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='validate')
import re
exec(compile(ast.Module(body=[node],type_ignores=[]),'<v1 validation>','exec'))
checks=[validate(preview,260),validate(wet,3600)]
assert hashlib.sha256(dry.read_bytes()).hexdigest()==expected
d={**old,'version':2,'sfx':asdict(settings),'files':checks,'music_only_source':str(dry),
 'music_only_sha256':expected,'rain_amplitude_relative_to_v1':.5,
 'user_feedback':'rain too loud at peak; try 50% volume',
 'user_join_approved':True,'join_feedback':'the transition between pieces sounds totally fine',
 'user_rain_mix_approved':False,'approval_scope':'Music transition approved. Rain v2 is a requested quieter candidate; rain balance and full-hour listening remain pending.'}
(REPORT/'rain-mix-delivery-v2.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
p=REPORT.parent/'generation-record.json';r=json.loads(p.read_text(encoding='utf-8'))
r.update(status='Music join approved; half-volume rain v2 delivered for listening review',
 local_join_approved=True,join_feedback=d['join_feedback'],rain_settings=d['sfx'],
 rain_delivery_record='music/long-source-v1/rain-mix-delivery-v2.json',
 current_rain_export=wet.relative_to(ROOT).as_posix(),approval_scope=d['approval_scope'])
p.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
p=REPORT.parent.parent/'manifest.json';m=json.loads(p.read_text(encoding='utf-8'))
m['music_current'].update(status=r['status'],user_join_approved=True,user_rain_mix_approved=False,
 rain_delivery_record=r['rain_delivery_record'],current_rain_export=r['current_rain_export'])
p.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
p=ROOT/'PRODUCTION_PIPELINE.md';s=p.read_text(encoding='utf-8')
s=s.replace('One-hour Above the Flooded Canopy music-only and intermittent-rain versions delivered; full decode passed; join/mix review pending',
 'One-hour music join approved; half-volume rain v2 delivered and fully decoded; rain balance review pending')
s=s.replace('Review music join/rain mix and v5 motion; 4K and final assembly pending','Review quieter rain v2 and v5 motion; 4K and final assembly pending')
p.write_text(s,encoding='utf-8')
p=ROOT/'AGENTS.md';s=p.read_text(encoding='utf-8');start=s.index('Current Rainline music (');end=s.index('\n\n',start)
paragraph=s[start:end]
paragraph=paragraph.replace('Rain -4 dB, starts', 'V1 rain -4 dB; current v2 is -10.0206 dB (exactly half v1 amplitude), starts')
paragraph=paragraph.replace('User requested extension; new join, rain balance and full-hour listening are not approved.',
 'User approved the music transition with "the transition between pieces sounds totally fine". Rain was too loud at peak; requested half-amplitude v2 preview/hour delivered with unchanged music/timing. See rain-mix-delivery-v2.json. Rain v2 balance and full-hour listening remain pending; v1 preserved.')
s=s[:start]+paragraph+s[end:];p.write_text(s,encoding='utf-8')
print(json.dumps(checks,indent=2),flush=True)
