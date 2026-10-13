"""Real delivery tests for once-only titles, scene colour and the audio entrance."""
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image
import pytest

from colony import render as R
from colony.intro import IntroSettings, TAGLINE, make_cards
from colony.sfx import SfxSettings


def ff(args):
    return subprocess.run([R.get_ffmpeg_path(), '-v', 'error', '-y', *args],
                          capture_output=True, check=True).stdout


def audio(path):
    return np.frombuffer(ff(['-i', str(path), '-map', '0:a:0', '-f', 'f32le', '-']), np.float32).reshape(-1, 2)


def rms(a, start, end):
    part = a[round(start*48000):round(end*48000)]
    return float(np.sqrt(np.mean(part*part)))


def pictures(path):
    return np.frombuffer(ff(['-i', str(path), '-map', '0:v:0', '-pix_fmt', 'rgb24',
                            '-f', 'rawvideo', '-']), np.uint8).reshape(-1, 180, 320, 3)


@pytest.fixture
def sources(tmp_path):
    R.clear_prepared()
    video, music = tmp_path/'scene.mp4', tmp_path/'music.wav'
    ff(['-f', 'lavfi', '-i', 'color=c=0x48657d:s=320x180:r=10:d=2', '-c:v', 'libx264',
        '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', str(video)])
    ff(['-f', 'lavfi', '-i', 'sine=frequency=200:sample_rate=48000:duration=46', '-ac', '2', str(music)])
    yield str(video), str(music)
    R.clear_prepared()


def test_real_opening_once_audio_entrance_and_clean_tail(sources, tmp_path):
    video, music = sources
    result = R.render(video, [music], str(tmp_path/'intro.mp4'), intro=IntroSettings('Rainline Relay'), full_decode=True)
    assert result.verified and result.duration == 46
    frames = pictures(result.output)
    assert len(frames) == 460
    clean = pictures(R._prepared.loop_path)
    # Every later decoded frame exactly retains the prepared clean picture.
    assert np.array_equal(frames[220:], np.tile(clean, (12, 1, 1, 1)))
    assert frames[0, 10, 10].mean() == pytest.approx(clean[0, 10, 10].mean() * .12, abs=3)
    assert np.array_equal(frames[0, 10, 10], frames[90, 10, 10])
    assert frames[120, 10, 10].mean() < frames[170, 10, 10].mean() < clean[0, 10, 10].mean()
    # Readable branding/title/tagline, with the early near-black hold.
    for frame in (40, 120, 170):
        assert frames[frame].max() > 190
    assert frames[90].max() < 130
    # PRESENTS is a separate delayed reveal below the enlarged channel name.
    assert frames[40, 98:108].max() < 130
    # Tiny 180p glyphs are subpixel-antialiased; judge their contrast against
    # the dark background, not the solid-ivory value of a full-size letter.
    assert int(frames[60, 98:108].max()) - int(frames[40, 98:108].max()) > 100
    brand_columns = np.where((frames[60, 65:94].max(axis=2) > 185).any(axis=0))[0]
    assert brand_columns[-1] - brand_columns[0] > 115
    # The invitation overlaps the title, near the bottom, and holds five
    # seconds after the central title clears. These regions catch regressions
    # where the invitation returns to the centre or a fourth card is omitted.
    assert frames[110, 151:170].max() < 150
    for frame in (130, 160, 190, 200):
        assert frames[frame, 151:170].max() > 165
    assert frames[130, 60:115].max() > 200
    assert frames[160, 60:115].max() < 170
    title_columns = np.where((frames[130, 73:105].max(axis=2) > 185).any(axis=0))[0]
    assert title_columns[-1] - title_columns[0] > 145
    rule = frames[130, 107:113].astype(int)
    amber = (rule[:,:,0] > 90) & (rule[:,:,0]-rule[:,:,2] > 35)
    assert amber.any(axis=0).sum() > 30
    a = audio(result.output)
    assert rms(a, 0, 4.9) < 1e-7
    full = rms(a, 23, 24)
    assert rms(a, 5.1, 5.3) < full * .01
    assert rms(a, 12.4, 12.6) / full == pytest.approx(.5, abs=.03)
    assert rms(a, 34, 35) / full == pytest.approx(1, abs=.01)
    record = json.loads(Path(result.manifest).read_text(encoding='utf-8'))
    assert record['opening']['tagline'] == TAGLINE
    assert len(record['opening']['font_sha256']) == 2
    assert record['output']['color']['space'] == 'bt709'


