"""Check selected decoded delivery pictures against direct native-to-YUV renders."""
from render_deepwell import *
s=Deepwell();indices=[0,1,119,120,239,240,359,360,479,480,598,599]
vf='scale=1280:720:flags=lanczos:in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p'
raw=b''.join(s.frame(i/30).tobytes() for i in indices)
expected=subprocess.run(['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1672x941','-r','30','-i','pipe:0','-vf',vf,'-f','rawvideo','-pix_fmt','yuv420p','pipe:1'],input=raw,stdout=subprocess.PIPE,check=True).stdout
select='select='+ '+'.join('eq(n\\,'+str(i)+')' for i in indices)
actual=subprocess.run(['ffmpeg','-v','error','-i',str(H/'Deepwell-v1-preview-20s.mp4'),'-vf',select,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','yuv420p','pipe:1'],stdout=subprocess.PIPE,check=True).stdout
assert actual==expected,'Decoded YUV differs from direct native rendering'
assert len(actual)==len(indices)*1280*720*3//2
delivery=json.loads((H/'preview-validation.json').read_text());assert delivery['fingerprint']==s.fingerprint(),'Frozen delivery fingerprint changed'
# Confirm the shorter wave study did not alter the secondary layers. The
# original 8s clips retain their original full decode records and fingerprint.
old=json.loads((H/'history'/'broad-water-study'/'isolated-validation.json').read_text())
unchanged={}
for layer in ['sky','screen']:
 p=H/f'deepwell-{layer}-isolated-8s.mp4';entry=next(v for v in old['clips'] if v['layer']==layer);assert digest(p)==entry['sha256']
 frames=[0,120,239];src=b''.join(s.frame(i/30,layer).tobytes() for i in frames)
 exp=subprocess.run(['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1672x941','-r','30','-i','pipe:0','-vf',vf,'-f','rawvideo','-pix_fmt','yuv420p','pipe:1'],input=src,stdout=subprocess.PIPE,check=True).stdout
 sel='select='+ '+'.join('eq(n\\,'+str(i)+')' for i in frames)
 act=subprocess.run(['ffmpeg','-v','error','-i',str(p),'-vf',sel,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','yuv420p','pipe:1'],stdout=subprocess.PIPE,check=True).stdout
 assert act==exp,(layer,'retained isolated changed')
 unchanged[layer]={'sha256':digest(p),'direct_native_yuv_match_frames':frames,'same_layer_output_with_fine_water_config':True}
write_json('direct-render-validation.json',{'fingerprint':s.fingerprint(),'preview_direct_native_to_decoded_yuv_match_frames':indices,'all_selected_yuv_bytes_exact':True,'retained_secondary_isolates':unchanged,'assistant_inspection':'Source, masks, native temporal stills, water scale comparison, isolated cloud temporal crops and selected decoded stills. Continuous playback not claimed.','user_artistic_approval':False})
print('Twelve delivered pictures and six retained isolated pictures match direct native renders exactly',flush=True)
