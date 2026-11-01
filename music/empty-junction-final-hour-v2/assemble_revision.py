"""Use actual Colony with a per-minute wind schedule and the existing opening."""
from revise_audio import H,R,C,E,FF,NEW,save,sha
import sys,json,subprocess,shutil,time
V1=R/'music/empty-junction-final-hour-v1'
sys.path.insert(0,str(V1))
import assemble_with_colony as previous
render=previous.render;IntroSettings=previous.IntroSettings
OUTPUT=E/'The-Empty-Junction-1-Hour-4K-v2.mp4'
ORIGINAL=E/'The-Empty-Junction-1-Hour-4K-v1.mp4'

def probe(path):return json.loads(subprocess.check_output([shutil.which('ffprobe'),'-v','error','-show_streams','-show_format','-of','json',str(path)]))
def prepare_units():
 d=json.loads((V1/'delivery-validation.json').read_text());assert sha(ORIGINAL)==d['sha256']
 records=json.loads((V1/'master-validation.json').read_text());assert records['status']=='passed'
 units={}
 for name in ['wind','quiet']:
  source=V1/'masters'/f'Empty-Junction-v6-{name}-60s-4K.mp4'
  record=next(r for r in records['files'] if r['file']==source.name);assert sha(source)==record['sha256']
  dest=C/f'{name}-60s-4K-bt709.mp4'
  if not dest.exists():subprocess.run([FF,'-v','error','-n','-i',str(source),'-map','0:v:0','-c','copy','-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',str(dest)],check=True)
  units[name]=str(dest)
 branded=C/'existing-Colony-opening-60s.mp4'
 if not branded.exists():subprocess.run([FF,'-v','error','-n','-i',str(ORIGINAL),'-t','60','-map','0:v:0','-c','copy','-movflags','+faststart',str(branded)],check=True)
 units['opening']=str(branded)
 for name,path in units.items():
  v=next(x for x in probe(path)['streams'] if x['codec_type']=='video')
  assert int(v['nb_frames'])==1800 and float(v['duration'])==60
  assert all(v[k]=='bt709' for k in ['color_space','color_transfer','color_primaries'])
 return units

def main():
 assert not OUTPUT.exists()
 validation=json.loads((H/'audio-delivery-validation.json').read_text());assert validation['status']=='passed'
 ar=next(x for x in validation['outputs'] if x['path']==str(NEW));assert sha(NEW)==ar['sha256']
 prior=json.loads((V1/'assembly-settings.json').read_text());assert sha(render.__file__)==prior['renderer_sha256']
 for p,h in prior['intro_verified_files'].items():assert sha(p)==h
 units=prepare_units();recipe=json.loads((H/'mix-recipe.json').read_text());wind=set(recipe['wind_minutes'])
 intro=IntroSettings('The Empty Junction',True);assert json.loads(json.dumps(intro.record()))==prior['opening']
 playlist=[units['opening'] if i==0 else units['wind' if i in wind else 'quiet'] for i in range(60)]
 def existing_opening_and_schedule(ffmpeg,prep,entries,settings,report):
  assert settings.record()==intro.record() and len(entries)>=60 and prep.loop_duration==60
  report.stage('Reusing approved opening and wind/quiet pictures',.20,.35);report.tick(1)
  return playlist
 # Job-local playlist adapter only. The actual Colony mux, audio envelope and
 # complete-file verifier run unchanged. No installed app file is edited.
 render.opening_entries=existing_opening_and_schedule
 info=render.probe_video(FF,units['wind'])
 render._prepared=render.Prepared(str(C),render._file_key(units['wind']),info,render.color_tags_for(info),units['wind'],60.,info)
 save('assembly-settings.json',{'tool':'Actual Colony renderer with job-local scheduled-minute playlist adapter','renderer':render.__file__,'renderer_sha256':sha(render.__file__),'original_video':str(ORIGINAL),'original_video_sha256':sha(ORIGINAL),'units':{k:{'path':p,'sha256':sha(p)} for k,p in units.items()},'minute_sequence':['opening' if i==0 else 'wind' if i in wind else 'quiet' for i in range(60)],'wind_minutes':sorted(wind),'audio':ar,'opening':intro.record(),'pictures_reencoded':False,'audio_gain_db':0,'match_loudness':False,'new_sfx_layer_added_during_video_export':False,'output':str(OUTPUT),'metadata':'BT.709 VUI tags completed on stream-copied units before assembly'})
 state=['',0]
 def status(message):
  state[0]=message;print(message,flush=True);save('progress.json',{'stage':message})
 def progress(fraction,eta):
  now=time.monotonic()
  if now-state[1]>25:
   record={'stage':state[0],'total_progress_percent':round(fraction*100,1),'eta_seconds':eta};save('progress.json',record);print(record,flush=True);state[1]=now
 result=render.render(units['wind'],[str(NEW)],str(OUTPUT),crossfade=0,overlay_mode=render.OVERLAY_OFF,match_loudness=False,full_decode=True,overwrite=False,intro=intro,on_status=status,on_progress=progress)
 assert result.output==str(OUTPUT) and result.verified and all(x.ok for x in result.checks)
 assert result.duration==3600 and result.gains_db==[0]
 shutil.copy2(result.manifest,H/'colony-export.json')
 save('assembly-result.json',{'status':'passed','output':str(OUTPUT),'duration':result.duration,'dimensions':[result.width,result.height],'fps':result.fps,'all_video_audio_decoded':True,'checks':[vars(x) for x in result.checks]})
 print('Revised full-hour export and complete decode passed',flush=True)
if __name__=='__main__':main()
