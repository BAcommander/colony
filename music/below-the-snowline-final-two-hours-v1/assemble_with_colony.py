"""Assemble Snowline using the actual verified Colony v3 intro export engine."""
from pathlib import Path
import sys
import os
import json
import subprocess
import hashlib
import shutil
import time

H = Path(__file__).resolve().parent
R = H.parents[1]
APP = Path('C:/dev/SpeedySlideShow')
SNAP = R / 'creative/brand/intro-v3/tool-source-snapshot'
VIDEO = H / 'visual/masters/Snowline-v6-loop-120s-4K.mp4'
SOURCE_AUDIO = R / 'exports/13-below-the-snowline/audio-2h-v6/Below-the-Snowline-2-Hours-unfaded-master-v6.flac'
AUDIO = H / 'cache/Snowline-V6-2-Hours-assembly-audio.flac'
EXPORT = R / 'exports/13-below-the-snowline'
CACHE = EXPORT / 'final-v1-cache'
OUTPUT = EXPORT / 'Below-the-Snowline-2-Hours-4K-v1.mp4'
sys.dont_write_bytecode = True
sys.path.insert(0, r'C:\AI\ComfyUI\venv\Lib\site-packages')
sys.path.insert(0, str(APP))
os.environ['IMAGEIO_FFMPEG_EXE'] = shutil.which('ffmpeg') or 'ffmpeg'
import colony
colony.__path__.insert(0, str(SNAP / 'colony'))
from colony import render
from colony.intro import IntroSettings
from app import exporter


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(name, value):
    (H / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    assert not OUTPUT.exists(), 'Preserve the existing final video'
    assert Path(render.__file__).resolve() == (SNAP / 'colony/render.py').resolve()
    implementation = json.loads((R / 'creative/brand/intro-v3/implementation-verification.json').read_text(encoding='utf-8'))
    verified = {}
    for entry in implementation['files']:
        path = SNAP / Path(entry['path']).relative_to(APP)
        assert digest(path) == entry['sha256'], path
        verified[str(path)] = entry['sha256']
    visual = json.loads((H / 'visual/master-validation.json').read_text(encoding='utf-8'))
    assert visual['status'] == 'passed'
    assert Path(visual['output']).resolve() == VIDEO.resolve()
    assert visual['seconds'] == 120 and visual['dimensions'] == [3840, 2160] and visual['fps'] == 30
    assert digest(VIDEO) == visual['sha256']
    audio = json.loads((H / 'audio-preparation-validation.json').read_text(encoding='utf-8'))
    assert audio['status'] == 'passed'
    assert Path(audio['output']['path']).resolve() == AUDIO.resolve()
    assert digest(AUDIO) == audio['output']['sha256'] and digest(SOURCE_AUDIO) == audio['source']['sha256']
    assert audio['output']['seconds'] == 7200 and audio['output']['sample_frames'] == 345600000
    assert audio['processing']['gain_db'] == 0.4 and not audio['processing']['opening_fade_applied']
    assert audio['processing']['closing_fade_start_seconds'] == 7180 and audio['processing']['closing_fade_seconds'] == 20
    EXPORT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    ffmpeg = render.get_ffmpeg_path()
    info = render.probe_video(ffmpeg, str(VIDEO))
    assert info.size == (3840, 2160) and info.duration == 120 and info.fps == 30
    probe = json.loads(subprocess.check_output([shutil.which('ffprobe') or 'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_streams', '-of', 'json', str(VIDEO)]))['streams'][0]
    assert probe['codec_name'] == 'h264' and probe['pix_fmt'] == 'yuv420p' and probe['has_b_frames'] == 0
    assert int(probe['nb_frames']) == 3600 and probe['color_range'] == 'tv'
    assert all(probe[key] == 'bt709' for key in ['color_space', 'color_transfer', 'color_primaries'])
    estimated_final = VIDEO.stat().st_size * 60
    assert shutil.disk_usage(EXPORT).free > 2 * estimated_final + 10 * 1024**3, 'Insufficient assembly/faststart headroom'
    render._prepared = render.Prepared(str(CACHE), render._file_key(str(VIDEO)), info,
                                       render.color_tags_for(info), str(VIDEO), 120.0, info)
    render.LOOP_CRF = 0
    render.LOOP_PRESET = 'veryfast'
    original_encode_args = render._loop_encode_args

    def tagged_lossless_args(color):
        args = original_encode_args(color)
        position = args.index('-crf')
        args[position:position+2] = ['-qp', '0']
        return args + ['-bsf:v', 'h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0']

    render._loop_encode_args = tagged_lossless_args
    intro = IntroSettings('Below the Snowline', fade_audio=True)
    settings = {
        'tool': 'Actual preserved Colony v3 renderer; Prepared reuses the verified 120-second clean master',
        'renderer_path': str(Path(render.__file__)), 'renderer_sha256': digest(render.__file__),
        'intro_verified_files': verified,
        'dependencies': {str(Path(exporter.__file__)): digest(exporter.__file__),
                         str(APP / 'colony/sfx.py'): digest(APP / 'colony/sfx.py'),
                         str(APP / 'app/utils.py'): digest(APP / 'app/utils.py')},
        'installed_app_modified': False,
        'video': {'path': str(VIDEO), 'sha256': visual['sha256'], 'native_source_dimensions': [1672, 941],
                  'output_dimensions': [3840, 2160], 'fps': 30, 'unit_seconds': 120},
        'audio': {'path': str(AUDIO), 'sha256': audio['output']['sha256'], 'seconds': 7200,
                  'source_unfaded_master': audio['source'], 'preparation_validation': 'audio-preparation-validation.json',
                  'playback_gain_db_already_applied': 0.4, 'assembly_gain_db': 0,
                  'gain_db': 0, 'match_loudness': False, 'crossfade': 0, 'sfx': None,
                  'closing_fade': 'One linear 20-second closing fade is already in the assembly FLAC; retained unchanged'},
        'opening': intro.record(),
        'opening_encoder': {'qp': 0, 'preset': 'veryfast', 'b_frames': 0, 'pixel_format': 'yuv420p',
                            'color': 'BT.709 TV', 'metadata_wrapper': 'Explicit H.264 VUI completion, identical picture data'},
        'clean_units': 'First complete 120-second unit carries intro once; following 59 units copied from the clean master',
        'output': str(OUTPUT), 'expected_frames': 216000, 'expected_seconds': 7200,
        'ffmpeg': ffmpeg, 'ffmpeg_version': subprocess.check_output([ffmpeg, '-version']).decode().splitlines()[0]}
    save('assembly-settings.json', settings)
    state = [-1, 0, 'Starting']

    def status(message):
        state[2] = message
        state[0] = -1
        print(message, flush=True)
        save('assembly-progress.json', {'stage': message, 'utc_epoch': time.time()})

    def progress(fraction, eta):
        percent, now = int(fraction * 100), time.monotonic()
        if percent >= state[0] + 5 or now - state[1] > 25:
            record = {'stage': state[2], 'stage_progress_percent': percent,
                      'stage_eta_seconds': eta, 'utc_epoch': time.time()}
            print(json.dumps(record), flush=True)
            save('assembly-progress.json', record)
            state[:2] = [percent, now]

    result = render.render(str(VIDEO), [str(AUDIO)], str(OUTPUT), crossfade=0,
                           overlay_mode=render.OVERLAY_OFF, match_loudness=False,
                           full_decode=True, overwrite=False, intro=intro,
                           on_status=status, on_progress=progress)
    assert result.output == str(OUTPUT) and result.verified and all(check.ok for check in result.checks)
    assert result.duration == 7200 and (result.width, result.height, result.fps) == (3840, 2160, 30)
    assert result.gains_db == [0] and result.crossfade == 0 and not result.overlay_times
    shutil.copy2(result.manifest, H / 'colony-export.json')
    assert digest(VIDEO) == visual['sha256'] and digest(AUDIO) == audio['output']['sha256']
    save('assembly-result.json', {'output': str(OUTPUT), 'bytes': OUTPUT.stat().st_size,
                                  'duration_seconds': result.duration, 'dimensions': [result.width, result.height],
                                  'fps': result.fps, 'colony_full_decode_passed': True,
                                  'checks': [vars(check) for check in result.checks],
                                  'source_hashes_unchanged': True,
                                  'further_checks': 'Independent verify_final.py checks packets, decoded frames, all audio and intro stills.'})
    print('Actual Colony assembly and full decode passed; independent delivery checks next.', flush=True)


if __name__ == '__main__':
    main()
