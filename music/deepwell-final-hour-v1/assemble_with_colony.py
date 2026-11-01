"""Assemble Deepwell Station with the preserved real Colony v3 intro export engine."""
from pathlib import Path
import sys,os,json,subprocess,hashlib,shutil,time
H=Path(__file__).resolve().parent;R=H.parents[1]
APP=Path('C:/dev/SpeedySlideShow')
SNAP=R/'creative/brand/intro-v3/tool-source-snapshot'
VIDEO=H/'masters/Deepwell-v4-60s-4K.mp4'
AUDIO=R/'exports/12-deepwell-station/Deepwell-Station-1-Hour-v1.flac'
EXPORT=R/'exports/12-deepwell-station';CACHE=EXPORT/'video-v1-assembly-cache'
OUTPUT=EXPORT/'Deepwell-Station-1-Hour-4K-v1.mp4'
sys.dont_write_bytecode=True
sys.path.insert(0,r'C:\AI\ComfyUI\venv\Lib\site-packages')
sys.path.insert(0,str(APP))
os.environ['IMAGEIO_FFMPEG_EXE']=shutil.which('ffmpeg') or 'ffmpeg'
import colony
colony.__path__.insert(0,str(SNAP/'colony'))
from colony import render
from colony.intro import IntroSettings
from app import exporter
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(16*1024**2),b''):h.update(chunk)
    return h.hexdigest()
def save(name,value):(H/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def main():
    assert not OUTPUT.exists(),'Preserve existing final video'
    assert Path(render.__file__).resolve()==(SNAP/'colony/render.py').resolve()
    implementation=json.loads((R/'creative/brand/intro-v3/implementation-verification.json').read_text())
    verified={}
    for entry in implementation['files']:
        rel=Path(entry['path']).relative_to(APP)
        p=SNAP/rel
        assert digest(p)==entry['sha256'],p
        verified[str(p)]=entry['sha256']
    validation=json.loads((H/'master-validation.json').read_text())
    assert validation['status']=='passed'
    vd=next(x for x in validation['files'] if x['file']==VIDEO.name)
    av=json.loads((R/'music/deepwell-production-2026-11-01/delivery-hour-v1/delivery-validation.json').read_text());assert av['status']=='passed'
    ar=next(x for x in av['outputs'] if x['path']==str(AUDIO))
    assert digest(VIDEO)==vd['sha256'] and digest(AUDIO)==ar['sha256']
    CACHE.mkdir(parents=True,exist_ok=True)
    ffmpeg=render.get_ffmpeg_path();info=render.probe_video(ffmpeg,str(VIDEO))
    assert info.size==(3840,2160) and info.duration==60 and info.fps==30
    assert shutil.disk_usage(EXPORT).free>80*1024**3,'Need room for final video and faststart work'
    # Reuse the verified clean unit verbatim. Only the first one-minute unit is encoded.
    render._prepared=render.Prepared(str(CACHE),render._file_key(str(VIDEO)),info,
        render.color_tags_for(info),str(VIDEO),60.0,info)
    # Job-local lossless opening encoder settings; no application source is edited.
    render.LOOP_CRF=0;render.LOOP_PRESET='veryfast'
    # Explicit VUI metadata prevents this FFmpeg build dropping primaries/transfer.
    original_encode_args=render._loop_encode_args
    def tagged_args(color):
        return original_encode_args(color)+['-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0']
    render._loop_encode_args=tagged_args
    intro=IntroSettings('Deepwell Station',fade_audio=True)
    settings={'tool':'Actual Colony renderer preserved with intro v3','renderer_path':str(Path(render.__file__)),'renderer_sha256':digest(render.__file__),'intro_verified_files':verified,'dependencies':{str(Path(exporter.__file__)):digest(exporter.__file__),str(APP/'colony/sfx.py'):digest(APP/'colony/sfx.py')},'local_installed_renderer_sha256':digest(APP/'colony/render.py'),'reason_for_snapshot':'Installed local source/executable predates the recorded intro release. Use verified v3 snapshot via package search path, retaining existing exporter/SFX dependencies. No installed tool file is modified.','video':{'path':str(VIDEO),'sha256':vd['sha256'],'native_source_dimensions':[1672,941],'output_dimensions':[3840,2160],'fps':30,'unit_seconds':60},'audio':{'path':str(AUDIO),'sha256':ar['sha256'],'seconds':3600,'gain_db':0,'match_loudness':False,'crossfade':0,'sfx':None,'closing_fade':'Existing soundtrack twenty-second closing fade retained'},'opening':intro.record(),'opening_encoder':{'crf':0,'preset':'veryfast','b_frames':0,'h264_vui_completion':'Job-local _loop_encode_args wrapper adds h264_metadata BT.709 TV; no application source edit','pixel_format':'yuv420p','color':'BT.709 TV'},'clean_units':'Original master stream-copied; source phase unchanged','output':str(OUTPUT),'expected_frames':108000,'expected_seconds':3600,'ffmpeg':ffmpeg,'ffmpeg_version':subprocess.run([ffmpeg,'-version'],stdout=subprocess.PIPE,check=True).stdout.decode().splitlines()[0]}
    save('assembly-settings.json',settings)
    previous=[-1,0,'Starting']
    def status(message):
        previous[2]=message;previous[0]=-1
        print(message,flush=True);save('assembly-progress.json',{'stage':message,'utc_epoch':time.time()})
    def progress(fraction,eta):
        pct=int(fraction*100);now=time.monotonic()
        if pct>=previous[0]+5 or now-previous[1]>25:
            item={'stage':previous[2],'stage_progress_percent':pct,'stage_eta_seconds':eta,'utc_epoch':time.time()}
            print(json.dumps(item),flush=True);save('assembly-progress.json',item);previous[:2]=[pct,now]
    result=render.render(str(VIDEO),[str(AUDIO)],str(OUTPUT),crossfade=0,overlay_mode=render.OVERLAY_OFF,
        match_loudness=False,full_decode=True,overwrite=False,intro=intro,on_status=status,on_progress=progress)
    assert result.output==str(OUTPUT) and result.verified and all(c.ok for c in result.checks)
    assert result.duration==3600 and (result.width,result.height,result.fps)==(3840,2160,30)
    assert result.gains_db==[0] and result.crossfade==0 and not result.overlay_times
    shutil.copy2(result.manifest,H/'colony-export.json')
    assert digest(VIDEO)==vd['sha256'] and digest(AUDIO)==ar['sha256']
    save('assembly-result.json',{'output':str(OUTPUT),'bytes':OUTPUT.stat().st_size,'duration_seconds':result.duration,'dimensions':[result.width,result.height],'fps':result.fps,'colony_full_decode_passed':True,'checks':[vars(c) for c in result.checks],'source_hashes_unchanged':True,'further_checks':'verify_final.py checks every video timestamp/loop payload, decoded source identity, opening stills and the complete audio envelope.'})
    print('Colony export and full decode complete; independent delivery checks next.',flush=True)
if __name__=='__main__':main()
