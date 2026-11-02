"""Copy verified Deepwell pictures and mux the approved replacement soundtrack."""
from pathlib import Path
import subprocess,json,hashlib,math
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[1];D=H/'video-v2';D.mkdir(exist_ok=True)
C=H/'cache';E=R/'exports/12-deepwell-station'
OLD=E/'Deepwell-Station-1-Hour-4K-v1.mp4'
AUDIO=E/'Deepwell-Station-1-Hour-claim-rework-v1.flac'
OUT=E/'Deepwell-Station-1-Hour-4K-v2-audio-revised.mp4'
FF='ffmpeg';PROBE='ffprobe';SR=48000
def save(n,x):(D/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(16*1024**2),b''):h.update(b)
 return h.hexdigest()
def run(args):return subprocess.run(args,capture_output=True,check=True).stdout
def rows(path):
 for line in path.read_text().splitlines():
  if line and not line.startswith('#'):yield [s.strip() for s in line.split(',')]

def main():
 oldrecord=json.loads((R/'music/deepwell-final-hour-v1/delivery-validation.json').read_text())
 audio_record=json.loads((H/'replacement-v1/validation.json').read_text())
 expected_audio=next(x['sha256'] for x in audio_record['output_files'] if x['path']==str(AUDIO))
 print('Verifying original video and replacement audio fingerprints...',flush=True)
 assert sha(OLD)==oldrecord['sha256'];assert sha(AUDIO)==expected_audio
 oldgraph=json.loads((R/'music/deepwell-final-hour-v1/audio-validation.json').read_text())['source_expected_graph']
 graph=oldgraph.replace('[0:a:0]','[1:a:0]')
 save('user-approval.json',{'date':'2026-11-02','verbatim':"yeah that sounds good, lets update the full deepwell video with the new audio so i can reupload it",'scope':'Accepts replacement excerpt and authorizes a revised full video for user reupload','audio_sha256':expected_audio})
 cmd=[FF,'-hide_banner','-nostats','-v','warning','-n','-i',str(OLD),'-i',str(AUDIO),'-filter_complex',graph,'-map','0:v:0','-map','[aout]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t','3600','-map_metadata','0','-movflags','+faststart','-progress',str(C/'video-mux-progress.txt'),str(OUT)]
 save('assembly-settings.json',{'original_video':str(OLD),'original_video_sha256':oldrecord['sha256'],'audio':str(AUDIO),'audio_sha256':expected_audio,'output':str(OUT),'audio_filter':graph,'video_processing':'Stream copy; no re-encoding','opening':'Existing picture opening retained; original Colony audio graph applied once to unfaded replacement soundtrack','command':cmd,'copyright_clearance':'Not tested; user must run fresh upload checks'})
 print('Muxing approved replacement audio with unchanged video...',flush=True)
 with (C/'video-mux.log').open('wb') as log:subprocess.run(cmd,stdout=log,stderr=log,check=True)
 probe=json.loads(run([PROBE,'-v','error','-show_streams','-show_format','-of','json',str(OUT)]))
 v=next(x for x in probe['streams'] if x['codec_type']=='video');a=next(x for x in probe['streams'] if x['codec_type']=='audio')
 assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(3840,2160,'30/1',108000)
 assert abs(float(probe['format']['duration'])-3600)<.04
 assert all(v[x]=='bt709' for x in ['color_space','color_transfer','color_primaries']) and v['color_range']=='tv'
 assert a['codec_name']=='aac' and a['sample_rate']=='48000' and a['channels']==2
 print('Comparing all108,000 video packets and timestamps with the verified original...',flush=True)
 packets=C/'v2-video-packets.sha256'
 with packets.open('wb') as out:subprocess.run([FF,'-v','error','-i',str(OUT),'-map','0:v:0','-c:v','copy','-f','framehash','-hash','sha256','pipe:1'],stdout=out,check=True)
 previous=R/'music/deepwell-final-hour-v1/verification-cache/all-video-packets.sha256'
 original=list(rows(previous));current=list(rows(packets));assert len(original)==len(current)==108000
 assert original==current,'Video packet payload/timing changed'
 metadata=lambda p:[s for s in p.read_text().splitlines() if s.startswith(('#tb','#extradata'))]
 assert metadata(previous)==metadata(packets)
 save('video-validation.json',{'status':'passed','video_packets_and_pts_dts_identical':108000,'codec_extradata_and_timebase_identical':True,'visuals_and_opening_identical':True,'original_full_decode_validation_inherited':'Exact packets/extradata/timestamps match the hash-verified previously fully decoded video. No redundant full4K decode performed.','probe':probe})
 print('Comparing the complete AAC soundtrack against approved audio and opening fade...',flush=True)
 p=subprocess.Popen([FF,'-v','error','-i',str(AUDIO),'-filter_complex',oldgraph,'-map','[aout]','-t','3600','-ar','48000','-ac','2','-f','f32le','pipe:1'],stdout=subprocess.PIPE)
 q=subprocess.Popen([FF,'-v','error','-i',str(OUT),'-vn','-t','3600','-ar','48000','-ac','2','-f','f32le','pipe:1'],stdout=subprocess.PIPE)
 energy=observed=cross=error=0.;peak=silent=0.;patch_checks=[]
 for sec in range(3600):
  raw=p.stdout.read(SR*8);got=q.stdout.read(SR*8);assert len(raw)==len(got)==SR*8
  x=np.frombuffer(raw,'<f4').astype(float);y=np.frombuffer(got,'<f4').astype(float)
  assert np.isfinite(x).all() and np.isfinite(y).all()
  xx=float(np.sum(x*x));yy=float(np.sum(y*y));xy=float(np.sum(x*y));ee=float(np.sum((x-y)**2))
  energy+=xx;observed+=yy;cross+=xy;error+=ee;peak=max(peak,float(abs(y).max()))
  if sec<4:silent=max(silent,float(abs(y).max()))
  if sec in [30,1194,1196,1200,1214,3540]:patch_checks.append({'second':sec,'expected_correlation':xy/math.sqrt(max(xx*yy,1e-30))})
 assert not p.stdout.read(1) and not q.stdout.read(1) and p.wait()==q.wait()==0
 corr=cross/math.sqrt(energy*observed);snr=10*math.log10(energy/error);gain=10*math.log10(observed/energy)
 assert corr>.995 and snr>25 and abs(gain)<.15 and silent<1e-6 and peak<1
 save('audio-validation.json',{'status':'passed','decoded_seconds':3600,'sample_frames_per_channel':172800000,'full_audio_correlation':corr,'encoding_snr_db':snr,'gain_difference_db':gain,'sample_peak_dbfs':20*math.log10(peak),'first4_seconds_peak':silent,'same_opening_audio_graph':oldgraph,'patch_diagnostics':patch_checks,'all_samples_finite_unclipped':True,'closing_fade_retained':True,'assistant_listening':False})
 print('Hashing finished revised video...',flush=True)
 digest=sha(OUT)
 save('delivery-validation.json',{'status':'passed','date':'2026-11-02','output':str(OUT),'sha256':digest,'bytes':OUT.stat().st_size,'seconds':3600,'dimensions':[3840,2160],'fps':30,'frames':108000,'video_packets_identical_to_original':True,'complete_audio_decode_and_recipe_comparison_passed':True,'replacement_occurrences':10,'audio_approval':'user-approval.json','source_audio_sha256':expected_audio,'original_preserved':True,'uploaded':False,'youtube_claim_check':'Pending on new upload; no clearance claimed','assistant_listening':False})
 print('PASS: revised one-hour4K upload file ready.',flush=True)
if __name__=='__main__':main()
