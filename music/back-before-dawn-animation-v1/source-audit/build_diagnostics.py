"""Build source-only geometry annotations; never replace the production plate."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def main():
    spec=json.loads((HERE/'source-geometry-audit.json').read_text())
    source=ROOT/spec['source'];base=Image.open(source).convert('RGB');overlay=Image.new('RGBA',base.size);draw=ImageDraw.Draw(overlay)
    regions=[]
    screen=spec['screen'];regions.append(('CRT glass',screen['glass_quad'],(90,220,255)))
    for item in spec['cabin_emitter_rois']:
        a,b,c,d=item['roi'];regions.append((item['name'],[[a,b],[c,b],[c,d],[a,d]],(255,183,80)))
    regions.append(('Hood receiver plane',spec['main_work_lamp']['hood_receiver_polygon'],(240,140,90)))
    for key in ['conservative_right_rain_polygon','upper_clear_road_polygon','near_wet_road_polygon']:regions.append((key,spec['exterior'][key],(90,210,235)))
    regions.append(('Work-lamp shade',spec['main_work_lamp']['shade_polygon'],(255,225,130)))
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
    for index,(name,poly,color) in enumerate(regions,1):
        draw.polygon(poly,fill=(*color,42),outline=(*color,230),width=2)
        x,y=poly[0];draw.rectangle((x,y-18,x+24,y),fill=(8,12,18,225));draw.text((x+3,y-17),str(index),font=font,fill='white')
    result=Image.alpha_composite(base.convert('RGBA'),overlay).convert('RGB');result.save(HERE/'source-regions-annotated.png')
    receipt={'source':spec['source'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_pixels_modified':False,'annotated_output':'source-regions-annotated.png','numbered_regions':[{'number':i,'name':n} for i,(n,p,c) in enumerate(regions,1)],'note':'Planning/audit diagnostic only; original image remains unchanged.'}
    (HERE/'diagnostic-manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__':main()