def test_preview_and_full_export_agree_and_preserve_later_sfx(sources, tmp_path):
    video, music = sources
    silent = str(tmp_path/'silent.wav')
    ff(['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo:d=46', silent])
    sfx = SfxSettings(music, mode='continuous', gain_db=0, start_s=22, fade_in_s=1, fade_out_s=10)
    kwargs = dict(intro=IntroSettings('THE SHORELESS COLONY'), sfx=sfx)
    preview = R.render(video, [silent], str(tmp_path/'preview.mp4'), preview_seconds=25, **kwargs)
    full = R.render(video, [silent], str(tmp_path/'full.mp4'), **kwargs)
    assert np.array_equal(pictures(preview.output), pictures(full.output)[:250])
    a, b = audio(preview.output), audio(full.output)
    assert rms(a, 0, 21.9) < 1e-7
    assert rms(a, 23.5, 24.5) == pytest.approx(rms(b, 23.5, 24.5), rel=.01)
    assert rms(a, 23.5, 24.5) > .04


def test_keep_supplied_audio_and_disabled_intro(sources, tmp_path):
    video, music = sources
    original = R.render(video, [music], str(tmp_path/'plain.mp4'), preview_seconds=25)
    keep = R.render(video, [music], str(tmp_path/'keep.mp4'), preview_seconds=25,
                    intro=IntroSettings('Beneath a Crimson Sky', fade_audio=False))
    assert np.array_equal(audio(original.output), audio(keep.output))
    assert json.loads(Path(original.manifest).read_text())['opening'] is None


def test_quote_paths_titles_native_4k_cards(tmp_path):
    folder = tmp_path / "Colony's assets"
    cards = make_cards(IntroSettings("D'Arcy: 100% [Station]"), 3840, 2160, folder)
    for path, x, y in cards:
        im = Image.open(path)
        assert im.mode == 'RGBA' and im.getbbox()
        assert 0 <= x and 0 <= y and x+im.width <= 3840 and y+im.height <= 2160
    title = Image.open(next(path for path, _, _ in cards if Path(path).stem == 'title'))
    assert title.height > 200  # native resolution, not a small upscaled bitmap


@pytest.mark.parametrize('title', ['', '   ', 'a\nb\nc', 'a\x00b', 'x'*161])
def test_invalid_title(title):
    with pytest.raises(ValueError):
        IntroSettings(title).validate()


def test_subscription_overlay_is_deferred_past_opening():
    assert R.plan_overlay(R.OVERLAY_ONCE, 46, 2, 10, intro=True) == [22]
    assert R.plan_overlay(R.OVERLAY_ONCE, 25, 2, 10, intro=True) == []


def test_visual_preview_requires_no_music(sources, tmp_path):
    video, _ = sources
    result = R.preview_opening(video, [], str(tmp_path/'silent.mp4'), intro=IntroSettings('Rainline Relay'))
    assert result.verified and result.duration == 25
    assert not audio(result.output).any()
    record = json.loads(Path(result.manifest).read_text(encoding='utf-8'))
    assert record['preview_silent'] is True and record['audio']['tracks'] == []


def test_short_audio_rejected_with_opening(sources, tmp_path):
    video, _ = sources
    short = str(tmp_path/'short.wav')
    ff(['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo:d=3', short])
    with pytest.raises(ValueError, match='22 seconds'):
        R.render(video, [short], str(tmp_path/'bad.mp4'), intro=IntroSettings('Test'))


def test_nonintegral_loop_preserves_scene_phase(sources, tmp_path):
    _, music = sources
    video = str(tmp_path/'moving.mp4')
    ff(['-f', 'lavfi', '-i', 'testsrc2=s=320x180:r=10:d=3', '-c:v', 'libx264', video])
    result = R.render(video, [music], str(tmp_path/'motion.mp4'), intro=IntroSettings('TEST'), full_decode=True)
    clean = pictures(R._prepared.loop_path)
    actual = pictures(result.output)
    assert result.verified and len(actual) == 460
    for i in range(240, 460):
        assert np.array_equal(actual[i], clean[i % 30])
