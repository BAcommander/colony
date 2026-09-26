from pathlib import Path
import subprocess,json,numpy as np
R=Path(__file__).resolve().parent/'test-01';R.mkdir(exist_ok=True)
FF=r'C:\Program Files\ShareX\ffmpeg.exe'
files={
'Basalt Transmission Outpost':r'C:\Users\jazzs\Downloads\Basalt_Transmission_Outpost_2026-09-26T152953.mp3',
'Copper Dusk Transmission':r'C:\Users\jazzs\Downloads\Copper_Dusk_Transmission_2026-09-26T152953.mp3',
'Reference':r'C:\Users\jazzs\Downloads\YTDown.com_YouTube_Media_G0-ZTBd6jyI_THE-GREAT-PYRAMID-OUTPOST-Dark-Ambient-Music-at-the-Edge-of-Civilization_009_128k.mp3'}
result={}
for name,path in files.items():
    args=[FF,'-v','error']
    if name=='Reference':args+=['-ss','60']
    args+=['-i',path,'-t','60','-ar','22050','-ac','2','-f','f32le','pipe:1']
    p=subprocess.run(args,capture_output=True,check=True)
    a=np.frombuffer(p.stdout,np.float32).reshape(-1,2).astype(float)
    # Compare the interior, excluding 10 seconds at either edge of each excerpt.
    b=a[220500:-220500]; n=16384; freq=np.fft.rfftfreq(n,1/22050); powers=[]
    for j in range(0,len(b)-n,n//2):
        powers.append((abs(np.fft.rfft(b[j:j+n]*np.hanning(n)[:,None],axis=0))**2).mean(axis=1))
    powers=np.array(powers); power=powers.mean(0)
    rms=np.array([np.mean(b[j:j+22050]**2) for j in range(0,len(b)-22050,22050)])
    db=10*np.log10(rms+1e-20)
    edges=np.geomspace(30,8000,49)
    feat=np.array([powers[:,(freq>=lo)&(freq<hi)].sum(1) for lo,hi in zip(edges[:-1],edges[1:])]).T
    feat=feat/(feat.sum(1,keepdims=True)+1e-20)
    result[name]={'decoded_seconds':len(a)/22050,'stereo_energy_percent':{f'{lo}-{hi} Hz':round(float(100*power[(freq>=lo)&(freq<hi)].sum()/power.sum()),2) for lo,hi in [(0,80),(80,250),(250,1000),(1000,4000),(4000,11025)]},'rms_dbfs_p10_median_p90':np.round(np.percentile(db,[10,50,90]),2).tolist(),'stereo_correlation':round(float(np.corrcoef(b.T)[0,1]),3),'energy_centroid_hz':round(float(np.sum(freq*power)/power.sum()),1),'spectral_change_10seconds_L1':round(float(np.mean(np.sum(abs(feat[27:]-feat[:-27]),axis=1))),3)}
    q=subprocess.run([FF,'-hide_banner','-i',path,'-t','60','-af','ebur128=peak=true:framelog=verbose','-f','null','-'],capture_output=True)
    (R/(name.replace(' ','-')+'-test-loudness.txt')).write_bytes(q.stderr)
(R/'test-comparison.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
