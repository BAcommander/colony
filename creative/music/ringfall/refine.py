from pathlib import Path
import subprocess,json,numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
FF=r'C:\Program Files\ShareX\ffmpeg.exe'
SRC=r'C:\Users\jazzs\Downloads\YTDown.com_YouTube_Media_KO0k7at4qCs_DEAD-WATER-Deep-Ambient-Music-Underground-Waterfall-Ambience_009_128k.mp3'
def audio(t,d,sr=8192):
    p=subprocess.run([FF,'-v','error','-ss',str(t),'-i',SRC,'-t',str(d),'-ar',str(sr),'-ac','1','-f','f32le','pipe:1'],capture_output=True,check=True)
    return np.frombuffer(p.stdout,np.float32)
results=[]
for lag in [686,3564,7128,10692]:
    for start in [60,300,900,1800,3000]:
        a=audio(start,20); b=audio(start+lag-2,24)
        n=2**int(np.ceil(np.log2(len(a)+len(b))))
        cc=np.fft.irfft(np.fft.rfft(b,n)*np.fft.rfft(a,n).conj(),n)[:len(b)-len(a)+1]
        energy=np.r_[0,np.cumsum(b.astype(float)**2)]
        norm=cc/np.sqrt(np.sum(a.astype(float)**2)*(energy[len(a):]-energy[:-len(a)])+1e-30)
        ix=np.argmax(norm); results.append({'start':start,'lag':lag-2+int(ix)/8192,'correlation':float(norm[ix])})
print(json.dumps(results,indent=2),flush=True)
(R/'waveform-matches.json').write_text(json.dumps(results,indent=2))
data=np.load(R/'features.npz'); F=data['features']; L=data['levels']
im=Image.new('RGB',(1600,760),'#101825'); draw=ImageDraw.Draw(im)
draw.text((40,15),'DEAD WATER: measured level across four hours (one-second RMS, dBFS)',fill='white')
for db in [-5,-10,-15,-20,-25]:
    yy=70+(-5-db)*10; draw.line((60,yy,1550,yy),fill='#344050'); draw.text((20,yy-5),str(db),fill='white')
lv=10*np.log10(L[:,0]+1e-15)
for i in range(1490):
    v=lv[int(i*len(lv)/1490):int((i+1)*len(lv)/1490)];
    draw.line((60+i,70+(-5-v.max())*10,60+i,min(350,70+(-5-v.min())*10)),fill='#f6b759')
for m in range(0,241,30):
    x=60+m/240*1490;draw.text((x-12,360),str(m)+'m',fill='white')
draw.text((40,400),'First hour: spectral energy, 20 Hz (bottom) to 4 kHz (top); brighter = more energy',fill='white')
z=10*np.log10(F[:3600]+1e-15); z=(np.clip((z+15)/55,0,1)*255).astype('uint8')
rgb=np.stack([z,(z.astype(float)*.65).astype('uint8'),255-z],axis=-1)
spec=Image.fromarray(rgb[::-1].transpose(1,0,2)[::-1]).resize((1490,260))
# time runs left to right, low frequencies at bottom
spec=Image.fromarray(rgb.transpose(1,0,2)[::-1]).resize((1490,260))
im.paste(spec,(60,430))
for m in range(0,61,5):draw.text((60+m/60*1490-10,700),str(m)+'m',fill='white')
im.save(R/'analysis-overview.png')
# High-resolution spectral peaks at representative moments; source identity cannot be inferred.
peaks=[]
for t in [60,180,360,600,900]:
    a=audio(t,16,22050); n=65536; spectra=[]
    for j in range(0,len(a)-n,n//2): spectra.append(abs(np.fft.rfft(a[j:j+n]*np.hanning(n)))**2)
    power=np.mean(spectra,0); freq=np.fft.rfftfreq(n,1/22050)
    ix=np.where((power[1:-1]>power[:-2])&(power[1:-1]>power[2:]))[0]+1
    ix=sorted([i for i in ix if 35<freq[i]<2000],key=lambda i:power[i],reverse=True)[:12]
    peaks.append({'time':t,'peaks_hz':[round(float(freq[i]),2) for i in ix], 'energy_by_band':{f'{lo}-{hi}':round(float(power[(freq>=lo)&(freq<hi)].sum()/power.sum()),4) for lo,hi in [(0,80),(80,250),(250,1000),(1000,4000),(4000,11025)]}})
(R/'spectral-peaks.json').write_text(json.dumps(peaks,indent=2)); print(json.dumps(peaks,indent=2))
