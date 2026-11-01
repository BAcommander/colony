"""Fresh source-space map for the revised complete-cabin composition."""
from pathlib import Path
import json,hashlib,shutil
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1]
source=R/'music/empty-junction-visual-revision-v1/artwork-v3.png'
target=H/'artwork-v3.png'
if not target.exists():shutil.copy2(source,target)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(source)==digest(target)=='44bd1465510494ed91bc54c9461cb77da590179cb708c6dd21fcd6a6b51f8ba8'
def rect(x0,y0,x1,y1):return [[x0,y0],[x1,y0],[x1,y1],[x0,y1]]
def event(start,hold,depth=.78,transition=1.4):return {'start':start,'hold':hold,'transition':transition,'depth':depth}
def light(name,poly,events,glows=None,feather=.7):
    d={'name':name,'polygons':poly,'events':events,'feather':feather}
    if glows:d['glows']=glows
    return d
# Boundary traced against the new source. Conservative inset protects pale fins.
skyline=[[109,-5],[1392,-5],[1390,90],[1380,89],[1372,113],[1364,146],[1362,178],[1350,165],[1342,146],[1335,140],[1330,135],[1320,149],[1312,160],[1308,158],[1302,142],[1298,161],[1295,183],[1290,186],[1286,176],[1285,163],[1280,148],[1275,130],[1269,125],[1265,116],[1260,111],[1254,108],[1250,111],[1244,123],[1237,108],[1231,111],[1226,125],[1228,160],[1229,182],[1226,198],[1228,237],[1227,270],[1216,286],[1210,276],[1202,265],[1200,235],[1190,219],[1181,190],[1176,184],[1171,185],[1170,208],[1163,193],[1156,174],[1150,161],[1146,153],[1140,154],[1135,165],[1128,187],[1127,206],[1121,215],[1117,247],[1112,260],[1114,295],[1107,301],[1100,280],[1094,290],[1085,284],[1080,252],[1074,250],[1071,265],[1067,246],[1061,246],[1055,260],[1050,283],[1043,281],[1035,292],[1020,294],[1014,285],[1002,285],[997,277],[989,277],[981,284],[973,274],[965,272],[957,283],[950,271],[943,274],[938,242],[934,231],[928,227],[925,231],[921,214],[914,211],[907,219],[904,234],[898,231],[894,238],[888,245],[887,232],[882,222],[874,222],[868,235],[862,239],[857,236],[851,252],[848,258],[839,253],[834,237],[826,234],[821,220],[816,220],[808,235],[802,233],[800,205],[794,160],[785,155],[780,160],[774,155],[770,161],[762,182],[757,200],[751,194],[744,196],[739,201],[731,193],[725,191],[720,181],[712,180],[705,190],[701,145],[698,116],[690,116],[684,111],[676,117],[671,105],[662,102],[654,115],[649,103],[639,94],[633,83],[627,83],[620,95],[613,101],[607,101],[601,123],[596,149],[585,147],[580,141],[577,103],[567,63],[561,55],[555,60],[552,51],[547,51],[540,58],[536,47],[525,36],[520,32],[512,39],[508,30],[501,29],[494,50],[492,65],[485,81],[481,70],[475,76],[470,115],[466,98],[460,96],[462,79],[457,57],[450,45],[441,47],[436,52],[430,51],[427,76],[423,92],[419,120],[409,148],[404,146],[398,159],[390,161],[380,176],[371,194],[367,170],[361,155],[351,151],[347,146],[338,151],[333,152],[327,169],[320,178],[314,201],[307,204],[300,192],[293,194],[285,198],[278,216],[266,216],[258,217],[251,215],[246,156],[237,113],[230,98],[220,97],[215,83],[209,83],[205,97],[198,82],[193,74],[190,62],[182,62],[176,55],[168,55],[160,63],[154,78],[148,70],[140,50],[132,36],[125,25],[122,7],[115,0]]
blockers=[rect(159,474,556,806),[[607,544],[659,539],[668,571],[788,568],[788,482],[883,478],[887,421],[1157,411],[1187,438],[1188,596],[608,604]],
 [[1203,399],[1450,377],[1457,448],[1202,472]],[[1480,317],[1644,279],[1653,423],[1453,467]],rect(792,671,844,798)]
