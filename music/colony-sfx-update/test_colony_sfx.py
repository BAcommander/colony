"""Real FFmpeg tests: ambience must fade, become silent and preserve music level."""
from dataclasses import replace
import json
import subprocess
import numpy as np
import pytest
from colony import render as R
from colony.sfx import SfxSettings, mix_graph, prepare_loop


def ff(args):
    return subprocess.run([R.get_ffmpeg_path(), '-v', 'error', '-y', *args],
                          capture_output=True, check=True).stdout


@pytest.fixture
def sound(tmp_path):
    p = str(tmp_path/'rain.wav')
    ff(['-f','lavfi','-i','sine=frequency=1000:sample_rate=48000:duration=3',
        '-ac','2',p])
    return p


def samples(settings, tmp_path, duration=12):
    loop = str(tmp_path/'loop.wav')
    prepare_loop(R.get_ffmpeg_path(), settings, loop, 3)
    graph = mix_graph(R.build_audio_graph([0], 0, first_input=0), settings, duration, 1)
    raw = ff(['-f','lavfi','-i',f'anullsrc=r=48000:cl=stereo:d={duration}',
              '-stream_loop','-1','-i',loop,'-filter_complex',graph,'-map','[aout]',
              '-t',str(duration),'-f','f32le','pipe:1'])
    return np.frombuffer(raw,np.float32).reshape(-1,2)


def rms(a, start, end):
    b = a[int(start*48000):int(end*48000)]
    return float(np.sqrt(np.mean(b*b)))


def test_intermittent_envelope_and_end(sound,tmp_path):
    s=SfxSettings(sound,gain_db=0,start_s=1,on_s=4,off_s=2,fade_in_s=1,fade_out_s=1,loop_crossfade_s=.2)
    a=samples(s,tmp_path)
    assert len(a)==12*48000 and np.isfinite(a).all()
    assert rms(a,0,.9)<1e-7
    assert rms(a,5.1,6.9)<1e-7  # actual silent gap, no automatic mix gain changes
    full=rms(a,2.2,2.8)
    assert rms(a,1.05,1.2)<full*.15
    assert rms(a,4.8,4.95)<full*.15
    assert rms(a,8.2,8.8)==pytest.approx(full,rel=.03)
    assert rms(a,11.1,11.9)<1e-7


def test_continuous_and_gain(sound,tmp_path):
    s=SfxSettings(sound,mode='continuous',gain_db=0,start_s=0,fade_in_s=1,fade_out_s=1)
    a=samples(s,tmp_path)
    b=samples(replace(s,gain_db=-6),tmp_path)
    assert rms(a,5,6)>0.02  # no intermittent gap
    assert rms(b,5,6)/rms(a,5,6)==pytest.approx(10**(-6/20),rel=.001)
    assert rms(a,11.85,11.99)<rms(a,5,6)*.1


@pytest.mark.parametrize('field,value', [('gain_db',float('nan')),('start_s',float('inf')),
    ('off_s',-1),('on_s',0),('fade_out_s',150),('mode','bad')])
def test_invalid_settings(sound,field,value):
    with pytest.raises(ValueError):
        replace(SfxSettings(sound),**{field:value}).validate()


def test_short_source_loop_is_valid_and_crossfade_clamped(sound,tmp_path):
    out=str(tmp_path/'prepared.wav')
    x=prepare_loop(R.get_ffmpeg_path(),SfxSettings(sound,loop_crossfade_s=20),out,3)
    a=np.frombuffer(ff(['-i',out,'-f','f32le','pipe:1']),np.float32)
    assert x==1 and len(a)==2*48000*2 and np.isfinite(a).all()
    # A continuous sine must not acquire a boundary click.
    a=a.reshape(-1,2)
    assert abs(a[-1,0]-a[0,0]) < .02


def test_real_export_manifest_and_preview(sound,tmp_path):
    video=str(tmp_path/'video.mp4')
    music=str(tmp_path/'music.wav')
    ff(['-f','lavfi','-i','color=blue:s=64x48:r=10:d=1','-c:v','libx264',video])
    ff(['-f','lavfi','-i','sine=frequency=200:sample_rate=48000:duration=8','-ac','2',music])
    settings=SfxSettings(sound,start_s=1,on_s=3,off_s=1,fade_in_s=.5,fade_out_s=.5)
    result=R.render(video,[music],str(tmp_path/'out.mp4'),sfx=settings,full_decode=True)
    assert result.verified and result.duration==pytest.approx(8,abs=.03)
    manifest=json.loads(open(result.manifest,encoding='utf-8').read())
    assert manifest['audio']['sfx']['on_s']==3
    assert manifest['audio']['gains_db'] if 'gains_db' in manifest['audio'] else manifest['audio']['tracks'][0]['gain_db']==0
    preview=R.preview_audio([music],str(tmp_path/'preview.mp3'),sfx=settings)
    a=np.frombuffer(ff(['-i',preview,'-f','f32le','pipe:1']),np.float32)
    assert len(a)==8*48000*2
    R.clear_prepared()


def test_silent_rain_preserves_music(sound,tmp_path):
    # Rain scheduled after the end must not halve music through amix normalisation.
    s=SfxSettings(sound,start_s=100)
    base=R.build_audio_graph([0],0,first_input=0)
    args=['-f','lavfi','-i','sine=frequency=200:sample_rate=48000:duration=2']
    expected=ff([*args,'-filter_complex',base,'-map','[aout]','-f','f32le','pipe:1'])
    actual=ff([*args,'-stream_loop','-1','-i',sound,'-filter_complex',mix_graph(base,s,2,1),
               '-map','[aout]','-t','2','-f','f32le','pipe:1'])
    assert actual==expected
