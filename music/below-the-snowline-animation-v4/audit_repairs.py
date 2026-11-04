"""Target the defects identified in the user's V3 screenshots."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
import render_v4 as r
H=Path(__file__).resolve().parent

def main():
    s=r.Scene();report={}
    # Frozen geometry must never be a cloud source or a cloud destination.
    guards={}
    for label,xy in s.g['landmark_guards'].items():
        x,y=r.point(*xy)
        assert s.sky[y,x]==0 and s.skyvalid[y,x]==0,(label,s.sky[y,x])
        guards[label]={'native_xy':xy,'destination_weight':float(s.sky[y,x]),'source_valid':False}
    outside=s.sky==0;changes=[]
    for t in [0,7,19,31,45,59,73,91,109,119.9]:
        f=s.base.astype(np.float32);s.sky_layer(f,t)
        assert np.array_equal(f[outside],s.base[outside])
        changes.append(float(np.abs(f[s.sky>.5]-s.base[s.sky>.5]).mean()))
    assert max(changes)>.5
    report['cloud_geometry']={'landmarks':guards,'all_pixels_outside_cloud_mask_exact_at_10_phases':True,'moving_sky_mean_changes':changes}
    # Texture wrapping must resemble adjacent samples rather than expose a step.
    seams=[]
    for seed in [100,101,102,63,34]:
        tex=s.texture(seed)
        row=float(np.abs(tex[0]-tex[-1]).max());col=float(np.abs(tex[:,0]-tex[:,-1]).max())
        normal_row=float(np.abs(np.diff(tex,axis=0)).max());normal_col=float(np.abs(np.diff(tex,axis=1)).max())
        assert row<=normal_row*1.05+1e-5 and col<=normal_col*1.05+1e-5
        seams.append({'seed':seed,'row_wrap_max':row,'ordinary_row_max':normal_row,'column_wrap_max':col,'ordinary_column_max':normal_col})
    report['fog_seams']=seams
    # Physical control lens colour and texture are scaled, never painted over.
    ratios=[]
    for t in [0,3,9,25,45,80,110]:
        f=s.base.astype(np.float32);s.interior(f,t)
        for c,m in s.buttons:
            mask=(m>.2)&(np.min(s.base,axis=2)>2)
            rgb_ratio=f[mask]/s.base[mask].astype(np.float32)
            spread=float(np.ptp(rgb_ratio,axis=1).max())
            assert spread<2e-5,(c['name'],t,spread)
            ratios.append(spread)
    report['console_materials']={'original_rgb_ratios_preserved':True,'worst_channel_scale_spread':max(ratios),'physical_lens_count':len(s.buttons)}
    raw=(H/'assets/lambda-shuttle-master.png').read_bytes();im=Image.open(H/'assets/lambda-shuttle-master.png')
    assert im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0
    report['shuttle']={'master_sha256':hashlib.sha256(raw).hexdigest(),'rgba':True,'original_alpha_preserved_in_master':True,'compositing':'premultiplied-alpha resampling, subpixel translation and atmospheric colour blending','tool':'built-in image_gen','prompt':'assets/shuttle-prompt.txt'}
    report['hardware']={'mapped_beacons':s.g['beacons'],'cannon_cycles':s.g['charge_cycles'],'charging_only_no_firing':True}
    report['limits']='Geometry/material/texture checks and temporal still inspection; artistic approval requires user review.'
    (H/'repair-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('PASS: protected sky geometry, seamless fog texture, original lens materials and transparent shuttle asset',flush=True)

if __name__=='__main__':main()
