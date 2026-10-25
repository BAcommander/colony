"""Retained v3 controls, direct YUV pictures, round-trip evidence and preservation."""
from render_deepwell_v4 import *
s=DeepwellV4();reference=previous.DeepwellV3();times=[0,4,8,10,12,16,19+29/30]
changed=['coffee_steam','tank_steam_near','tank_steam_middle','tank_steam_far','pipeline_lights'];retained=[k for k in reference.layer_masks if k not in changed];controls={}
for name in retained:
 for t in times:assert np.array_equal(s.frame(t,name),reference.frame(t,name)),('Retained v3 layer changed',name,t)
 controls[name]={'seconds':times,'all_pixels_exact':True}
authority=np.zeros((s.h,s.w),bool)
for name in changed:authority|=s.layer_masks[name]|reference.layer_masks[name]
for t in times:assert np.array_equal(s.frame(t)[~authority],reference.frame(t)[~authority]),('Unrelated composite changed',t)
preview=json.loads((H/'preview-validation.json').read_text());assert preview['fingerprint']==s.fingerprint()
vf='scale=1280:720:flags=lanczos:in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p'
def direct_yuv(path,frames,group=None):
 raw=b''.join(s.frame(i/30,group).tobytes() for i in frames)
 expected=subprocess.run(['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1672x941','-r','30','-i','pipe:0','-vf',vf,'-f','rawvideo','-pix_fmt','yuv420p','pipe:1'],input=raw,stdout=subprocess.PIPE,check=True).stdout
 select='select='+ '+'.join('eq(n\\,'+str(i)+')' for i in frames)
 actual=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-vf',select,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','yuv420p','pipe:1'],stdout=subprocess.PIPE,check=True).stdout
 assert expected==actual and len(actual)==len(frames)*1280*720*3//2,(path,'Direct native YUV mismatch')
 return {'frames':frames,'all_yuv_bytes_exact':True}
frames=[0,1,119,120,239,240,299,300,359,360,479,480,598,599]
direct={'combined':direct_yuv(H/'Deepwell-v4-preview-20s.mp4',frames),'pipeline_full_roundtrip':direct_yuv(H/'deepwell-v4-pipeline-roundtrip-20s.mp4',[0,150,299,300,450,599],'pipeline')}
clips=[]
for group in ['coffee','tank_steam','pipeline']:
 record=json.loads((H/f'isolated-{group}-validation.json').read_text())
 if group=='pipeline':assert record['fingerprint']==s.fingerprint()
 else:
  item=record['clips'][0];assert digest(H/item['path'])==item['sha256']
  direct[group+'_retained_isolate']=direct_yuv(H/item['path'],[0,120,239],group)
  item['retained_before_pipe_mount_alignment']=True;item['original_render_fingerprint']=record['fingerprint'];item['final_config_direct_yuv_controls']=direct[group+'_retained_isolate']
 clips+=record['clips']
save('isolated-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'pipeline_test_covers_complete_20s_outward_and_return_motion':True,'user_approved':False})
v3=H.parent/'deepwell-animation-v3';manifest=json.loads((v3/'package-manifest.json').read_text());count=0
for name,item in manifest['files'].items():assert digest(v3/name)==item['sha256'],('V3 changed',name);count+=1
for name,expected_hash in json.loads((H/'v3-snapshot-manifest.json').read_text()).items():assert digest(S/name)==expected_hash,('Snapshot changed',name)
save('direct-render-validation.json',{'fingerprint':s.fingerprint(),'retained_v3_layers':controls,'scoped_composite_exact_at_seconds':times,'direct_native_yuv_controls':direct,'all_selected_yuv_bytes_exact':True,'pipeline_head_normalized_arc_at_0_5_10_15_20':{str(t):s.pipeline_head(t)[0] for t in [0,5,10,15,20]},'all_v3_manifest_files_exact':True,'v3_preserved_file_count':count,'v3_manifest_sha256':digest(v3/'package-manifest.json'),'snapshot_hashes_exact':True,'source_guards':'Inherited v3 frame/mullion/stone/steady pane, cup/tank and pipeline protection; only the explicitly changed vapor/pipe-emitter masks authorize new pixels.','inspection':'Native source, unamplified actual-conversion 720p samples, isolated decoded temporal stills and selected final decoded stills. Continuous playback not claimed.','user_approved':False})
print(len(retained),'retained v3 layers exact; combined and full pipe round-trip direct YUV controls passed;',count,'v3 files preserved.',flush=True)
