from pathlib import Path
import json
H=Path(__file__).resolve().parent
c=json.loads((H.parent/'cable-animation-v2/scene-plan-v2.json').read_text())
c['version']='v3';c['feedback']="its' getting there, can we do anything with the computer screens?"
c['computer_activity']={
 'left_aperture':[[270,480],[437,470],[448,578],[282,590]],
 'right_aperture':[[476,476],[614,467],[623,568],[483,578]],
 'route':[[335,516],[347,523],[358,532],[374,540],[387,547],[403,552]],
 'route_duration_seconds':20,'route_fade_seconds':2,'route_color':[112,141,140],'marker_radius':1.25,
 'nodes':[{'xy':[335,516],'start':2.2,'hold':2.1},{'xy':[403,552],'start':14.5,'hold':2.8}],
 'log_quad':[[485,490],[538,487],[540,515],[487,518]],'log_size':[56,32],'log_scroll_seconds':20,
 'indicators':[{'roi':[583,486,603,489],'start':1.7,'hold':4.6},{'roi':[584,500,607,503],'start':7.2,'hold':5.2},{'roi':[586,515,610,518],'start':13.5,'hold':4.2}],
 'cursor':{'roi':[506,550,510,552],'period_seconds':4,'color':[65,108,115]},
 'meter':{'start_xy':[576,560],'width':27,'height':2,'color':[40,83,91],'minimum_fraction':.22,'maximum_fraction':.86}}
c['implementation_note']='Screen-only v3 extension: map-route marker/nodes, perspective log scroll, status strokes, cursor and small meter. All v2 cloud, fog and lighting configuration retained byte-for-byte in their fields.'
p=H/'scene-plan-v3.json';assert not p.exists();p.write_text(json.dumps(c,indent=2)+'\n')
