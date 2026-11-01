from prepare_samples import H,S,sha,decode,measure
from pathlib import Path
import json,shutil,numpy as np
src=Path('C:/Users/jazzs/Downloads/A_distant_water-circ_#4-1793555177439.mp3');dst=S/src.name
if not dst.exists():shutil.copy2(src,dst)
assert sha(src)==sha(dst)
x=decode(dst);assert np.isfinite(x).all()
m=measure(dst,'plant-pump-source');gain=min(-39-m['i'],-18-m['tp'])
record={'date':'2026-11-01','user_message':'here the distant water pmp for more variance','original_path':str(src),'source_copy':str(dst),'sha256':sha(dst),'frames':len(x),'seconds':len(x)/48000,'measurements':m,'proposed_gain_db':gain,'proposed_nominal_lufs':m['i']+gain,'proposed_peak_dbtp':m['tp']+gain,'actual_generation_prompt_model_cost':'Not verified; supplied by user','assistant_listening':False}
(H/'pump-intake.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record),flush=True)
