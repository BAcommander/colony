"""Freeze source-specific geometry and schedules for the first Crimson Sky trial."""
from pathlib import Path
import json, hashlib, shutil
import imageio_ffmpeg

H = Path(__file__).resolve().parent
R = H.parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    target = H / 'scene-plan-v1.json'
    assert not target.exists(), 'Preserve the existing plan'
    deps = H / 'dependencies'
    deps.mkdir(exist_ok=True)
    for name, path in [('ambient_effects.py', R/'scripts/ambient_effects.py'),
                       ('dust_transport.py', R/'music/saltline-animation-v1/dust_transport.py'),
                       ('periodic_transport.py', R/'music/saltline-animation-v1/periodic_transport.py')]:
        shutil.copyfile(path, deps/name)
    c = {
        'scene_name': 'Beneath a Crimson Sky', 'version': 'v1',
        'status': 'implemented_candidate_not_user_approved',
        'authority': {'date': '2026-10-08', 'request': 'ok so shall we execute the prompt?',
                      'scope': 'Execute production prompt v2; full minute preview and 4K still. 4K animation after complete-preview acceptance.'},
        'source': {'path': (H/'source-v11.png').relative_to(R).as_posix(),
                   'sha256': digest(H/'source-v11.png'), 'dimensions': [1672,941]},
        'duration': 60, 'fps': 30, 'preview_size': [1280,720], 'final_size': [3840,2160],
        'ffmpeg': imageio_ffmpeg.get_ffmpeg_exe(),
        'protected_geometry': ['camera','roof','pillar','bench','blanket','barrel','parapet','fortress silhouettes','rock contours','gateway masonry','world and clear opening'],
        'sky': {
            'polygon': [[244,103],[297,83],[297,70],[548,47],[550,63],[590,73],[605,51],[605,36],[871,15],[881,43],[911,40],[926,29],[921,0],[1671,0],[1671,444],[1410,445],[1240,449],[1115,446],[1004,442],[996,448],[919,446],[904,451],[824,449],[759,446],[738,428],[737,405],[726,402],[725,381],[718,381],[716,363],[711,380],[705,376],[698,383],[698,401],[663,402],[661,370],[656,345],[651,337],[649,313],[645,307],[642,269],[638,307],[633,312],[630,334],[623,341],[621,350],[600,346],[600,320],[595,323],[593,304],[589,328],[585,325],[581,298],[575,292],[575,272],[570,273],[566,239],[563,211],[559,240],[553,251],[548,260],[548,226],[544,221],[544,165],[540,160],[540,98],[548,74],[551,65],[531,68],[514,66],[503,66],[518,78],[522,99],[520,162],[516,170],[516,215],[502,210],[499,169],[494,162],[493,134],[488,128],[483,72],[478,126],[474,142],[472,181],[468,188],[466,211],[461,220],[459,197],[455,190],[452,158],[449,139],[446,114],[443,157],[439,176],[436,189],[434,223],[428,233],[428,271],[423,274],[420,254],[417,273],[410,267],[406,256],[404,229],[400,218],[397,170],[392,218],[387,236],[386,256],[379,254],[378,233],[374,251],[365,255],[350,265],[344,260],[341,246],[337,239],[334,216],[331,187],[327,213],[325,231],[320,237],[317,275],[309,275],[307,260],[302,270],[298,266],[296,252],[290,258],[286,253],[283,234],[278,232],[277,224],[266,225],[262,217],[258,227],[247,228],[244,217]],
            'clear_opening': [[1045,246],[1093,222],[1155,211],[1220,220],[1278,240],[1293,275],[1287,318],[1255,348],[1199,355],[1134,354],[1074,342],[1042,316],[1028,279]],
            'feather': 5, 'opening_feather': 32, 'inset': 2.0,
            'background_sigma': [60,32], 'fade_seconds': 8,
            'groups': [[380,170,180,85,2.6,10],[635,130,150,105,3.3,18],[826,242,170,105,2.7,26],
                       [1004,70,165,72,3.1,34],[1215,55,190,73,3.5,42],[1510,170,225,155,2.9,50],
                       [930,378,150,46,1.1,15],[1240,413,170,38,1.0,31],[1515,397,190,45,1.3,47]]},
        'weather': [
            {'name':'far_dust','polygon':[[791,490],[1045,492],[1190,497],[1410,493],[1671,490],[1671,560],[1460,554],[1320,556],[1120,544],[1010,548],[837,536],[813,516]],
             'feather':12,'seed':821,'speed':4.5,'optical_depth':.33,'max_opacity':.22,'color':[203,109,83],
             'gusts':[[880,522,115,10,.00,12],[1110,520,145,13,.006,27],[1410,524,145,14,-.012,44],[1670,525,125,11,-.009,55]]},
            {'name':'middle_dust','polygon':[[883,552],[1000,548],[1140,551],[1320,544],[1500,558],[1663,549],[1671,615],[1580,609],[1535,622],[1510,639],[1425,629],[1391,653],[1250,649],[1190,629],[1060,634],[937,616],[883,587]],
             'feather':13,'seed':143,'speed':7.3,'optical_depth':.27,'max_opacity':.18,'color':[193,103,77],
             'gusts':[[970,583,106,9,.02,9],[1140,609,118,9,.01,24],[1370,582,133,10,.008,40],[1550,603,112,12,-.04,52]]}],
        'weather_blockers': [
            [[1207,613],[1211,570],[1220,570],[1220,573],[1248,573],[1251,567],[1259,571],[1268,570],[1278,610],[1260,614],[1255,591],[1248,586],[1241,588],[1236,595],[1235,615]],
            [[1268,607],[1283,596],[1292,597],[1300,608],[1315,601],[1325,604],[1325,620],[1287,619]],
            [[1363,623],[1365,599],[1373,602],[1384,599],[1387,625]],
            [[1087,608],[1094,590],[1100,591],[1104,608]]],
        'lights': [
            {'name':'upper_dome','polygons':[[[490,231],[496,231],[497,251],[490,253]],[[498,234],[502,234],[503,252],[498,253]]], 'events':[[6.5,8.2,1.2,.58],[44,10,1.8,.44]],'glows':[[496,245,10,18,.14]]},
            {'name':'high_tower','polygons':[[[534,232],[539,233],[540,257],[534,257]]], 'events':[[20,12,1.7,.62]],'glows':[[536,246,8,17,.14]]},
            {'name':'west_room','polygons':[[[423,257],[429,258],[429,276],[423,276]]], 'events':[[55,11,1.4,.64],[29,8,1.2,.45]],'glows':[[426,268,8,12,.12]]},
            {'name':'east_arch','polygons':[[[560,338],[566,338],[567,350],[560,350]]], 'events':[[15,9,1.3,.57],[42,6,1.1,.4]],'glows':[[563,346,9,12,.15]]},
            {'name':'gallery_room','polygons':[[[386,440],[394,440],[395,449],[385,449]]], 'events':[[35,13,1.6,.68]],'glows':[[390,446,11,9,.16]]},
            {'name':'east_room','polygons':[[[644,414],[652,414],[652,425],[644,425]]], 'events':[[3,9,1.5,.5],[48,10,1.6,.6]],'glows':[[648,420,9,11,.13]]}],
        'lantern': {'core_polygon':[[41,308],[82,309],[83,402],[41,402]],
                    'wall_polygon':[[0,242],[132,240],[230,296],[224,609],[155,669],[1,649]],
                    'floor_polygon':[[0,805],[152,791],[313,821],[368,919],[266,940],[0,940]],
                    'wall_glow':[62,365,66,122], 'floor_glow':[122,861,150,56],
                    'modulation':[.045,.021,.015], 'brief_dip':[38.3,.34,.10,.07]},
        'knowledge_reuse': {
            'bank':'creative/ANIMATION_KNOWLEDGE_BANK.md',
            'selected_examples':[
                {'scene':'Basalt v6 / Cable v3','status':'accepted looks','reuse':'Recognizable source-cloud transport, exclusions in sampling and destination','remap':'New roof/fortress/opening silhouette and cloud parcels'},
                {'scene':'Saltline v5 / v7','status':'v5 accepted; v7 minute timing separate','reuse':'PeriodicDust/DustTransport optical transport at unchanged speed','remap':'Far plain and ruin-adjacent channels, new seeds and minute schedules'},
                {'scene':'Ringfall v9b / Floodplain v2','status':'accepted looks','reuse':'Whole-aperture light events with local spill','remap':'Six rooms and terrace lantern, main sanctuary window steady'},
                {'scene':'Empty Junction v1 sky code','status':'implemented, subsequent user dissatisfaction with overall activity','reuse':'Source residual parcel extraction, not its approval claim or coordinates','remap':'Signed cloud/rim residual, minute phases and protected luminous opening'}],
            'known_failures':['invisible cloud shimmer','planet fragments drifting from texture source','global time blending','dust disappearing late in loop','white cores and spill staying lit']},
        'review': {'approved':False,'user_feedback':None,'continuous_playback_inspected':False},
        'delivery': {'master_4k_video':None,'preview':None,'tracked_in_git':False}}
    target.write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
    print('Saved plan and frozen dependencies')

if __name__ == '__main__': main()
