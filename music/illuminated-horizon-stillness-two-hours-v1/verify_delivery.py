"""Full sample validation and exact-recipe lossless comparison of both hours."""
from build_two_hours import *
import re
def validate(path,pieces,compare):
    began=time.time();total=0;maximum=0.0;energy=0.0;error=0.0;all_finite=True
    logpath=H/(path.suffix[1:]+'-decode-loudness.log')
    with logpath.open('wb') as log:
        p=subprocess.Popen(['ffmpeg','-hide_banner','-nostats','-v','info','-i',str(path),'-af','ebur128=peak=true:framelog=verbose','-ar',str(RATE),'-ac','2','-f','f32le','pipe:1'],stdout=subprocess.PIPE,stderr=log)
        for offset,expected in chunks(pieces):
            raw=p.stdout.read(len(expected)*2*4)
            assert len(raw)==len(expected)*2*4,(path.name,offset,len(raw))
            actual=np.frombuffer(raw,dtype='<f4').reshape(-1,2)
            assert np.isfinite(actual).all(),(path,offset)
            maximum=max(maximum,float(np.max(abs(actual))));assert maximum<1,(path,maximum)
            energy+=float(np.sum(actual.astype(float)**2));total+=len(actual)
            if compare:error=max(error,float(np.max(abs(actual-expected))))
            if total//(1800*RATE)!=(total-len(actual))//(1800*RATE):print(f'{path.suffix} verified {total/RATE/60:.0f}/120 minutes',flush=True)
        assert not p.stdout.read(1),'Decoded extra samples'
        assert p.wait()==0 and total==N
    if compare:assert error<=2**-22,('Lossless recipe discrepancy',error)
    text=logpath.read_text(errors='replace');summary=text[text.rfind('Summary:'):]
    integrated=re.search(r'I:\s*([-+\d.]+) LUFS',summary)
    truepeak=re.search(r'Peak:\s*([-+\d.]+) dBFS',summary)
    assert integrated and truepeak,summary
    return {'file':path.name,'bytes':path.stat().st_size,'sha256':digest(path),'decoded_sample_frames':total,'decoded_seconds':total/RATE,'all_samples_finite':True,'no_full_scale_samples':True,'sample_peak_dbfs':20*np.log10(maximum),'rms_dbfs':10*np.log10(energy/(2*total)),'integrated_lufs':float(integrated.group(1)),'true_peak_dbtp':float(truepeak.group(1)),'full_sample_recipe_comparison':{'performed':compare,'maximum_absolute_error':error if compare else None,'tolerance':2**-22 if compare else None,'note':'FLAC quantized to 24-bit; entire two-hour decoded stream compared with approved gain/crossfade recipe and one closing fade.' if compare else 'Lossy MP3: exact count, every decoded sample checked for finite values/peak; no waveform identity claim.'},'validation_seconds':time.time()-began}
def main():
    assert not (H/'delivery-validation.json').exists(),'Preserve previous validation'
    a,b,pieces,tracks,joins=prepare()
    records=[]
    for path,compare in [(FLAC,True),(MP3,False)]:
        records.append(validate(path,pieces,compare))
        save('validation-progress.json',records)
    for row in records:assert row['decoded_seconds']==7200 and row['true_peak_dbtp']<0
    recipe=json.loads((H/'mix-recipe.json').read_text())
    assert digest(ASOURCE)==recipe['sources']['horizon']['sha256'] and digest(BSOURCE)==recipe['sources']['stillness']['sha256']
    save('delivery-validation.json',{'status':'passed','duration_seconds':7200,'sample_frames_per_channel':N,'source_hashes_unchanged':True,'user_approved_transitions':True,'join_count':len(joins),'all_joins_and_repetitions_checked_in_lossless_sample_comparison':True,'outputs':records,'assistant_scope':'Full technical decode/recipe/loudness verification, not listening. User accepted short joins and requested duration; full two-hour listening remains pending.','remote_backup':False})
    print(json.dumps({'status':'passed','files':records},indent=2),flush=True)
if __name__=='__main__':main()
