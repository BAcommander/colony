"""Keep the brighter purple fixtures on the photographed distant pipe face."""
from pathlib import Path
import json,shutil
H=Path(__file__).resolve().parent;A=H/'history'/'pipe-mount-alignment-study';assert not A.exists();A.mkdir(parents=True)
for name in ['scene-plan-v4.json','analytic-validation.json','preview-validation.json','isolated-pipeline-validation.json','far-pipe-alignment-review.png','pipe-face-profile-study.json']:
 shutil.copy2(H/name,A/name)
for p in list(H.glob('sample-*.png'))+list(H.glob('preview-size-*.png'))+list(H.glob('decoded-0*.png')):shutil.copy2(p,A/p.name)
for name in ['deepwell-v4-pipeline-roundtrip-20s.mp4','Deepwell-v4-preview-20s.mp4','Deepwell-v4-three-loops-60s.mp4']:
 src=(H/name).resolve();assert src.is_relative_to(H.resolve());shutil.move(str(src),str(A/name))
c=json.loads((H/'scene-plan-v4.json').read_text());pc=c['pipeline_lights']
pc['route']=[[876,324.8],[879,324.5],[899,322.1],[940,317.5],[960,315.5],[981,312.7],[1000,310.1],[1050,304.2],[1100,298.3],[1150,292.5],[1200,288.0],[1250,282.0],[1300,276.0],[1350,270.0],[1390,266.5]]
pc['tube_outline']=[[876,321.7],[899,319.3],[940,314.7],[960,312.7],[981,309.8],[1000,305.4],[1050,300.1],[1100,293.9],[1150,288.3],[1200,282.9],[1250,276.0],[1300,271.1],[1350,265.0],[1392,261.3],[1392,278.0],[1350,280.6],[1300,287.0],[1250,291.2],[1200,297.4],[1150,301.0],[1100,306.2],[1050,311.2],[1000,316.2],[981,318.3],[960,318.2],[940,320.4],[899,324.8],[876,327.0]]
(H/'scene-plan-v4.json').write_text(json.dumps(c,indent=2)+'\n')
(A/'README.txt').write_text('Internal candidate, not delivered/approved. Brighter/larger purple segments exposed approximation in the distant route: the first x879 centre was y327.55, on the pale area below the tube, while the dark pipe face is around y323-326. Correct its centre to y324.5 and x899 to y322.1, refine neighbouring far-face coverage inward and retain the remainder. Source pixel profiles and normal/close decoded stills support this geometric correction. The lamp is now on darker metal and reads as emitted light rather than a coloured patch below the edge. Steam, colour, timing and other layers are unchanged. Prior movies/checks preserved; rerender only pipeline isolation and full composite/repeats.\n')
print('Far indicator mounts fitted to photographed metal; prior candidate preserved.')
