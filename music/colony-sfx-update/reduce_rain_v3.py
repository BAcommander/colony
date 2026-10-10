"""User requested another 10–15% rain reduction: use midpoint 12.5%."""
from pathlib import Path
import sys,json,math,hashlib,subprocess,ast,re
import numpy as np
sys.path.insert(0,'C:/dev/SpeedySlideShow')
from colony import render as R
from colony.sfx import SfxSettings,mix_graph
from dataclasses import asdict
ROOT=Path('G:/AI/colony');REPORT=ROOT/'final/08-rainline-relay/music/long-source-v1'
old=json.loads((REPORT/'rain-mix-delivery-v2.json').read_text())
dry=Path(old['music_only_source']);expected=old['music_only_sha256']
assert hashlib.sha256(dry.read_bytes()).hexdigest()==expected
settings=SfxSettings(**{**old['sfx'],'gain_db':old['sfx']['gain_db']+20*math.log10(.875)})
FF=R.get_ffmpeg_path();SR=48000
preview=REPORT/'Rainline-rain-mix-preview-v3.mp3'
wet=ROOT/'exports/08-rainline-relay/Rainline-Relay-1-Hour-with-Rain-v3.mp3'
assert not preview.exists() and not wet.exists()
R.preview_audio([str(dry)],str(preview),sfx=settings)
print('Quieter v3 preview rendered.',flush=True)
graph=mix_graph(R.build_audio_graph([0],0,first_input=0),settings,3600,1)
subprocess.run([FF,'-n','-v','error','-i',str(dry),'-stream_loop','-1','-i',str(REPORT/'rain-loop-28s-v1.wav'),
 '-filter_complex',graph,'-map','[aout]','-t','3600','-c:a','libmp3lame','-b:a','192k',str(wet)],check=True)
tree=ast.parse((REPORT/'make_rainline_hour.py').read_text())
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='validate')
exec(compile(ast.Module(body=[node],type_ignores=[]),'<v1 validation>','exec'))
checks=[validate(preview,260),validate(wet,3600)]
assert hashlib.sha256(dry.read_bytes()).hexdigest()==expected
d={**old,'version':3,'sfx':asdict(settings),'files':checks,
 'rain_amplitude_relative_to_v1':.4375,'rain_amplitude_relative_to_v2':.875,
 'user_feedback':'yeah that sounds better, can we take the maximum rain down 10-15% more? then record the finidings for future videos etc',
 'v2_feedback':'sounds better; reduce maximum another 10–15%',
 'user_rain_mix_approved':False,
 'approval_scope':'Music transition approved; v2 quieter rain received positive feedback. V3 implements the requested further reduction at the 12.5% midpoint; no separate v3 listening verdict or full-hour approval inferred.'}
(REPORT/'rain-mix-delivery-v3.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print(json.dumps(checks,indent=2),flush=True)
