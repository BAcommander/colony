from pathlib import Path
import subprocess,json,numpy as np
R=Path(__file__).resolve().parent/'long-test';R.mkdir(exist_ok=True)
FF=r'C:\Program Files\ShareX\ffmpeg.exe'
SRC=r'C:\Users\jazzs\Downloads\Lunar_Observatory_Night_Watch_2026-09-25T230455.mp4'
p=subprocess.run([FF,'-v','error','-i',SRC,'-vn','-ar','8192','-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True)
a=np.frombuffer(p.stdout,np.float32).reshape(-1,2);n=len(a)//8192
b=a[:n*8192].reshape(n,8192,2)
level=10*np.log10(np.mean(b.astype(float)**2,axis=(1,2))+1e-20)
P=(abs(np.fft.rfft(b*np.hanning(8192)[None,:,None],axis=1))**2).mean(axis=2)
freq=np.fft.rfftfreq(8192,1/8192); edges=np.geomspace(30,4000,33)
F=np.array([P[:,(freq>=lo)&(freq<hi)].sum(1) for lo,hi in zip(edges[:-1],edges[1:])]).T
F=F/(F.sum(axis=1,keepdims=True)+1e-20)
scores=[];d=15
for start in range(5,36):
 for end in range(n-40,n-3):
  x=F[start:start+d].mean(0);y=F[end-d:end].mean(0)
  gap=abs(level[start:start+d].mean()-level[end-d:end].mean())
  if min(level[start:start+d].min(),level[end-d:end].min())<np.median(level)-9:continue
  score=float(np.sum(abs(x-y)))+gap*.1+(start+n-end)*.001
  scores.append((score,start,end,gap))
score,start,end,gap=min(scores)
report={'audio_seconds':len(a)/8192,'rms_first_35_seconds':np.round(level[:35],1).tolist(),'rms_last_40_seconds':np.round(level[-40:],1).tolist(),'rms_p10_median_p90':np.round(np.percentile(level,[10,50,90]),2).tolist(),'candidate_start_seconds':start,'candidate_end_seconds':end,'crossfade_seconds':d,'overlap_level_difference_db':round(float(gap),2),'selection_note':'Spectral and level similarity only; listening approval required. Equal-power crossfade is a starting candidate.'}
(R/'loop-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
filters=f'[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,asplit=3[a][b][c];[a][b]acrossfade=d={d}:c1=qsin:c2=qsin[ab];[ab][c]acrossfade=d={d}:c1=qsin:c2=qsin,volume=0.7[out]'
out=R/'Night-Watch-three-cycle-preview.mp3'
subprocess.run([FF,'-y','-v','error','-i',SRC,'-filter_complex',filters,'-map','[out]','-c:a','libmp3lame','-b:a','192k',str(out)],check=True)
firstjoin=end-start-d
subprocess.run([FF,'-y','-v','error','-ss',str(firstjoin-30),'-i',str(out),'-t','75','-c:a','libmp3lame','-b:a','192k',str(R/'Night-Watch-join-check-75s.mp3')],check=True)
print('Preview complete. First overlap begins at',firstjoin,'seconds; second at',2*firstjoin,flush=True)
