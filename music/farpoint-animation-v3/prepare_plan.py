"""Freeze the v3 additions while retaining the reviewed v2 cloud parameters."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent
p=H/'scene-plan-v3.json'
c=json.loads(p.read_text())
c['protected_geometry']=[x for x in c['protected_geometry'] if x!='blue and pink LEDs']
c['prototype']['duration']=12
c['prototype']['method']='Reviewed direct cloud travel plus added atmosphere/instrumentation; forward excerpt, not a seamless loop'
c['new_atmosphere']={
 'lower_cloud':{'roi':[1290,465,1480,591],
   'polygon':[[1322,507],[1344,491],[1379,494],[1410,513],[1440,548],[1446,567],[1418,580],[1384,566],[1354,543]],
   'protected_crater':[1339,563,23], 'speed_pixels_per_second':2.8,'gain':.82,
   'blue_red_ratio':.63,'blue_offset':3,'red_floor':85,'red_range':80},
 'cloud_shadows':{'offset':[-14,18],'blur_sigma':4.5,'strength':.26,
   'method':'Difference from original cloud-shadow state, attenuated by moving cloud opacity; local terrain light only'}
}
c['screen_additions']={
 'radar_center':[238,117],'radar_radius':17,'radar_period':8,
 'route_color':[42,115,136],'route_width':2,
 'meter_origins':[[39,194],[91,193],[139,192],[181,191]],
 'meter_color':[35,98,103], 'meter_segments':5,
 'method':'Perspective-confined moving sweep on existing small dial, sequential original-diagram links and bottom-panel status segments'}
def ev(start,hold,depth,transition=.06):return dict(start=start,hold=hold,depth=depth,transition=transition)
c['instrument_lights']=[
 {'name':'blue_left_indicator','core_polygons':[[[43.1,68.7],[46.5,68.7],[46.5,88.7],[42.9,88.7]],[[40.5,83.9],[44,83.9],[44,88.2],[40.5,88.2]]],
  'halo_center':[44.4,80],'halo_radius':[7,16],'color':'blue','events':[ev(.9,.26,.88),ev(1.35,.22,.82),ev(7.4,.55,.72)]},
 {'name':'amber_status','core_polygons':[[[214.5,54.5],[220.9,55.3],[221.5,65.7],[214.6,65.9]]],
  'halo_center':[217.8,60.2],'halo_radius':[13,19],'color':'amber','events':[ev(5.5,1.45,.78,.18)]},
 {'name':'blue_column_indicator','core_polygons':[[[219.6,239],[223.9,239],[223.9,253.5],[219.6,253.5]]],
  'halo_center':[221.8,246],'halo_radius':[9,19],'color':'blue','events':[ev(2.1,.22,.84),ev(2.5,.25,.84),ev(9.1,.62,.8)]},
 {'name':'blue_upper_strip','core_polygons':[[[441,26.4],[486.1,23.9],[486.4,28],[441.1,30.5]]],
  'halo_center':[463.5,27.3],'halo_radius':[32,10],'color':'blue','events':[ev(3.25,.56,.66,.1),ev(10.45,.3,.52)]},
 {'name':'pink_left_desk_strip','core_polygons':[[[356.8,775.7],[439.8,784.3],[439.9,789.2],[356.4,780.6]]],
  'halo_center':[396,790],'halo_radius':[56,25],'color':'pink','events':[ev(4.55,.29,.64),ev(9.75,.4,.55)]},
 {'name':'pink_right_desk_strip','core_polygons':[[[668.1,772],[704.3,759.1],[705.9,763.8],[670,776.8]]],
  'halo_center':[687,774],'halo_radius':[29,22],'color':'pink','events':[ev(7,.65,.61,.13)]}
]
c['steady_lights']=['lower blue column indicator','right exterior habitat window','unchanged unrelated source practicals']
c['layer_order']=['clouds','veil','cloud_shadows','lower_cloud','windows','screen','lamp','instrument_lights']
c['isolated_layers']=['new_atmosphere','habitation']
c['loop_method']='Twelve-second forward review excerpt. No seamless closure claimed. Preserve reviewed v2 principal rates when designing periodic delivery.'
p.write_text(json.dumps(c,indent=2)+'\n')
