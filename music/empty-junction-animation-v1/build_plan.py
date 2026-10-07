"""Source-coordinate plan for catalog 11; no automatic transfer from another scene."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
def main():
 source=R/'final/11-empty-junction/artwork-v2.png'
 sha=hashlib.sha256(source.read_bytes()).hexdigest()
 assert sha=='ed7b02777c1dcc35504bc0628739688b56515f09ece89d58f299f2dd6013a4be'
 boundary=[[226,0],[235,43],[249,62],[254,113],[255,151],[265,157],[278,153],[292,174],[302,151],[320,153],[345,135],[353,145],[364,135],[370,123],[380,117],[391,133],[399,128],[405,85],[413,42],[423,29],[431,33],[437,60],[448,50],[455,37],[463,14],[474,18],[485,32],[495,43],[502,56],[509,29],[519,27],[528,48],[536,68],[539,115],[551,119],[555,87],[568,79],[576,68],[588,62],[599,73],[603,99],[617,79],[627,80],[632,93],[644,91],[649,107],[651,144],[659,155],[663,156],[665,163],[674,151],[685,156],[689,171],[699,147],[708,145],[715,127],[727,129],[735,145],[741,187],[749,188],[754,199],[762,188],[770,210],[776,232],[785,234],[790,218],[801,221],[812,196],[820,192],[827,202],[833,196],[846,196],[855,182],[863,183],[868,197],[878,195],[885,213],[888,245],[899,246],[902,260],[914,258],[921,276],[938,280],[945,274],[956,279],[969,261],[978,263],[986,270],[999,270],[1007,264],[1016,266],[1024,280],[1032,269],[1036,244],[1045,229],[1053,232],[1058,220],[1078,218],[1088,224],[1093,248],[1103,241],[1111,263],[1118,293],[1128,290],[1136,242],[1142,169],[1153,130],[1162,112],[1172,107],[1180,125],[1185,149],[1194,146],[1201,165],[1208,176],[1217,209],[1226,194],[1233,198],[1236,145],[1244,99],[1253,91],[1263,114],[1271,87],[1283,96],[1289,133],[1299,145],[1304,163],[1311,149],[1318,121],[1327,120],[1336,133],[1342,135],[1349,123],[1356,132],[1366,167],[1373,162],[1376,102],[1385,80],[1394,85],[1397,58],[1404,0]]
 def events(rows):return [{'start':a,'hold':b,'transition':c,'depth':d} for a,b,c,d in rows]
 def room(name,poly,rows):return {'name':name,'kind':'window','polygons':[poly],'feather':.65,'events':events(rows)}
 lights=[
 room('hall_left',[[924,391],[951,390],[951,399],[924,401]],[(6,6,.65,.82),(43,8,.8,.8)]),
 room('hall_middle',[[1005,386],[1031,385],[1031,396],[1005,398]],[(19,8,.8,.84),(57,5,.6,.78)]),
 room('hall_right',[[1094,380],[1120,379],[1120,390],[1094,392]],[(32,7,.6,.82)]),
 room('gallery_left',[[1295,351],[1336,348],[1336,373],[1295,379]],[(10,9,.8,.75),(46,5,.7,.72)]),
 room('gallery_right',[[1387,341],[1420,337],[1420,363],[1387,368]],[(27,11,1,.75)]),
 room('upper_room',[[1565,252],[1575,249],[1575,267],[1565,269]],[(39,10,.7,.78)]),
 room('cabin_window',[[385,420],[406,420],[407,519],[385,518]],[(29,4,1,.20)])
 ]
 lights+=[
 {'name':'door_lamp','kind':'lamp','polygons':[[[378,338],[437,343],[433,357],[376,351]]],'feather':.6,'glows':[[405,346,23,9,.9],[405,375,47,28,.35],[399,496,54,140,.12],[418,725,61,55,.11]],'events':events([(8.1,.32,.08,.72),(8.64,.22,.06,.6),(47.4,.42,.09,.76)])},
 {'name':'roof_amber','kind':'lamp','polygons':[[[206,144],[223,146],[223,164],[206,163]]],'feather':.5,'glows':[[214,154,10,9,.9],[214,169,9,13,.2]],'events':events([(14,.3,.07,.6),(14.6,.3,.07,.6),(51,.32,.07,.6),(51.65,.27,.07,.6)])},
 {'name':'yard_left','kind':'lamp','polygons':[[[883,441],[897,441],[897,449],[883,449]]],'feather':.5,'glows':[[890,445,16,13,.85],[889,468,26,26,.20],[890,533,29,11,.14]],'events':events([(23,1.5,.22,.65),(54,.5,.13,.65)])},
 {'name':'yard_bay','kind':'lamp','polygons':[[[1150,426],[1162,426],[1163,434],[1150,434]]],'feather':.5,'glows':[[1156,431,15,12,.85],[1156,464,27,33,.23],[1153,518,35,10,.12]],'events':events([(3,2,.3,.62),(35,.6,.12,.65)])},
 {'name':'path_lamp','kind':'lamp','polygons':[[[1406,394],[1416,394],[1422,400],[1417,404],[1408,400]]],'feather':.6,'glows':[[1414,400,13,10,.8],[1410,496,44,18,.17]],'events':events([(40,1.8,.28,.55)])}
 ]
 c={'scene_name':'The Empty Junction','catalog':11,'version':'v1','status':'Implementation candidate; user review pending','source':{'path':source.relative_to(R).as_posix(),'sha256':sha,'dimensions':[1672,941]},'duration':60,'fps':30,'preview_size':[1280,720],'final_size':[3840,2160],'ffmpeg':'C:/Program Files/ShareX/ffmpeg.exe',
 'sky':{'polygon':[[226,-5],[1404,-5]]+list(reversed(boundary)),'holes':[[[441,77],[446,76],[448,82],[446,96],[442,104]],[[600,104],[604,103],[607,111],[603,122]],[[832,206],[837,207],[837,216],[834,221],[830,214]],[[1181,156],[1185,157],[1186,168],[1182,173]]],'blockers':[[[313,0],[332,0],[332,200],[313,200]]],'inset':3,'feather':3,'background_sigma':[90,18],'speed_upper':3.4,'speed_horizon':2.1,'lifetime':60,'fade':7,'seed':1101,'strength':1.12,'groups':[[270,150,100,46],[370,113,115,45],[570,144,140,50],[764,150,145,49],[920,179,140,40],[1060,180,150,37],[1120,221,140,25],[923,232,170,26],[1310,119,120,50]]},
 'weather':[
 {'name':'far_mist','polygons':[[[813,315],[858,283],[879,272],[908,292],[935,286],[967,280],[1005,302],[1040,292],[1090,293],[1134,324],[1121,341],[1060,354],[998,369],[938,369],[874,355]]],'feather':16,'seed':1102,'speed':2.6,'color':[188,184,195],'optical_depth':.26,'max_opacity':.36,'gusts':[[846,320,58,10],[912,311,60,12],[976,327,63,12],[1049,326,58,11],[958,351,66,9],[1110,334,50,8]],'phases':[.05,.38,.72,.18,.54,.86]},
 {'name':'middle_mist','polygons':[[[582,323],[650,312],[710,320],[770,342],[821,350],[860,356],[875,366],[859,386],[802,395],[748,390],[683,376],[619,366],[591,351]],[[1190,297],[1241,267],[1300,256],[1351,224],[1404,220],[1445,241],[1476,274],[1451,301],[1391,311],[1332,315],[1270,329],[1235,334],[1204,332]]],'feather':15,'seed':1103,'speed':4.0,'color':[168,174,187],'optical_depth':.24,'max_opacity':.30,'gusts':[[620,342,65,10],[719,355,78,11],[803,371,67,9],[1246,305,69,9],[1342,289,75,11],[1413,267,67,10]],'phases':[.14,.48,.81,.25,.61,.91]}
 ],'weather_blockers':[[[934,326],[952,326],[952,380],[934,380]]],
 'lights':lights,'protected_geometry':['All rail/turnout/wagon geometry','Cabin shell, window frames, steps and railings','Mineral silhouettes and holes','Buildings, gallery framing, pipes and lamp housings','Foreground below weather masks','Trackside amber signal stays steady'],
 'omitted':{'vent':'Upper-right pipe is capped; no unambiguous open outlet, so no invented plume','screen':'No readable display in source','foreground_weather':'No near-camera dust or snowfall','hardware':'No added LEDs or structures'},
 'knowledge_reuse':[{'scene':'Basalt v6','evidence':'scripts/render_basalt.py','scope':'Accepted landscape-motion reference','reuse':'Coherent rightward sky transport, far/middle weather with occlusion','remap':'Native mineral silhouette and valley polygons','avoid':'Cloud shimmer, one opaque smoke stripe, copied silhouettes'},{'scene':'Saltline v5/v6','evidence':'music/saltline-animation-v1/periodic_transport.py','scope':'Accepted distant-dust look; later timing has separate scope','reuse':'Textured optical density and staggered locally faded renewal','remap':'Cold pass instead of foreground road; independent terrain depth masks','avoid':'Weather disappears after initial gusts; foreground excess'},{'scene':'Ringfall/Floodplain','evidence':'scripts/ambient_effects.py','scope':'Accepted masked-light principle, settings scene-specific','reuse':'Deterministic held events and complete emitter/local spill','remap':'Each aperture and practical light','avoid':'White cores left lit, synchronized room breathing'},{'scene':'Farpoint v6','evidence':'music/farpoint-animation-v6/README.md','scope':'Implemented candidate, not artistic acceptance','reuse':'Separate numeric evidence from visibility; full minute audit','remap':'No reuse of stars, planet or cabinet hardware','avoid':'More glowing effects as automatic improvement'}],
 'geometry_review':'Two visible routes and stationary crossing details retained from approved plate. Fine turnout mechanics are visually ambiguous; no claim of engineering accuracy and no animation of points.',
 'review':{'approved':False,'inspection':'Source and native crops inspected; production samples pending','scope':'Complete 60-second candidate for user playback before 4K'}}
 (H/'scene-plan-v1.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
 print('Source-bound plan saved')
if __name__=='__main__':main()

