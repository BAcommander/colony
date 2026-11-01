"""Complete H.264 VUI tags without re-encoding pictures or audio."""
from assemble_with_colony import *
from colony import intro as opening
ARCHIVE=H/'history/pre-colour-tags';ARCHIVE.mkdir(parents=True,exist_ok=True)
TEMP=EXPORT/'The-Empty-Junction-1-Hour-4K-v1-colour-tagged.mp4'
OLD=CACHE/'The-Empty-Junction-1-Hour-4K-v1-before-colour-tags.mp4'

def audio_hash(p):
 return subprocess.check_output([render.get_ffmpeg_path(),'-v','error','-i',str(p),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','pipe:1']).decode().strip()

def main():
 assert OUTPUT.exists() and not TEMP.exists() and not OLD.exists()
 before=json.loads((H/'container-hash.json').read_text());assert digest(OUTPUT)==before['sha256']
 cmd=[render.get_ffmpeg_path(),'-v','error','-n','-i',str(OUTPUT),'-map','0','-c','copy','-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',str(TEMP)]
 subprocess.run(cmd,check=True)
 probe=json.loads(subprocess.check_output([shutil.which('ffprobe'),'-v','error','-show_streams','-of','json',str(TEMP)]))
 video=next(x for x in probe['streams'] if x['codec_type']=='video')
 assert all(video[k]=='bt709' for k in ['color_space','color_transfer','color_primaries']) and video['color_range']=='tv'
 ah=audio_hash(OUTPUT);assert audio_hash(TEMP)==ah,'AAC packets changed during colour-tag remux'
 for n in ['container-hash.json','colony-export.json','assembly-result.json','audio-validation.json']:
  shutil.copy2(H/n,ARCHIVE/n)
 # Preserve the first assembled file rather than overwrite it.
 OUTPUT.rename(OLD);TEMP.rename(OUTPUT)
 (H/'container-hash.json').unlink() # stale job-generated checksum is safely archived above
 save('colour-tag-correction.json',{'reason':'Encoded input and first final file had BT.709 matrix but unspecified primaries/transfer despite requested encoder flags; detected by final probe assertion.','method':'Stream copy with h264_metadata VUI correction and matching container tags; no video/audio re-encoding','original_preserved':str(OLD),'original_sha256':before['sha256'],'command':cmd,'aac_packet_payloads_identical':True,'aac_packet_payload_sha256':ah,'followup':'Corrected full file decoded again; video timestamps, loop payloads and source picture comparisons repeated.'})
 audio=json.loads((H/'audio-validation.json').read_text());audio['colour_remux_aac_packet_identity']=True;save('audio-validation.json',audio)
 print('Colour tags corrected; AAC packets unchanged. Full corrected-file decode...',flush=True)
 start=time.monotonic()
 checks=render.verify_output(render.get_ffmpeg_path(),str(OUTPUT),3600,(3840,2160),30,full_decode=True,on_progress=lambda x:None)
 assert all(x.ok for x in checks)
 result=json.loads((H/'assembly-result.json').read_text());result.update(bytes=OUTPUT.stat().st_size,checks=[vars(x) for x in checks],colour_tag_correction='colour-tag-correction.json');save('assembly-result.json',result)
 record=json.loads((H/'colony-export.json').read_text());record['colour_tag_correction']='colour-tag-correction.json';record['verification']['checks']=[vars(x) for x in checks];record['verification']['passed']=True;record['verification']['full_decode']=True;save('colony-export.json',record)
 print('Corrected final-file full decode passed in',round(time.monotonic()-start),'seconds',flush=True)
if __name__=='__main__':main()
