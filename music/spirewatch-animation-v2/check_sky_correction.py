from pathlib import Path
import importlib.util,json,hashlib
import numpy as np
from render_spirewatch import Spirewatch,H,save
spec=importlib.util.spec_from_file_location('before_sky',H/'history/pre-sky-correction/render_spirewatch.py')
before=importlib.util.module_from_spec(spec);spec.loader.exec_module(before);before.H=H
old=before.Spirewatch();new=Spirewatch();reports={}
for layer in new.layer_masks:
 if layer in ('clouds','mist'):continue
 assert np.array_equal(old.masks[layer],new.masks[layer]),layer
 for t in [0,8,20,32,40,52.6]:assert np.array_equal(old.frame(t,layer),new.frame(t,layer)),(layer,t)
 reports[layer]={'mask_exact':True,'source_frames_exact_at':[0,8,20,32,40,52.6]}
save('sky-correction-regression.json',{'fingerprint':new.fingerprint(),'retained_layer_checks':reports,'change':'Only reconstructed cloud source texture; masks, all schedules and other material/effect algorithms unchanged','older_render_fingerprint':json.loads((H/'history/pre-sky-correction/isolated-validation.json').read_text())['fingerprint'],'retained_isolated_media':['falls-isolated-8s.mp4','water-isolated-8s.mp4','storm-isolated-12s.mp4','city-isolated-16s.mp4'],'new_atmosphere_render_required':True})
print('All fourteen non-sky layers match before/after at six source times',flush=True)
