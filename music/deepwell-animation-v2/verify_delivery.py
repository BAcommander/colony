"""Colour-aware direct picture checks, retained-layer controls and preservation."""
from render_deepwell_v2 import *
s=DeepwellV2();vf='scale=1280:720:flags=lanczos:in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p'
def direct_check(path,frames,layer=None):
 raw=b''.join(s.frame(i/30,layer).tobytes() for i in frames)
 expected=subprocess.run(['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1672x941','-r','30','-i','pipe:0','-vf',vf,'-f','rawvideo','-pix_fmt','yuv420p','pipe:1'],input=raw,stdout=subprocess.PIPE,check=True).stdout
 select='select='+ '+'.join('eq(n\\,'+str(i)+')' for i in frames)
 actual=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-vf',select,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','yuv420p','pipe:1'],stdout=subprocess.PIPE,check=True).stdout
 assert actual==expected and len(actual)==len(frames)*1280*720*3//2,(path,'direct native YUV mismatch')
 return {'frames':frames,'all_yuv_bytes_exact':True,'sha256':digest(path)}
frames=[0,1,119,120,239,240,359,360,479,480,598,599]
preview=json.loads((H/'preview-validation.json').read_text());assert preview['fingerprint']==s.fingerprint()
results={'preview':direct_check(H/'Deepwell-v2-preview-20s.mp4',frames)}
old=json.loads((H/'history'/'soft-weather-study'/'isolated-validation.json').read_text());refined=json.loads((H/'isolated-atmosphere-validation.json').read_text());assert refined['fingerprint']==s.fingerprint()
clips=refined['clips'][:]
for name in ['water','habitation']:
 path=H/f'deepwell-v2-{name}-isolated-8s.mp4';item=next(q for q in old['clips'] if q['path']==path.name);assert digest(path)==item['sha256']
 results[name]=direct_check(path,[0,120,239],name);item['retained_from']='history/soft-weather-study/isolated-validation.json';item['current_config_direct_native_yuv_controls']=results[name];clips.append(item)
sky_record=json.loads((H/'history'/'support-occlusion-fix'/'isolated-refined-weather-validation.json').read_text());path=H/'deepwell-v2-sky-isolated-8s.mp4';item=next(q for q in sky_record['clips'] if q['path']==path.name);assert digest(path)==item['sha256']
results['sky']=direct_check(path,[0,120,239],'sky');item['retained_from']='history/support-occlusion-fix/isolated-refined-weather-validation.json';item['current_config_direct_native_yuv_controls']=results['sky'];clips.append(item)
write_json('isolated-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'retained_layers_explanation':'Sky/water/habitation are unchanged after the focused mineral-drift support occlusion fix. Original full decode records/hashes retained and direct native/YUV controls verify final-config output compatibility. Only atmosphere was rerendered after that fix.','user_approved':False})
v1=H.parent/'deepwell-animation-v1';manifest=json.loads((v1/'package-manifest.json').read_text());verified=[]
for name,item in manifest['files'].items():
 p=v1/name;assert p.exists() and digest(p)==item['sha256'],('V1 changed',name);verified.append(name)
for name,expected in json.loads((H/'baseline-snapshot-manifest.json').read_text()).items():assert digest(B/name)==expected,('Baseline snapshot changed',name)
# Source structures do not move. Pipeline is also excluded from every new air
# mask, and remains byte-identical even in full composite source frames.
for t in [0,4,8,12,16,19+29/30]:assert np.array_equal(s.frame(t)[s.pipeline],s.base[s.pipeline]),('Pipeline changed',t)
write_json('direct-render-validation.json',{'fingerprint':s.fingerprint(),'direct_native_yuv_controls':results,'pipeline_source_pixels_exact_at':[0,4,8,12,16,19+29/30],'v1_preserved_file_count':len(verified),'v1_all_manifest_files_byte_identical':True,'v1_manifest_sha256':digest(v1/'package-manifest.json'),'baseline_snapshot_all_hashes_exact':True,'planet_model':'Underlying source body/limb coordinates fixed. Foreground cloud opacity changes source colour only; no planet remap/rotation and no planet in advected texture source.','user_approved':False,'inspection':'Source, masks, normal-size native/decoded temporal stills and local crop comparisons. No continuous playback claim.'})
print('Twelve preview pictures and retained layer controls match direct native YUV; all',len(verified),'v1 files remain exact.',flush=True)
