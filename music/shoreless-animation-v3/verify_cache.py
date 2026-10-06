from pathlib import Path
import json,numpy as np
from render_shoreless_v3 import ShorelessV3,H
s=ShorelessV3();cache=H/'.environment-cache'
assert json.loads((cache/'fingerprint.json').read_text())==s.fingerprint()
checks={}
for t in [20,27,47]:
 s.cache=None;fresh=s.frame(t)
 s.cache=cache;reused=s.frame(t)
 checks[str(t)]=np.array_equal(fresh,reused);assert checks[str(t)]
(H/'cache-validation.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'cached_vs_uncached_source_frames_exact':checks},indent=2)+'\n')
print('Cached and uncached minute frames match exactly at 20, 27 and 47 seconds')