lights=[
 light('hall_left',[rect(935,447,946,457),rect(949,446,958,456)],[event(5,12),event(42,10,.72)]),
 light('hall_middle',[[[1018,441],[1031,440],[1031,451],[1018,452]],[[1035,440],[1047,439],[1047,451],[1035,452]]],[event(19,13,.82)]),
 light('hall_right',[[[1100,436],[1111,435],[1111,447],[1100,448]],[[1116,435],[1126,434],[1126,446],[1116,447]]],[event(36,13,.80)]),
 light('gallery_left',[[[1230,410],[1251,408],[1251,431],[1230,434]]],[event(9,13,.72),event(48,8,.68)]),
 light('gallery_middle',[[[1290,406],[1312,404],[1312,427],[1290,429]]],[event(25,14,.78)]),
 light('gallery_right',[[[1364,400],[1387,398],[1387,420],[1364,423]]],[event(40,12,.74)]),
 light('gallery_far',[[[1410,395],[1430,393],[1430,416],[1410,419]]],[event(16,10,.66)]),
 light('upper_left',[[[1555,313],[1565,310],[1565,330],[1555,333]]],[event(12,16,.74)]),
 light('upper_right',[[[1573,307],[1588,303],[1588,326],[1573,330]]],[event(36,15,.78)]),
 light('cabin_window',[rect(391,572,410,632)],[event(30,6,.25,1.2)]),
 light('door_lamp',[[[396,530],[419,529],[420,536],[396,538]]],[event(8.2,.6,.35,.15),event(47.6,.7,.38,.16)],
       [[406,534,15,7,.8],[405,556,24,20,.40],[405,621,28,74,.19],[433,762,62,27,.22]],.55),
 light('roof_amber',[rect(296,411,312,425)],[event(14,1.8,.82,.35),event(44,2.5,.85,.5)],[[304,417,12,10,.7]],.55),
 light('yard_signal',[rect(811,683,826,697)],[event(25,2.4,.78,.6),event(52,1.5,.74,.4)],[[817,689,12,12,.7]],.55),
 light('hall_practical',[rect(973,498,989,509)],[event(33,4,.48,1)],[[980,504,17,14,.45],[982,551,33,45,.18]],.6),
 light('upper_door_lamp',[rect(1606,300,1633,309)],[event(20,3,.40,.8)],[[1620,305,15,9,.65],[1620,341,24,29,.14]],.6),
]
weather=[
 {'name':'far_mist','polygons':[[[648,351],[768,341],[865,348],[981,329],[1119,339],[1200,370],[1165,412],[1045,427],[890,410],[752,428],[652,402]]],
  'feather':15,'seed':44102,'speed':3,'color':[164,174,193],'optical_depth':.42,'max_opacity':.32,'threshold':.30,'contrast':2.7,'fade':10,
  'parcels':[[819,373,94,22,.06],[964,367,110,23,.39],[1091,385,103,23,.73]]},
 {'name':'middle_mist','polygons':[[[489,358],[599,366],[710,405],[797,444],[785,478],[677,458],[573,420],[492,401]],[[1201,317],[1330,306],[1472,327],[1472,379],[1340,385],[1220,371]]],
  'feather':13,'seed':44103,'speed':3.8,'color':[151,163,184],'optical_depth':.33,'max_opacity':.27,'threshold':.33,'contrast':2.8,'fade':10,
  'parcels':[[595,404,88,19,.14],[735,439,85,18,.52],[1325,352,105,22,.82]]},
]
new_motion={
 'terrain_flow':{'polygon':[[942,307],[1001,315],[1053,348],[1115,370],[1198,352],[1206,388],[1115,411],[1044,387],[984,358],[940,335]],
  'path':[[964,320],[994,340],[1036,363],[1083,384],[1133,387],[1182,370]],'widths':[2,5,10,15,11,2],
  'speed':6,'seed':44201,'opacity':.26,'color':[171,181,199],'feather':9},
 'cabin_exhaust':{'polygon':[[131,432],[176,427],[227,458],[275,498],[333,534],[337,556],[306,562],[266,545],[217,532],[164,499],[125,465]],
  'path':[[315,546],[302,537],[280,526],[254,515],[218,497],[182,480],[149,457]],'widths':[1,3,6,9,13,16,1],
  'lifetime':15,'particles':28,'seed':44202,'opacity':.38,'color':[182,190,205],'feather':4,
  'blockers':[rect(269,392,280,569),rect(363,424,373,515)],'anchor':[315,546]},
 'yard_powder':{'polygons':[[[550,771],[617,759],[689,770],[756,791],[814,814],[806,836],[737,823],[672,804],[609,797],[549,800]],
   [[1149,675],[1215,693],[1300,724],[1400,755],[1506,797],[1590,858],[1580,889],[1481,839],[1376,801],[1280,763],[1199,731],[1145,705]]],
  'routes':[{'path':[[556,786],[613,778],[680,786],[740,805],[800,823]],'widths':[1,5,9,10,1],'speed':18},
   {'path':[[1158,692],[1210,712],[1295,743],[1391,778],[1491,818],[1570,870]],'widths':[1,4,7,10,12,1],'speed':17}],
  'seed':44203,'opacity':.33,'color':[164,174,192],'feather':7,'blockers':[rect(792,670,846,800)]},
}
c={'scene_name':'The Empty Junction','catalog':11,'version':'animation-v4-artwork-v3','status':'New-composition animation preview; user review pending',
 'source':{'path':target.relative_to(R).as_posix(),'sha256':digest(target),'dimensions':list(Image.open(target).size)},
 'duration':60,'fps':30,'preview_size':[1280,720],'final_size':[3840,2160],'ffmpeg':shutil.which('ffmpeg'),
 'sky':{'polygon':skyline,'holes':[],'blockers':[rect(263,201,285,493),rect(359,262,376,495)],'inset':8,'feather':24,
   'background_sigma':[90,18],'speed_upper':2.8,'speed_horizon':1.7,'lifetime':60,'fade':8,'seed':44101,'strength':1.05,
   'groups':[[300,98,125,40],[675,95,130,44],[866,121,150,40],[1023,156,145,32],[1050,222,120,28],[1305,81,110,28]]},
 'cloud_bank':{'seed':44110,'speed':2.8,'color':[102,119,150],'optical_depth':.42,'max_opacity':.25,'threshold':.39,'contrast':2.9,'fade':10,
   'parcels':[[735,90,210,26,.08],[957,104,235,28,.43],[1160,72,185,24,.78]]},
 'weather':weather,'weather_blockers':blockers,'lights':lights,'new_motion':new_motion,
 'wind_visual_schedule':{'cycle_seconds':180,'active_seconds':60,'fade_in_seconds':5,'fade_out_seconds':8,'quiet_minutes_retain_cloud_mist_plume_and_lights':True},
 'knowledge_reuse':{'methods':['Existing Junction v1 source-safe sky and practical light masks','Junction v2 evolving cloud/mist parcels','Junction v3 terrain route fields and anchored plume'],
  'remapped':'Every polygon, field centre, route, light aperture, spill and occluder mapped anew to artwork v3; no coordinate transform applied to the previous masks.',
  'avoid':['Do not reuse old source coordinates','Protect sky sampling and output from rocks','No opacity-only stripe as main weather','No synchronized global dimming','No train added to the fixed artwork']},
 'source_detail':'1672x941 native; preview 1280x720. Any later 4K is disclosed upscaling, not native detail.',
 'review':{'approved':False,'scope':'Full silent units, scheduled three-minute cycle and four-minute music/SFX preview; no final 4K or one-hour video yet.'}}
(H/'scene-plan-v4.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
print('New source frozen and all masks mapped',digest(target),flush=True)
