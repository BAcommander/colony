from pathlib import Path
import json, shutil, hashlib
H=Path(__file__).parent; V1=H.parent/'spirewatch-animation-v1'
assert not (H/'scene-plan-v2.json').exists()
shutil.copytree(V1/'dependencies',H/'dependencies',ignore=shutil.ignore_patterns('__pycache__'))
code=(V1/'render_spirewatch.py').read_text().replace("scene-plan-v1.json","scene-plan-v2.json")
(H/'baseline.py').write_text(code,encoding='utf-8')
c=json.loads((V1/'scene-plan-v1.json').read_text());c['version']='v2'
c['status']='Implemented candidate; visual and numeric checks pending'
c['sky'].update(speed=2.1,strength=.94)
c['mist'].update(speed=.95,strength=.8)
c['water']['method']='Detail-preserving source ripple transport, no reconstructed blurred columns'
c['water']['polygons'] += [
 [[1109,537],[1167,540],[1219,545],[1218,555],[1174,550],[1109,544]],
 [[1509,759],[1592,780],[1668,799],[1668,824],[1580,810],[1509,794]],
 [[957,662],[980,658],[980,740],[958,738]],
]
c['windows']['facade_regions'] += [[356,102,392,175],[420,140,463,210],[622,313,641,346],[866,384,882,422],[1225,281,1240,324],[1290,359,1322,398],[1404,418,1420,444],[1560,480,1600,493],[1060,466,1095,481],[943,611,963,643],[1220,667,1264,713]]
c['windows']['count']=32
c['windows']['starts']=[float((7+i*13.7)%60) for i in range(32)]
c['windows']['holds']=[float(6+(i*1.31)%9) for i in range(32)]
c['windows']['floor']=.28
c['screen'].update(marker_strength=80,period=30)
c['tower']={'roi':[1200,24,1340,418],'events':[[2,13,'up'],[26,40,'down'],[45,57,'up']],'band_height':31,'strength':1.0}
c['transit']={'route':[[688,484],[790,504],[930,529],[1080,553],[1260,581],[1460,613],[1671,642]],'events':[[3,16,1],[26,40,-1],[46,59,1]],'carriages':3,'occluders':[[[975,543],[996,544],[996,565],[975,560]],[[1149,570],[1165,572],[1165,588],[1149,584]],[[1274,590],[1284,590],[1284,604],[1274,602]]]}
c['lightning']={'events':[{'time':9.4,'center':[956,155],'radius':[190,116],'strength':1.0,'seed':121},{'time':34.4,'center':[1473,158],'radius':[172,113],'strength':.8,'seed':127},{'time':52.4,'center':[704,143],'radius':[185,106],'strength':.9,'seed':134}],'duration':1.25,'style':'localized intracloud illumination and short partially obscured branches; exterior response, no full-frame flash'}
c['new_mist']={'regions':[[[644,340],[905,317],[1126,336],[1157,384],[960,425],[701,410]],[[1325,319],[1515,308],[1671,348],[1671,422],[1407,413]],[[696,436],[855,408],[1046,434],[1106,475],[965,478],[739,457]]],'strengths':[.17,.13,.1],'speeds':[4.0,2.8,1.7]}
c['optional_effects']={'transit':'Authorized lighted carriage interpretation of existing elevated route','lightning':'Explicitly requested','tower':'Explicitly requested up/down glow mapped to existing cyan strips'}
c['knowledge_reuse'].update(water='Source detail retained; bounded ripple transport with far-right calming from Shoreless',falls='Rebuilt moving source texture and irregular falling threads; visible landing spray',clouds='Transport with protected geometry plus separate valley/city mist, no roof-source contamination',screen='Readable original-map route and node events, no prominent waveform',lightning='Localized source-cloud illumination and exterior response; staggered minute events',tower='Existing emission strips only; travelling bright band and bounded spill')
c['baseline_sha256']=hashlib.sha256((H/'baseline.py').read_bytes()).hexdigest()
(H/'scene-plan-v2.json').write_text(json.dumps(c,indent=2)+'\n')
print('V2 source-bound configuration and preserved dependencies ready')
