"""Preserve supplied Deepwell samples and make fixed-gain listening copies."""
from pathlib import Path
import hashlib,json,subprocess,shutil,math
import numpy as np
H=Path(__file__).resolve().parent;S=H/'sources';V=H/'review';C=H/'cache'
for p in [S,V,C]:p.mkdir(exist_ok=True)
FF=shutil.which('ffmpeg');PROBE=shutil.which('ffprobe');SR=48000
FILES=['Waterworks_Gallery_2026-11-01T171541.mp4','Sheltered_Replenishment_2026-11-01T171541.mp4']
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def save(n,d):(H/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def decode(p):
 b=subprocess.check_output([FF,'-v','error','-i',str(p),'-map','0:a:0','-ac','2','-ar',str(SR),'-f','f32le','pipe:1'])
 return np.frombuffer(b,'<f4').reshape(-1,2)
def measure(p,label):
 result=subprocess.run([FF,'-hide_banner','-nostats','-i',str(p),'-map','0:a:0','-af','loudnorm=I=-23:TP=-2:LRA=11:print_format=json','-f','null','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
 log=result.stderr.decode(errors='replace');(C/(label+'-measurement.log')).write_text(log)
 data=json.loads(log[log.rfind('{'):log.rfind('}')+1])
 return {k:float(data['input_'+k]) for k in ['i','tp','lra','thresh']}
def rmsdb(x):return float(20*np.log10(max(float(np.sqrt(np.mean(x.astype(float)**2))),1e-12)))
def main():
 originals=[]
 for name in FILES:
  src=Path('C:/Users/jazzs/Downloads')/name;dst=S/name;digest=sha(src)
  if not dst.exists():shutil.copy2(src,dst)
  assert sha(dst)==digest
  originals.append((src,dst,digest))
 records=[]
 for i,(src,dst,digest) in enumerate(originals):
  label='A-Waterworks-Gallery' if i==0 else 'B-Sheltered-Replenishment'
  print('Checking',label,flush=True)
  probe=json.loads(subprocess.check_output([PROBE,'-v','error','-show_streams','-show_format','-of','json',str(dst)]))
  stream=next(s for s in probe['streams'] if s['codec_type']=='audio')
  x=decode(dst);seconds=len(x)/SR;assert np.isfinite(x).all()
  measurement=measure(dst,label);gain=round(-23-measurement['i'],2)
  assert measurement['tp']+gain<-2,'Fixed gain would exceed audition headroom'
  level=[rmsdb(x[n*SR:min(len(x),(n+1)*SR)]) for n in range(math.ceil(seconds))]
  out=V/(label+'-4min-level-matched.mp3')
  if not out.exists():
   subprocess.run([FF,'-v','error','-n','-i',str(dst),'-map','0:a:0','-vn','-af',f'volume={gain:.2f}dB','-ar',str(SR),'-ac','2','-c:a','libmp3lame','-b:a','192k',str(out)],check=True)
  y=decode(out);assert y.shape==x.shape and np.isfinite(y).all() and abs(y).max()<1
  expected=x.astype(float)*10**(gain/20);err=expected-y;snr=float(10*np.log10(np.sum(expected**2)/np.sum(err**2)))
  assert snr>20
  audition=measure(out,label+'-review');assert abs(audition['i']+23)<.5
  middle=rmsdb(x[30*SR:-30*SR]);first=rmsdb(x[:5*SR]);last=rmsdb(x[-5*SR:])
  record={'id':'A' if i==0 else 'B','title':'Waterworks Gallery' if i==0 else 'Sheltered Replenishment','original_path':str(src),'source_copy':str(dst),'source_sha256':digest,'source_bytes':dst.stat().st_size,'decoded_seconds':seconds,'decoded_frames_per_channel':len(x),'source_sample_rate':int(stream['sample_rate']),'source_channels':stream['channels'],'source_measurements':{'integrated_lufs':measurement['i'],'true_peak_dbtp':measurement['tp'],'lra_lu':measurement['lra']},'audition':{'path':str(out),'sha256':sha(out),'fixed_gain_db':gain,'target_lufs':-23,'measured_lufs':audition['i'],'true_peak_dbtp':audition['tp'],'whole_file_recipe_snr_db':snr,'all_samples_finite_unclipped':True,'duration_unchanged':True},'edge_measurements':{'first_5s_rms_dbfs':first,'middle_rms_dbfs':middle,'last_5s_rms_dbfs':last,'first_5s_relative_to_middle_db':first-middle,'last_5s_relative_to_middle_db':last-middle},'one_second_rms_dbfs':level,'probe':probe}
  records.append(record);print(label,seconds,'s;',measurement['i'],'LUFS;',gain,'dB audition gain;',round(snr,1),'dB SNR',flush=True)
  assert sha(src)==sha(dst)==digest
 save('sample-intake.json',{'date':'2026-11-01','user_message':'heres two 4 minute samples','status':'Two supplied samples preserved, fully decoded, measured and fixed-gain audition copies verified','actual_supplied_durations_seconds':[r['decoded_seconds'] for r in records],'earlier_proposal_seconds':120,'earlier_proposal_is_not_actual_duration':True,'sources':records,'audition_processing':'Fixed gain only to approximately -23 LUFS; MP3 192k. No limiting, compression, EQ, SFX, stretching, added fades, cuts or joins. The loudnorm filter is measurement-only; its processed output is discarded.','selection':None,'user_audio_approval':False,'assistant_listening':False,'generation_prompt_and_settings':'User-supplied exports; exact model, prompt, reference and cost not verified. Prepared pilot prompt is provenance for the proposal, not proof of actual generation settings.','paid_generation_by_assistant':False})
 print('PASS: both originals preserved, complete durations and matched-level auditions verified',flush=True)
if __name__=='__main__':main()
