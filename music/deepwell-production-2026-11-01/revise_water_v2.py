"""Reduce only water amplitude 10%; keep a separate +3dB wind audition."""
from build_combined_review import H,S,FF,SR,sha,decode,loop,write_audio
from pathlib import Path
import json,math
import numpy as np
OLD=H/'combined-review-v1';D=H/'combined-review-v2';D.mkdir(exist_ok=True)
def save(n,d):(D/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def layer(source,settings,seconds):
 lp=settings['loop'];material,_=loop(decode(source),*lp['trim'],lp['overlap_seconds'],lp['gain_db']);n=seconds*SR
 out=np.zeros((n,2),np.float32)
 for a,b in settings['events']:
  f=np.arange(a*SR,b*SR);local=f-a*SR;length=len(f)
  env=np.maximum(0,np.minimum(1,np.minimum(local/(settings['fade_in_seconds']*SR),(length-1-local)/(settings['fade_out_seconds']*SR))))
  out[a*SR:b*SR]=material[f%len(material)]*env[:,None]
 out[-10*SR:]*=np.linspace(1,0,10*SR,dtype=np.float32)[:,None]
 return out
def main():
 recipe=json.loads((OLD/'mix-recipe.json').read_text());validation=json.loads((OLD/'delivery-validation.json').read_text())
 p=OLD/'Deepwell-both-music-water-wind-8min-v1.flac';ref=next(x for x in validation['outputs'] if x['path']==str(p));assert sha(p)==ref['sha256']
 wet=decode(p);water=layer(recipe['water']['local_copy'],recipe['water'],480);wind=layer(recipe['wind']['local_copy'],recipe['wind'],480)
 revised=(wet.astype(float)-water.astype(float)*.1).astype(np.float32)
 mask=np.zeros(len(wet),bool)
 for a,b in recipe['water']['events']:mask[a*SR:b*SR]=True
 assert np.array_equal(revised[~mask],wet[~mask]);assert np.isfinite(revised).all() and abs(revised).max()<1
 outputs=[]
 for ext in ['flac','mp3']:outputs.append(write_audio(D/f'Deepwell-water-down-10-percent-8min-v2.{ext}',revised))
 outputs.append(write_audio(D/'Deepwell-water-down-check-2min-v2.mp3',revised[20*SR:140*SR]))
 # Same source range twice. Extra wind is only an optional audition, not the new main mix.
 start,end=100*SR,145*SR;normal=revised[start:end];louder=(normal.astype(float)+wind[start:end]*(10**(3/20)-1)).astype(np.float32)
 comparison=np.concatenate([normal,np.zeros((SR,2),np.float32),louder])
 outputs.append(write_audio(D/'Deepwell-wind-current-vs-plus3dB-91s.mp3',comparison))
 updated=json.loads(json.dumps(recipe));updated['status']='Water reduced 10% at user request; wind unchanged in main mix. Separate +3dB wind option for listening.'
 old_gain=updated['water']['loop']['gain_db'];delta=20*math.log10(.9)
 updated['water']['loop']['gain_db']=old_gain+delta;updated['water']['nominal_isolated_lufs_before_envelope']+=delta
 updated['water_revision']={'amplitude_multiplier':.9,'gain_change_db':delta,'previous_gain_db':old_gain,'new_gain_db':old_gain+delta,'scope':'Water only; timings and existing music/wind unchanged','outside_water_events_samples_identical_to_v1':True}
 updated['wind_comparison']={'file':'Deepwell-wind-current-vs-plus3dB-91s.mp3','full_mix_range':[100,145],'current_level_range':[0,45],'silence_separator':[45,46],'plus3db_range':[46,91],'wind_enters_at_comparison_seconds':[5,51],'new_main_mix_wind_gain_db':recipe['wind']['loop']['gain_db'],'optional_gain_db':recipe['wind']['loop']['gain_db']+3,'boost_applied_to_main_mix':False}
 save('mix-recipe.json',updated)
 save('delivery-validation.json',{'status':'passed','outputs':outputs,'full_decode_and_gain_recipe_comparison':True,'only_water_changed_in_main_mix':True,'outside_water_windows_exact':True,'assistant_listening':False,'water_change':updated['water_revision'],'optional_wind_comparison':updated['wind_comparison']})
 feedback={'date':'2026-11-01','verbatim':"water is a little too loud maybe 10%, at what point does the wind kick in? i feel like i was missing it too much is there a 3rd sfx we could generate for the plant room to add more variancE?",'action':'Reduce water amplitude 10%, report wind timing, provide separate optional +3dB wind comparison, propose plant-room circulation pump prompt','wind_timing_full_mix':recipe['wind']['events'],'wind_timing_two_minute_check':'Starts1:25, eight-second fade-in; excerpt ends before the wind event finishes','third_sfx_generated':False,'paid_generation_performed':False,'new_balance_approval':False}
 save('user-feedback.json',feedback)
 prompt='A distant water-circulation pump in a quiet plant room. A soft rounded motor hum slowly takes load, with gentle hollow pipe resonance and one muted valve sigh, then settles. Smooth and unobtrusive. No rhythmic pulsing, harsh hiss, clunks, alarms, voices or music.\n'
 (D/'plant-room-pump-sfx-prompt.txt').write_text(prompt,encoding='utf-8')
 save('plant-room-sfx-proposal.json',{'status':'Prompt only; not generated','suggested_test_duration_seconds':15,'suggested_variants':2,'prompt':'plant-room-pump-sfx-prompt.txt','scene_reason':'Visible plant equipment; slow mechanical load change offers a different texture from exterior water and wind','mixing_proposal':'Occasional soft cycles between exterior-sound events, not a continuous motor drone','actual_cost_and_settings':'Unknown; manual user generation, no API action'})
 print('PASS: water-only -10% revision and separate optional wind comparison',flush=True)
if __name__=='__main__':main()
