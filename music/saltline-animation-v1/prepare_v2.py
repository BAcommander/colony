from pathlib import Path
import json
H=Path(__file__).resolve().parent
c=json.loads((H/'scene-plan-v1.json').read_text());c['trial_version']='v2';c['version']='v2'
c['previous_feedback']={'date':'2026-09-29','verbatim':'i cant see any dust movement. near or far','scope':'Both v1b dust tests rejected as unreadable; no cloud approval inferred'}
c['status']='Wider source-mapped dust transport trial; awaiting normal-speed review'
blockers=[[[119,278],[272,278],[410,308],[489,473],[491,550],[450,605],[451,748],[120,769]],[[518,405],[634,404],[727,514],[727,586],[676,616],[665,692],[520,702]],[[995,478],[1088,477],[1128,550],[1112,625],[993,625]],[[881,522],[918,522],[924,601],[881,601]]]
c['mask_geometry']={
 'far_dust':{'include':[[[0,413],[1092,408],[1169,424],[1122,463],[1020,487],[929,487],[0,485]]],'exclude':blockers},
 'near_dust':{'include':[[[0,477],[991,477],[984,502],[931,538],[881,571],[860,590],[738,592],[515,628],[370,667],[0,691]]],'exclude':blockers}}
c['feather']['far_dust']=10;c['feather']['near_dust']=12
def sheet(x,y,w,h,phase=0,strength=1,slope=0):return {'x':x,'y':y,'width':w,'height':h,'phase':phase,'strength':strength,'slope':slope,'bend':h*.3}
c['far_dust']={'speed':12,'lifetime':10,'opacity':.38,'max_opacity':.40,'color':[242,211,174],'sheets':[sheet(749,430,88,9),sheet(877,458,95,12,.5,.9,-.025),sheet(1000,431,75,8,.2,.7),sheet(22,454,75,11,.35,.7)]}
c['near_dust']={'speed':24,'lifetime':10,'opacity':.42,'max_opacity':.46,'color':[238,195,147],'sheets':[sheet(742,508,62,13,0,1,-.045),sheet(744,550,76,16,.5,.85,-.04),sheet(5,591,70,19,.3,.8,-.09)]}
p=H/'scene-plan-v2.json';assert not p.exists();p.write_text(json.dumps(c,indent=2)+'\n')
