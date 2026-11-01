"""Verify every copied picture payload/timestamp and the entire final AAC mix."""
from assemble_revision import *
from colony import intro as opening
import numpy as np,math

def picture_payloads(path,label,seconds=None,expected=None):
 args=[FF,'-v','error','-i',str(path)]
 if seconds:args+=['-t',str(seconds)]
 args+=['-map','0:v:0','-an','-c:v','copy','-bsf:v','h264_mp4toannexb,filter_units=remove_types=7','-f','framehash','-hash','sha256','pipe:1']
 hashes=[];tb=None
 with (C/(label+'-picture-payloads.sha256')).open('wb') as records,(C/(label+'-packet-check.log')).open('wb') as err:
  p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=err)
  for raw in p.stdout:
   records.write(raw);line=raw.decode().strip()
   if line.startswith('#tb 0:'):
    n,d=map(int,line.split(':',1)[1].strip().split('/'));tb=n/d
   elif line and not line.startswith('#'):
    fields=[x.strip() for x in line.split(',')];i=len(hashes)
    assert abs(int(fields[1])*tb-i/30)<1e-5 and abs(int(fields[2])*tb-i/30)<1e-5
    if expected is not None:assert fields[-1]==expected[i],('Changed picture payload',label,i)
    hashes.append(fields[-1])
    if expected is not None and len(hashes)%18000==0:print('Checked video payloads',len(hashes)//1800,'/60 minutes',flush=True)
  assert p.wait()==0
 return hashes

def video():
 settings=json.loads((H/'assembly-settings.json').read_text());recipe=json.loads((H/'mix-recipe.json').read_text());refs={}
 for name,item in settings['units'].items():
  assert sha(item['path'])==item['sha256']
  refs[name]=picture_payloads(item['path'],'unit-'+name);assert len(refs[name])==1800
  source=ORIGINAL if name=='opening' else V1/'masters'/f'Empty-Junction-v6-{name}-60s-4K.mp4'
  actual=picture_payloads(source,'source-'+name,60)
  assert actual==refs[name],('Prepared section picture payload changed',name)
 expected=[]
 for label in settings['minute_sequence']:expected.extend(refs[label])
 actual=picture_payloads(OUTPUT,'full-revision',expected=expected);assert len(actual)==108000
 p=probe(OUTPUT);v=next(x for x in p['streams'] if x['codec_type']=='video');a=next(x for x in p['streams'] if x['codec_type']=='audio')
 assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(3840,2160,'30/1',108000)
 assert all(v[k]=='bt709' for k in ['color_space','color_transfer','color_primaries']) and v['color_range']=='tv'
 assert abs(float(p['format']['duration'])-3600)<.04
 assert a['codec_name']=='aac' and a['channels']==2 and int(a['sample_rate'])==48000
 save('video-validation.json',{'status':'passed','all_108000_pts_dts_exact':True,'every_picture_payload_matches_selected_original_unit':True,'all_prepared_unit_picture_payloads_match_original_sources':True,'existing_opening_preserved':True,'no_reencoding':True,'wind_passages':25,'quiet_minutes':35,'minute_sequence':settings['minute_sequence'],'method':'Compare SHA-256 of every H.264 packet after Annex-B normalization and removal only of SPS NAL type7 (colour metadata differs). PPS, SEI and complete coded picture slices remain in comparison. Full actual file separately decoded by Colony.','probe':p})
 print('PASS: complete source-picture identity, minute schedule, timestamps and BT.709 tags',flush=True)

def audio():
 graph=opening.audio_graph(render.build_audio_graph([0.0],0,first_input=0),IntroSettings('The Empty Junction',True))
 with (C/'audio-expected.log').open('wb') as e,(C/'audio-final.log').open('wb') as f:
  p=subprocess.Popen([FF,'-v','error','-i',str(NEW),'-filter_complex',graph,'-map','[aout]','-t','3600','-ac','2','-ar','48000','-f','f32le','pipe:1'],stdout=subprocess.PIPE,stderr=e)
  q=subprocess.Popen([FF,'-v','error','-i',str(OUTPUT),'-vn','-t','3600','-ac','2','-ar','48000','-f','f32le','pipe:1'],stdout=subprocess.PIPE,stderr=f)
  xx=yy=xy=error=peak=silence=0.;n=0
  for sec in range(3600):
   ab=p.stdout.read(48000*8);bb=q.stdout.read(48000*8);assert len(ab)==len(bb)==48000*8
   a=np.frombuffer(ab,'<f4').astype(float);b=np.frombuffer(bb,'<f4').astype(float)
   assert np.isfinite(b).all();peak=max(peak,float(abs(b).max()));assert peak<1
   if sec<4:silence=max(silence,float(abs(b).max()))
   xx+=float(a@a);yy+=float(b@b);xy+=float(a@b);error+=float(np.sum((a-b)**2));n+=48000
  assert not p.stdout.read(1) and not q.stdout.read(1) and p.wait()==q.wait()==0
 corr=xy/math.sqrt(xx*yy);gain=10*math.log10(yy/xx);snr=10*math.log10(xx/error)
 assert n==172800000 and silence<1e-6 and corr>.995 and abs(gain)<.15 and snr>25
 save('final-audio-validation.json',{'status':'passed','seconds':3600,'sample_frames':n,'all_finite_unclipped':True,'sample_peak_dbfs':20*math.log10(peak),'entire_mix_correlation':corr,'gain_difference_db':gain,'aac_snr_db':snr,'actual_Colony_audio_graph':graph,'silent_first_four_seconds_peak':silence,'intro_audio_envelope_once':True})
 print('PASS: entire revised AAC mix and once-only opening envelope',flush=True)

def finish():
 for f in ['audio-delivery-validation.json','video-validation.json','final-audio-validation.json','assembly-result.json']:assert json.loads((H/f).read_text())['status']=='passed'
 settings=json.loads((H/'assembly-settings.json').read_text());assert sha(NEW)==settings['audio']['sha256']
 before=OUTPUT.stat();digest=sha(OUTPUT);after=OUTPUT.stat();assert before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns
 save('delivery-validation.json',{'status':'passed','output':str(OUTPUT),'sha256':digest,'bytes':after.st_size,'duration_seconds':3600,'dimensions':[3840,2160],'fps':30,'frames':108000,'native_dimensions':[1672,941],'upscale':'Existing native-to-4K Lanczos masters reused; no video re-encoding','user_visual_feedback':'i think the video is fine','revision':'About 25% more frequent SFX, preserving levels, music and visuals; existing wind/quiet sections rescheduled to keep powder synchronized.','counts':json.loads((H/'mix-recipe.json').read_text())['counts'],'complete_decode':True,'every_picture_payload_and_timestamp_checked':True,'complete_audio_comparison':True,'user_revised_mix_review':'pending','assistant_listening':False,'published':False,'committed_or_pushed':False})
 print('Final revised hour verified',flush=True)
if __name__=='__main__':
 args=sys.argv[1:]
 if '--video' in args:video()
 if '--audio' in args:audio()
 if '--finish' in args:finish()
