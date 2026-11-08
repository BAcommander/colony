"""Optional reusable ambience: crossfaded source loop and timed rain envelopes."""
import math
import os
from dataclasses import dataclass

from app import exporter


@dataclass(frozen=True)
class SfxSettings:
    path: str
    mode: str = 'intermittent'
    gain_db: float = -6.0
    start_s: float = 20.0
    on_s: float = 120.0  # Includes both fades.
    off_s: float = 90.0
    fade_in_s: float = 20.0
    fade_out_s: float = 30.0
    loop_crossfade_s: float = 2.0

    def validate(self):
        if not os.path.isfile(self.path):
            raise ValueError('Choose an existing rain/SFX audio file.')
        if self.mode not in ('continuous', 'intermittent'):
            raise ValueError('SFX mode must be continuous or intermittent.')
        values = (self.gain_db, self.start_s, self.on_s, self.off_s,
                  self.fade_in_s, self.fade_out_s, self.loop_crossfade_s)
        if not all(math.isfinite(v) for v in values):
            raise ValueError('Rain/SFX settings must be finite numbers.')
        if not -60 <= self.gain_db <= 12:
            raise ValueError('Rain/SFX gain must be between -60 and +12 dB.')
        if min(values[1:]) < 0 or self.on_s <= 0:
            raise ValueError('Rain/SFX times must be nonnegative; rain duration must be positive.')
        if self.mode == 'intermittent' and self.fade_in_s + self.fade_out_s > self.on_s:
            raise ValueError('Rain fade-in plus fade-out must fit inside the rain duration.')


def envelope(settings, total):
    """Frame-evaluated smooth cosine fades, including a truncated final event."""
    s = settings
    age = f'(t-{s.start_s:.9f})'
    phase = f'mod({age},{s.on_s + s.off_s:.9f})' if s.mode == 'intermittent' else age
    def rise(x, length):
        return f'(0.5-0.5*cos(PI*clip(({x})/{length:.9f},0,1)))' if length else '1'
    up = rise(phase, s.fade_in_s)
    end = rise(f'{total:.9f}-t', s.fade_out_s)
    if s.mode == 'intermittent':
        down = rise(f'{s.on_s:.9f}-({phase})', s.fade_out_s)
        value = f'if(lt({phase},{s.on_s:.9f}),min({up},{down}),0)'
    else:
        value = up
    return f'if(isnan(t),0,if(lt(t,{s.start_s:.9f}),0,min({value},{end})))'


def mix_graph(music_graph, settings, total, sfx_input):
    """Insert SFX before the existing final limiter; never normalise the music."""
    settings.validate()
    prefix, limiter = music_graph.rsplit(';', 1)
    label = limiter.split(']', 1)[0] + ']'
    limiter = limiter.replace(label, '[mixed]', 1)
    gain = 10 ** (settings.gain_db / 20)
    rain = (f'[{sfx_input}:a:0]aresample=48000,'
            f'aformat=sample_fmts=fltp:channel_layouts=stereo,asetpts=PTS-STARTPTS,'
            f"volume='{gain:.12f}*({envelope(settings, total)})':eval=frame[rain]")
    return ';'.join((prefix, rain,
                     f'{label}[rain]amix=inputs=2:duration=first:normalize=0[mixed]', limiter))


def prepare_loop(ffmpeg, settings, output, duration):
    """Make one PCM loop: middle + equal-power tail/head overlap.

    Decode once, rather than letting MP3 encoder padding recur on every repeat.
    Rotation ends on the head/body boundary; source stays untouched.
    """
    settings.validate()
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('Rain/SFX file has no readable audio duration.')
    x = min(settings.loop_crossfade_s, duration / 3)
    base = 'aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,asetpts=PTS-STARTPTS'
    if x > 0:
        graph = (f'[0:a:0]{base},asplit=3[h][m][t];'
                 f'[h]atrim=end={x:.9f},asetpts=PTS-STARTPTS[head];'
                 f'[m]atrim=start={x:.9f}:end={duration-x:.9f},asetpts=PTS-STARTPTS[mid];'
                 f'[t]atrim=start={duration-x:.9f}:end={duration:.9f},asetpts=PTS-STARTPTS[tail];'
                 f'[tail]afade=t=out:st=0:d={x:.9f}:curve=qsin[tf];'
                 f'[head]afade=t=in:st=0:d={x:.9f}:curve=qsin[hf];'
                 '[tf][hf]amix=inputs=2:normalize=0[join];'
                 '[mid][join]concat=n=2:v=0:a=1[out]')
    else:
        graph = f'[0:a:0]{base}[out]'
    exporter._run_ffmpeg([ffmpeg, '-y', '-hide_banner', '-nostdin', '-i', settings.path,
                          '-filter_complex', graph, '-map', '[out]', '-c:a', 'pcm_f32le', output],
                         timeout=int(300 + duration * 2))
    return x
