"""Actual-strength replacements for the two affected isolated diagnostics."""
from render_farpoint_v4 import FarpointMinute,H,save,encode,verify
s=FarpointMinute();clips=[]
class Excerpt:
 config=s.config
 def frame(self,t,only=None,prototype=False):return s.frame(t+9,only,prototype)
for layer in ['stars_reflections','habitation']:
 path=H/f'{layer}-v4-corrected-isolated-8s.mp4'
 item=encode(Excerpt(),path,8,layer,True);item['source_start_seconds']=9
 item['validation'],_=verify(s,path,240,False);clips.append(item)
save('corrected-isolated-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'change':'Reflection emitter mask excludes surrounding dark glass while retaining white cores. Initial diagnostic renderer preserved separately.','user_approved':False})
