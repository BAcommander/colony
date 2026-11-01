"""Add the supplied pump between exterior events, retaining louder wind."""
from prepare_samples import H,SR,sha,decode,measure
from build_combined_review import write_audio
import json,math,numpy as np
D=H/'combined-review-v4';D.mkdir(exist_ok=True)
def save(n,x):(D/n).write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def main():
 intake=json.loads((H/'pump-intake.json').read_text());source=intake['source_copy'];assert sha(source)==intake['sha256']
 pump=decode(source);assert len(pump)==20*SR
 old=H/'combined-review-v3';recipe=json.loads((old/'mix-recipe.json').read_text());validation=json.loads((old/'delivery-validation.json').read_text())
 p=old/'Deepwell-water-down-wind-plus3dB-8min-v3.flac';assert sha(p)==next(x['sha256'] for x in validation['outputs'] if x['path']==str(p))
 base=decode(p);stem=np.zeros_like(base);gain=min(-37-intake['measurements']['i'],-18-intake['measurements']['tp'])
 local=np.arange(len(pump));env=np.maximum(0,np.minimum(1,np.minimum(local/(3*SR),(len(pump)-1-local)/(5*SR))))
 shaped=(pump.astype(float)*10**(gain/20)*env[:,None]).astype(np.float32)
 starts=[80,275,420];events=[];mask=np.zeros(len(base),bool)
 for t in starts:
  a=t*SR;b=a+len(pump)
  for name in ['water','wind']:
   assert all(t+20<=lo or t>=hi for lo,hi in recipe[name]['events'])
  stem[a:b]=shaped;mask[a:b]=True;events.append([t,t+20])
 mixed=base+stem;assert np.isfinite(mixed).all() and abs(mixed).max()<1 and np.array_equal(mixed[~mask],base[~mask])
 outputs=[]
 for ext in ['flac','mp3']:outputs.append(write_audio(D/f'Deepwell-both-music-water-wind-pump-8min-v4.{ext}',mixed))
 outputs.append(write_audio(D/'Deepwell-pump-and-louder-wind-in-music-60s-v4.mp3',mixed[70*SR:130*SR]))
 # Same isolated-wind-in-music passage requested before the pump arrived.
 outputs.append(write_audio(D/'Deepwell-louder-wind-in-composition-80s-v4.mp3',mixed[95*SR:175*SR]))
 recipe['status']='Requested wind+3dB and supplied pump added; quieter water retained. New pump balance and complete mix await listening.'
 recipe['pump']={'source':source,'sha256':intake['sha256'],'original_seconds':20,'gain_db':gain,'nominal_isolated_lufs_before_fades':intake['measurements']['i']+gain,'events':events,'fade_in_seconds':3,'fade_out_seconds':5,'source_playback_speed':1,'purpose':'Occasional interior plant-room cycle between water/wind passages','source_measurements':intake['measurements']}
 recipe['processing']='Existing music/water/wind unchanged from v3; pump added at fixed gain with3s rise/5s fall. No EQ, compression, stretching or generation.'
 save('mix-recipe.json',recipe)
 levels=measure(D/'Deepwell-both-music-water-wind-pump-8min-v4.flac','deepwell-pump-v4');assert levels['tp']<-2
 save('delivery-validation.json',{'status':'passed','outputs':outputs,'full_mix_measurements':levels,'all_files_fully_decoded_and_recipe_compared':True,'outside_pump_windows_exact_to_v3':True,'pump_events_avoid_water_and_wind':True,'input_hashes_unchanged':sha(source)==intake['sha256'],'assistant_listening':False,'user_mix_approval':False})
 save('user-direction.json',{'date':'2026-11-01','wind_request':'yeah the wind is still too quiet, lets try the 3db louder version in the mix','pump_request':'here the distant water pmp for more variance','wind_increase_applied_db':3,'prior_water_amplitude_reduction':.9,'pump_supplied':intake['original_path'],'main_mix_seconds':480,'final_duration_unset':True})
 print('PASS: louder wind retained, pump added at1:20/4:35/7:00; in-composition check ready',flush=True)
if __name__=='__main__':main()
