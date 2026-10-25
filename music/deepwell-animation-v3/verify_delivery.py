"""Direct colour controls, scoped v2 regression and exact previous delivery preservation."""
from render_deepwell_v3 import *
s=DeepwellV3();reference=previous.DeepwellV2();times=[0,4,8,12,16,19+29/30]
retained=[k for k in reference.layer_masks if k!='lights'];regression={}
for name in retained:
 for t in times:assert np.array_equal(s.frame(t,name),reference.frame(t,name)),('Retained layer changed',name,t)
 regression[name]={'states_seconds':times,'all_pixels_exact':True}
authority=(s.old_window_mask>0)|s.layer_masks['lights']
for name in ['coffee_steam','tank_steam_near','tank_steam_middle','tank_steam_far','pipeline_lights']:authority|=s.layer_masks[name]
for t in times:assert np.array_equal(s.frame(t)[~authority],reference.frame(t)[~authority]),('Unrelated composite changed',t)
preview=json.loads((H/'preview-validation.json').read_text());assert preview['fingerprint']==s.fingerprint()
vf='scale=1280:720:flags=lanczos:in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p'
frames=[0,1,119,120,239,240,359,360,479,480,598,599];raw=b''.join(s.frame(i/30).tobytes() for i in frames)
expected=subprocess.run(['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1672x941','-r','30','-i','pipe:0','-vf',vf,'-f','rawvideo','-pix_fmt','yuv420p','pipe:1'],input=raw,stdout=subprocess.PIPE,check=True).stdout
select='select='+ '+'.join('eq(n\\,'+str(i)+')' for i in frames)
actual=subprocess.run(['ffmpeg','-v','error','-i',str(H/'Deepwell-v3-preview-20s.mp4'),'-vf',select,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','yuv420p','pipe:1'],stdout=subprocess.PIPE,check=True).stdout
assert expected==actual and len(actual)==len(frames)*1280*720*3//2,'Decoded preview differs from direct native YUV'
isolates=[]
for group in ['windows','coffee','tank_steam','pipeline']:
 d=json.loads((H/f'isolated-{group}-validation.json').read_text());assert d['fingerprint']==s.fingerprint();isolates+=d['clips']
save('isolated-validation.json',{'fingerprint':s.fingerprint(),'clips':isolates,'user_approved':False})
old=H.parent/'deepwell-animation-v2';manifest=json.loads((old/'package-manifest.json').read_text());count=0
for name,data in manifest['files'].items():
 assert digest(old/name)==data['sha256'],('V2 changed',name);count+=1
for name,expected_hash in json.loads((H/'v2-snapshot-manifest.json').read_text()).items():assert digest(S/name)==expected_hash,('V2 snapshot changed',name)
save('direct-render-validation.json',{'fingerprint':s.fingerprint(),'retained_v2_layers':regression,'composite_outside_change_authority_exact_at':times,'direct_native_to_decoded_yuv_match_frames':frames,'all_selected_yuv_bytes_exact':True,'all_v2_manifest_files_exact':True,'v2_preserved_file_count':count,'v2_manifest_sha256':digest(old/'package-manifest.json'),'snapshot_hashes_exact':True,'all_rendered_source_frames_assert':'Window frames/stone/steady pane, explicit mullions and cup/tank/pipe/support guards, excluding only the user-authorized pipe indicator mask.','inspection':'Native source, masks, bright-core/all-dim close-ups, full-size temporal and selected decoded stills. Continuous playback not claimed.','user_approved':False})
print('Twelve retained v2 layers and scoped composites are exact; twelve decoded pictures match direct native YUV;',count,'v2 files preserved.',flush=True)
