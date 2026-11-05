"""Independent fin/palette regression checks for the two visual-audit defects."""
from pathlib import Path
import hashlib,importlib.util,json
import cv2,numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;SCENE=HERE.parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    path=SCENE/'render.py';spec=importlib.util.spec_from_file_location('corrected_workshop_audit',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);scene=module.Scene()
    fin=[950,67,971,75];a,b,c,d=fin;fin_changed=[]
    for t in np.arange(0,120,.5):
        frame=scene.frame(float(t),only=['rain','drips']);bad=int(np.count_nonzero(np.any(frame[b:d,a:c]!=scene.base[b:d,a:c],axis=2)))
        if bad:fin_changed.append({'seconds':float(t),'pixels':bad})
    # A <=1.1px original-source warp must stay within the source palette of a
    # 5x5 neighborhood. This catches generated-sky injection inside a dark crown
    # independently of the renderer's allowed/output masks.
    roi=[1255,23,1672,254];a,b,c,d=roi;source=scene.base[b:d,a:c];kernel=np.ones((5,5),np.uint8)
    low=cv2.erode(source,kernel).astype(np.int16)-1;high=cv2.dilate(source,kernel).astype(np.int16)+1;palette=[]
    for t in [0,9,16,23,39,60,72,80,95,111,119.5]:
        frame=scene.frame(t,only=['foliage']);patch=frame[b:d,a:c].astype(np.int16);bad=np.any((patch<low)|(patch>high),axis=2);palette.append({'seconds':t,'pixels_outside_original_local_palette':int(bad.sum())})
        if t in [16,80]:Image.fromarray(frame).crop((1380,23,1495,110)).resize((690,522)).save(HERE/f'tree1-corrected-{t}.png')
    result={'status':'passed' if not fin_changed and all(x['pixels_outside_original_local_palette']==0 for x in palette) else 'failed','renderer_sha256':sha(path),'settings_sha256':sha(SCENE/'settings.json'),'fin_roi':fin,'weather_states':240,'fin_weather_changed_states':fin_changed,'foliage_local_palette_checks':palette,'limits':'Independent native geometry/palette tests and temporal stills; no continuous-playback or artistic approval claim.'}
    (HERE/'correction-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['status']=='passed'
if __name__=='__main__':main()
