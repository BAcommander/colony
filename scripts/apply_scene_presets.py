"""Apply small reusable effect presets without editing a renderer."""
import argparse,json,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def apply(config,names):
 c=copy.deepcopy(config);presets=json.loads((ROOT/'creative/effect-presets.json').read_text())
 for name in names:
  v=presets[name]
  if name=='snow_heavier':c['effects']['snow']['count']=round(c['effects']['snow']['count']*v['count_multiplier'])
  elif name in ('water_still_glints','water_readable_glints'):c['effects']['water'].update(v)
  elif name=='foreground_snow_sparse':c['effects']['foreground_snow']=v.copy()
  elif name=='exterior_irregular_flicker':
   for lamp in c['effects'].get('exterior_lights',[])+c['effects'].get('light_spill',[]):lamp.update(v)
 c['applied_presets']=names;return c
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');p.add_argument('presets',nargs='+');a=p.parse_args();out=Path(a.output)
 if out.exists():raise FileExistsError(out)
 out.write_text(json.dumps(apply(json.loads(Path(a.source).read_text()),a.presets),indent=2))
