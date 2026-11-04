"""Create separable, circular wind, mineral grit and synthesized thunder stems."""
import hashlib
import json
from pathlib import Path
import subprocess
import wave

import imageio_ffmpeg
import numpy as np
from scipy.signal import butter, sosfilt

HERE = Path(__file__).resolve().parent
LIBRARY = HERE.parent / "sfx-library/assets"
FF = imageio_ffmpeg.get_ffmpeg_exe()
RATE = 48000
N = 60 * RATE
# Flash, travel delay, event length, relative level, and distance colour.
CUES = ((8.4, 2.5, 9.7, .62, .42), (16.7, 3.2, 9.1, .39, .66), (26.4, 1.8, 12.3, 1.0, .13),
        (33.2, 3.3, 9.8, .52, .69), (50.6, 1.9, 11.1, .87, .23), (56.2, 2.8, 9.2, .42, .61))


def sample(seconds):
    return round(seconds * RATE)


def insert(target, audio, start):
    start %= len(target)
    first = min(len(target) - start, len(audio))
    target[start:start+first] += audio[:first]
    target[:len(audio)-first] += audio[first:]


def band(data, lo, hi):
    return sosfilt(butter(3, [lo, hi], btype="bandpass", fs=RATE, output="sos"), data, axis=0)


def rms(data):
    return float(np.sqrt(np.mean(np.square(data, dtype=np.float64))))


def amplitude(data, target):
    return (data * (target / max(rms(data), 1e-8))).astype(np.float32)


def envelope(length, rise, fall):
    ramp = lambda seconds: np.sin(np.linspace(0, np.pi/2, sample(seconds)))**2
    result = np.ones(length, dtype=np.float32)
    result[:sample(rise)] = ramp(rise)
    result[-sample(fall):] = ramp(fall)[::-1]
    return result


def source(name):
    path = LIBRARY / name
    if path.stat().st_size < 200:
        pointer = path.read_text(encoding="utf-8").splitlines()
        assert pointer[0] == "version https://git-lfs.github.com/spec/v1"
        digest = pointer[1].removeprefix("oid sha256:")
        path = HERE.parents[1] / ".git/lfs/objects" / digest[:2] / digest[2:4] / digest
        with path.open("rb") as media:
            assert hashlib.file_digest(media, "sha256").hexdigest() == digest
    data = subprocess.check_output([FF, "-v", "error", "-i", str(path), "-vn", "-ac", "2", "-ar", str(RATE),
                                    "-f", "f32le", "pipe:1"])
    return np.frombuffer(data, dtype="<f4").reshape(-1, 2)


def thunder(rng, length, distance):
    n = sample(length)
    t = np.arange(n) / RATE
    noise = rng.standard_normal((n, 3), dtype=np.float32)
    belly = amplitude(band(noise[:, 0], 28, 94 - 27*distance), 1)
    body = amplitude(band(noise[:, 1], 69, 275 - 105*distance), 1)
    detail = amplitude(band(noise[:, 2], 179, 900 - 430*distance), 1)
    result = np.zeros(n, dtype=np.float64)
    for offset, gain, decay in ((.0, 1., 2.35), (.61, .70, 2.8), (1.82, .57, 3.3), (3.34, .35, 3.7), (5.28, .22, 2.8)):
        dt = t - offset - rng.uniform(-.09, .18)
        pulse = np.maximum(dt, 0)
        volume = (1-np.exp(-pulse/(.16 + .22*distance)))**2 * np.exp(-pulse/decay)
        result += gain * volume * (belly * .66 + body * .79 + detail * (.40 - .29*distance)*np.exp(-pulse/1.38))
    fade = envelope(n, .09, 2.0)
    spread = amplitude(band(noise[:, 2], 51, 168), 1) * .105 * np.exp(-t/4.6)
    def echo(signal, delay):
        return np.pad(signal, (delay, 0))[:len(signal)]
    stereo = np.stack((result + .23*echo(result, sample(.155)) + spread,
                       result + .20*echo(result, sample(.213)) - spread), axis=1)
    return (stereo * fade[:, None]).astype(np.float32)


