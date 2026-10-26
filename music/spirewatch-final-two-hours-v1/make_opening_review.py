"""Preview the same cached actual Colony opening while the long MP4 finalizes."""
from assemble_with_colony import *
ff=render.get_ffmpeg_path();info=render.probe_video(ff,str(VIDEO))
render._prepared=render.Prepared(str(CACHE),render._file_key(str(VIDEO)),info,render.color_tags_for(info),str(VIDEO),60.0,info)
render.LOOP_CRF=0;render.LOOP_PRESET='veryfast'
result=render.preview_opening(str(VIDEO),[str(AUDIO)],str(H/'Spirewatch-opening-review-25s-4K.mp4'),crossfade=0,
    intro=IntroSettings('Spirewatch',True),overlay_mode=render.OVERLAY_OFF,match_loudness=False,on_status=lambda s:print(s,flush=True))
assert result.verified and all(c.ok for c in result.checks) and result.duration==25
save('opening-review.json',{'path':result.output,'sha256':digest(result.output),'seconds':25,'dimensions':[3840,2160],'same_cached_opening_as_final':True,'same_intro_audio_graph':True,'colony_full_decode_passed':True})
print(result.output,flush=True)
