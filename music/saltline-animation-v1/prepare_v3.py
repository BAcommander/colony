from pathlib import Path
import json
H=Path(__file__).resolve().parent
c=json.loads((H/'scene-plan-v2.json').read_text());c['trial_version']='v3';c['version']='v3'
c['previous_feedback']={'date':'2026-09-29','verbatim':"right i can't see any dust man on either, ive increase your effort level to high, please stop wasting my time",'scope':'V2 near/far dust rejected as unreadable; replace method'}
c['status']='Textured ground gusts with optical extinction; foreground road near dust; review pending'
c['mask_geometry']['near_dust']={'include':[[[570,940],[648,880],[857,799],[1087,748],[1349,697],[1489,659],[1596,648],[1671,704],[1671,777],[1540,821],[1270,815],[1085,851],[914,915],[868,940]]], 'exclude':[[[665,590],[969,589],[1081,623],[1083,749],[999,771],[664,761]],[[1125,695],[1145,695],[1150,751],[1120,751]],[[1130,706],[1360,612],[1400,651],[1197,727]],[[1320,830],[1460,810],[1535,856],[1574,905],[1410,940],[1300,940]]]}
c['feather']['near_dust']=16;c['feather']['far_dust']=10
def gust(x,y,w,h,slope=0,phase=0,strength=1):return {'x':x,'y':y,'width':w,'height':h,'route_slope':slope,'phase':phase,'strength':strength}
c['far_dust']={'method':'textured_gusts','speed':20,'lifetime':10,'optical_depth':1.15,'max_opacity':.56,'seed':317,'color':[173,112,74],'gusts':[gust(786,437,77,15,-.015),gust(950,456,86,18,-.01,.5,.85),gust(4,451,66,14,0,.2,.65)]}
c['near_dust']={'method':'textured_gusts','speed':38,'lifetime':10,'optical_depth':1.0,'max_opacity':.60,'seed':971,'color':[245,188,120],'gusts':[gust(979,835,130,30,-.19),gust(1321,752,106,24,-.09,.5,.8),gust(695,907,87,25,-.32,.2,.7)]}
p=H/'scene-plan-v3.json';assert not p.exists();p.write_text(json.dumps(c,indent=2)+'\n')