def wave_out(name, values):
    path = HERE / name
    assert np.isfinite(values).all() and float(np.max(np.abs(values))) < 1
    pcm = np.rint(values * 32767).astype("<i2").tobytes()
    if path.exists():
        with wave.open(str(path), "rb") as file:
            assert (file.getnchannels(), file.getsampwidth(), file.getframerate(), file.getnframes()) == (2, 2, RATE, len(values))
            assert file.readframes(len(values)) == pcm
        return
    with wave.open(str(path), "wb") as file:
        file.setparams((2, 2, RATE, len(values), "NONE", "not compressed"))
        file.writeframes(pcm)


def main():
    rng = np.random.default_rng(5106)
    base = np.zeros((N, 2), dtype=np.float32)
    gravel = np.zeros_like(base)
    rolling = np.zeros_like(base)
    # Crossfaded draws from the existing exterior wind source, with changed offsets and widths.
    wind = source("wind-soft-exterior-01.mp3")
    for at, offset, scale in ((-4.8, .1, .91), (5.8, .37, .83), (16.4, .72, 1.08),
                              (27.1, .49, .89), (36.8, .22, 1.14), (46.7, .66, .96), (56.1, .93, .89)):
        count = min(sample(15), len(wind))
        start = int((len(wind) - count) * offset)
        segment = amplitude(band(wind[start:start+count], 70, 1810), .020) * scale
        segment *= envelope(count, 2.2, 3.3)[:, None]
        insert(base, segment, sample(at))
    tt = np.arange(N, dtype=np.float32) / RATE
    pulse = lambda center, width: np.exp(-.5 * (((tt - center + 30) % 60 - 30)/width)**2)
    base *= (.74 + .40*pulse(19.5, 6.7) + .46*pulse(41.5, 8.1))[:, None]

    grit = source("grit-mineral-soft-01.mp3")
    for at, length, level, offset in ((1.6, 3.3, .39, .15), (9.3, 3.8, .48, .69), (15.2, 6.4, .72, .31),
                                       (22.8, 4.0, .57, .86), (31.5, 3.7, .42, .45), (37.7, 6.5, .91, .12),
                                       (46.3, 5.5, .62, .77), (55.7, 3.9, .37, .34)):
        count = min(len(grit), sample(length))
        start = int((len(grit)-count) * offset)
        segment = amplitude(band(grit[start:start+count], 165, 2360), .013) * level
        segment *= envelope(count, .9, 1.5)[:, None]
        insert(gravel, segment, sample(at))

    for flash, delay, length, strength, distance in CUES:
        event = thunder(rng, length, distance)
        event *= strength * .265 / float(np.max(np.abs(event)))
        insert(rolling, event, sample(flash + delay))

    mix = base + gravel + rolling
    wave_out("storm-wind-grit.wav", base + gravel)
    wave_out("rolling-thunder.wav", rolling)
    wave_out("storm-audition-mix.wav", mix)
    report = {"sample_rate": RATE, "frames": N, "channels": 2, "no_music": True,
              "cues": [{"flash_s": f, "delay_s": d, "thunder_start_s": round(f+d, 1), "tail_s": dur,
                         "relative_level": strength} for f, d, dur, strength, _ in CUES],
              "mix_peak_dbfs": round(float(20*np.log10(np.max(np.abs(mix)))), 2),
              "thunder_peak_dbfs": round(float(20*np.log10(np.max(np.abs(rolling)))), 2),
              "wind_grit_peak_dbfs": round(float(20*np.log10(np.max(np.abs(base+gravel)))), 2),
              "join_step": float(np.max(np.abs(mix[0]-mix[-1]))),
              "synthesized_thunder": True}
    (HERE / "sound-checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
