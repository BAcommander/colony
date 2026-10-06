from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1]
src=R/'final/09-offshore-night-office/artwork-v1.png'
c={
 'scene':'The Shoreless Colony','catalog':'09','version':'v1','duration':20,'fps':30,'preview_size':[1280,720],
 'ffmpeg':'C:/Program Files/ShareX/ffmpeg.exe',
 'source':{'path':src.relative_to(R).as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'dimensions':[1672,941]},
 'window':[[84,55],[1217,150],[1217,576],[1042,602],[899,625],[892,637],[84,711]],
 'water_polygon':[[84,342],[1217,342],[1217,576],[1042,602],[899,625],[892,637],[84,711]],
 'water_exclusions':[
  [[84,335],[248,342],[350,353],[374,365],[386,386],[387,451],[410,454],[410,503],[382,526],[382,651],[359,676],[325,683],[284,693],[174,694],[105,687],[84,675]],
  [[380,410],[595,408],[605,443],[594,467],[407,475],[384,462]],
  [[557,363],[722,362],[780,370],[797,385],[800,427],[814,435],[814,460],[793,477],[793,517],[805,518],[805,550],[784,562],[644,567],[612,553],[589,549],[566,555],[552,544],[557,479],[578,470],[578,446]],
  [[793,412],[928,408],[950,422],[950,451],[917,457],[917,498],[899,501],[883,495],[883,459],[797,467]],
  [[918,381],[955,374],[1039,379],[1066,389],[1076,424],[1089,437],[1089,457],[1076,459],[1076,500],[1065,506],[954,508],[937,500],[935,475],[925,462],[912,451]],
  [[1076,342],[1117,342],[1117,360],[1076,360]],[[1145,341],[1190,341],[1190,361],[1145,361]],
  [[1039,577],[1195,562],[1197,615],[1037,622]]
 ],
 'sky_polygon':[[84,55],[1217,150],[1217,333],[1060,333],[1019,316],[1014,306],[950,303],[934,293],[849,288],[835,282],[727,277],[710,297],[678,314],[648,326],[623,332],[574,333],[571,315],[553,309],[529,310],[518,328],[501,328],[493,308],[445,304],[436,287],[383,273],[246,268],[231,278],[212,296],[196,303],[179,324],[162,333],[84,333]],
 'moons':[[1000,175,23],[1076,182,9]],
 'protected_polygons':[[[106,280],[132,280],[132,342],[106,342]]],
 'protected_lines':[[[244,299],[244,358],7],[[682,334],[682,374],6],[[950,318],[950,383],6],[[1097,283],[1097,348],5],[[1167,277],[1167,348],5]],
 'clouds':[{'name':'upper_clouds','y_range':[50,247],'speed':2.2,'phase':.1,'gain':.85},{'name':'horizon_clouds','y_range':[218,337],'speed':1.4,'phase':.45,'gain':.7}],
 'water':{'roi':[80,337,1221,716],'seed':909,'components':24,'time_scale':.17,'specular_strength':3.,'wavelength_range':[1.6,9.0],'reflection_sigma_x':.55,'reflection_sigma_y':.45,'displacement_scale':.40,'reflection_contrast':.045,'highlight_roughness':.35,'sampling_filter_pixels':.9,'edge_damping_pixels':10,'loop_seconds':20,'perspective_horizon_y':325,'perspective_distance_scale':2100,'perspective_center_x':700,'perspective_lateral_scale':480},
 'lights':[
  {'name':'near_left_panes','polygons':[[[272,409],[284,409],[284,424],[272,425]],[[288,409],[301,409],[301,424],[288,424]]],'start':2.4,'hold':5.4,'transition':.3,'floor':.18},
  {'name':'middle_right_panes','polygons':[[[762,399],[772,399],[772,410],[762,410]],[[775,399],[782,399],[782,410],[775,410]]],'start':10.3,'hold':6.2,'transition':.32,'floor':.22},
  {'name':'far_left_panes','polygons':[[[982,407],[989,407],[989,415],[982,415]],[[992,407],[997,407],[997,415],[992,415]]],'start':17.7,'hold':4.7,'transition':.3,'floor':.25}
 ],
 'lamp':{'aperture':[[1554,350],[1671,350],[1671,359],[1559,359]],'wall_polygon':[[1509,360],[1671,360],[1671,495],[1512,485]],'wall_center':[1616,387],'wall_radius':[120,107],'desk_polygon':[[1120,652],[1340,627],[1671,701],[1671,788],[1400,754]],'desk_center':[1490,706],'desk_radius':[260,90],'events':[{'start':4.2,'hold':.32,'transition':.08,'depth':.62},{'start':4.82,'hold':.18,'transition':.06,'depth':.38},{'start':14.1,'hold':.55,'transition':.13,'depth':.44}]},
 'computers':{'left_aperture':[[1363,487],[1481,495],[1467,588],[1350,577]],'right_aperture':[[1515,500],[1640,510],[1624,609],[1500,594]],'route':[[1360,539],[1386,538],[1403,541],[1426,542],[1441,548],[1464,552]],'marker_radius':2.0,'route_color':[44,112,130],'log_quad':[[1514,509],[1540,511],[1528,587],[1505,583]],'log_size':[32,88],'meter_quad':[[1593,563],[1623,565],[1619,590],[1588,587]],'meter_size':[42,30]},
 'turbines':[
  {'hub':[1096,282],'radius':42,'blade_ends':[[1100,245],[1067,292],[1118,307]],'width':2,'period':20,'direction':1},
  {'hub':[1166,275],'radius':45,'blade_ends':[[1156,234],[1203,281],[1148,307]],'width':2,'period':20,'direction':1}
 ],
 'beacons':[{'center':[1096,282],'phase':.5,'period':4},{'center':[1166,275],'phase':2.0,'period':5}],
 'knowledge_reuse':{'bank':'creative/ANIMATION_KNOWLEDGE_BANK.md','examples':['Glacier/Floodplain filtered reflection surface and sampling exclusions','Cable Station source-cloud transport and readable monitor actions','Ringfall/Floodplain complete apertures and coupled lamp spill','Saltline/Icebound independent circular light schedules'],'remapping':'All polygons, caissons, panes, screen quads, moons and turbine hubs mapped on Shoreless artwork-v1 only.','avoid':['Rainline excessive water and loose window masks','Static distant weather with only foreground activity','Global exposure pulsing','Copying other scenes coordinates'],'candidate_addition':'Slow rotation extracted from the two existing turbines; new scene-specific optical reconstruction, requires review.'},
 'isolated_layers':['water','sky','turbines','room'],
 'protected':'Interior/window frame, furniture, caissons, walkways, islands and moons remain fixed; rotor blades are the explicit geometry-motion exception.'
}
p=H/'scene-plan-v1.json';assert not p.exists();p.write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
print('Shoreless source and scene plan frozen',c['source']['sha256'])
