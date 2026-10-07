from pathlib import Path
import json
H=Path(__file__).resolve().parent
c=json.loads((H.parent/'empty-junction-animation-v1/scene-plan-v1.json').read_text(encoding='utf-8'))
c['version']='v2'
c['status']='Improvement candidate; full preview review required'
c['feedback']={'v1':'User: decent, but needs to be 500% better. Requested execution of proposed improvements.', 'scope':'Broader broken cloud bank, evolving terrain mist, softer coupled lamp dips, longer independent habitation holds.'}
c['cloud_bank']={'seed':11201,'speed':3.4,'color':[88,98,124],'optical_depth':.82,'max_opacity':.42,'threshold':.38,'contrast':3.2,'fade':9,'parcels':[[580,86,245,29,.06],[805,94,265,32,.40],[1090,68,235,30,.76]]}
c['weather'][0].update({'speed':3.0,'optical_depth':.66,'max_opacity':.53,'feather':12,'color':[173,177,193], 'polygons':[[[813,305],[853,280],[892,266],[929,283],[966,279],[1006,292],[1037,277],[1074,278],[1113,299],[1140,324],[1121,341],[1060,354],[998,369],[938,369],[874,355]]], 'gusts':[[846,319,91,21],[926,313,93,25],[1006,325,88,23],[1080,320,81,22],[958,351,90,14],[1110,334,70,15]]})
c['weather'][1].update({'speed':4.2,'optical_depth':.54,'max_opacity':.43,'color':[155,163,181], 'gusts':[[620,342,82,16],[719,355,95,20],[803,371,76,16],[1246,305,87,16],[1342,289,92,20],[1413,267,82,17]]})
for w in c['weather']:
 w.update({'threshold':.30,'contrast':2.8,'fade':9})
 w['parcels']=[g+[ph] for g,ph in zip(w['gusts'],w['phases'])]
c['weather'][0].update({'threshold':.26,'optical_depth':.72})
c['weather'][0]['parcels'][1][1:4]=[302,93,34]
c['weather'][0]['parcels'][2][1:4]=[311,88,31]
for light in c['lights']:
 if light['kind']=='window' and light['name']!='cabin_window':
  for e in light['events']: e['hold']+=3; e['transition']=max(e['transition'],1.0)
 if light['name']=='door_lamp':
  for e in light['events']: e['depth']*=.58
  light['glows']=[[405,346,23,9,.9],[405,375,47,28,.62],[399,496,48,130,.34],[418,725,55,45,.28]]
c['twilight_shading']={'status':'Diagnostic candidate only; evaluate separately before inclusion','center':[878,282],'radius':[65,38],'maximum_fraction':.045}
c['method_notes']=['Source cloud transport retained. New elongated procedural cloud parcels use sky-matched colour and source-safe destination masks. No rock texture sampled.', 'Evolving optical mist changes thickness, height and edge structure while traveling forward; local zero-opacity renewals span the minute.', 'Lighting changes remain local. No trains, camera movement, foreground precipitation or new hardware.', 'Existing v1 renderer and historical media remain unchanged. Native source remains immutable.']
(H/'scene-plan-v2.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
