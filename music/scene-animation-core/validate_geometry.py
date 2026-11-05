"""Targeted source geometry checks beyond broad output-footprint protection."""
from pathlib import Path
from html.parser import HTMLParser
import json,numpy as np
from PIL import Image
from validate_review import load,ROOT

def main():
    results={}
    for name in ['city','gate']:
        scene,media=load(name);checks={}
        if name=='city':
            cases=[('foreground_tower_roof_and_face',[1127,505,1170,567]),('fixed_river_boat',[1285,582,1317,602])]
            for label,(a,b,c,d) in cases:
                checks[label]=all(np.array_equal(scene.frame(t,only=['water','ferry'])[b:d,a:c],scene.base[b:d,a:c]) for t in [0,10,20,30,40,46,50,59]);assert checks[label]
            checks['minimum_car_headway_seconds']=[float(np.diff(np.r_[birth,birth[0]+60]).min()) for birth in scene.births]
            checks['active_source_qualified_mast_cores']=int(sum(bool(np.any(mask)) for _,mask,_ in scene.beacons))
            checks['inactive_seed_anchors']=len(scene.beacons)-checks['active_source_qualified_mast_cores']
        else:
            for label,(a,b,c,d) in [('fixed_planet',[766,145,916,241]),('fixed_small_moon',[944,167,969,193]),('fixed_support_pole',[479,125,492,430])]:
                checks[label]=all(np.array_equal(scene.frame(t,only=['clouds','canopy'])[b:d,a:c],scene.base[b:d,a:c]) for t in [0,10,20,30,40,50,59]);assert checks[label]
            original=np.array(Image.open(ROOT/'creative/brainstorm/2026-10-27-three-worlds/e1-gate-camp/concept-v1.png').convert('RGB'));outside=np.ones(original.shape[:2],bool);outside[600:680,280:321]=False
            checks['mug_patch_outside_roi_exact']=bool(np.array_equal(original[outside],scene.base[outside]));assert checks['mug_patch_outside_roi_exact']
        (media.parent/'source-geometry-validation.json').write_text(json.dumps(checks,indent=2)+'\n');results[name]=checks
    class Links(HTMLParser):
        def __init__(self):super().__init__();self.links=[]
        def handle_starttag(self,tag,attrs):self.links.extend(v for k,v in attrs if k in ['src','href'] and v)
    page=ROOT/'creative/animation-development/2026-11-05-16-17/review.html';parser=Links();parser.feed(page.read_text(encoding='utf-8'));missing=[v for v in parser.links if not v.startswith(('http','#')) and not (page.parent/v.split('#')[0]).exists()];assert not missing,missing
    report={'geometry':results,'review_links_checked':len(parser.links),'missing':missing};(page.parent/'review-link-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
