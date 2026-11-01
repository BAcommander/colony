"""Apply the requested +3dB wind to the current water-reduced composition."""
from revise_water_v2 import H,SR,sha,decode,layer,write_audio
import json
import numpy as np
D=H/'combined-review-v3';D.mkdir(exist_ok=True)
def save(name,data):(D/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def main():
 prior=H/'combined-review-v2';recipe=json.loads((prior/'mix-recipe.json').read_text());checks=json.loads((prior/'delivery-validation.json').read_text())
 src=prior/'Deepwell-water-down-10-percent-8min-v2.flac';assert sha(src)==next(x['sha256'] for x in checks['outputs'] if x['path']==str(src))
 assert sha(recipe['wind']['local_copy'])==recipe['wind']['sha256']
 original=decode(src);wind=layer(recipe['wind']['local_copy'],recipe['wind'],480)
 multiplier=10**(3/20);revised=(original.astype(float)+wind.astype(float)*(multiplier-1)).astype(np.float32)
 mask=np.zeros(len(original),bool)
 for start,end in recipe['wind']['events']:mask[start*SR:end*SR]=True
 assert np.array_equal(revised[~mask],original[~mask]) and np.isfinite(revised).all() and abs(revised).max()<1
 outputs=[]
 for ext in ['flac','mp3']:outputs.append(write_audio(D/f'Deepwell-water-down-wind-plus3dB-8min-v3.{ext}',revised))
 outputs.append(write_audio(D/'Deepwell-louder-wind-in-composition-80s-v3.mp3',revised[95*SR:175*SR]))
 recipe['status']='User-requested +3dB wind applied in composition; prior10% water reduction retained. Listening verdict pending.'
 recipe['wind']['loop']['gain_db']+=3;recipe['wind']['nominal_isolated_lufs_before_envelope']+=3
 for key in ['seam_sample_rms_step','ordinary_step_99_9_percentile']:recipe['wind']['loop'][key]*=multiplier
 recipe['wind']['loop']['boundary_measurements_note']='Previous loop step measurements scaled by +3dB amplitude factor'
 recipe['wind']['reuse']='Junction wind at +4.85dB source gain:3dB above Deepwell v2,3dB below Junction'
 recipe.pop('wind_comparison',None)
 recipe['wind_revision']={'change_db':3,'amplitude_multiplier':multiplier,'source_gain_db':recipe['wind']['loop']['gain_db'],'water_and_music_preserved':True,'outside_wind_events_samples_identical_to_v2':True,'timings_and_fades_unchanged':True}
 save('mix-recipe.json',recipe)
 save('delivery-validation.json',{'status':'passed','outputs':outputs,'all_outputs_fully_decoded_and_compared':True,'outside_wind_events_exact_to_v2':True,'source_unchanged':True,'assistant_listening':False,'new_balance_approval':False})
 save('user-feedback.json',{'date':'2026-11-01','verbatim':'yeah the wind is still too quiet, lets try the 3db louder version in the mix','action':'Apply +3dB wind to both events in the actual composition; keep water10% reduction, music, timings and fades. Provide same80-second full-mix1:35–2:55 excerpt.'})
 print('PASS: +3dB wind in full composition; same80-second excerpt ready',flush=True)
if __name__=='__main__':main()
