"""Link three-depth dust, cloud-masked lightning, and wind swells to shared cues."""
import json
from pathlib import Path
import sys
import wave

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "beneath-a-crimson-sky-full-storm"))
import render_full_storm as previous

SETTINGS = json.loads((HERE / "settings.json").read_text(encoding="utf-8"))
LENGTH = SETTINGS["loop_seconds"]
CUES = SETTINGS["squalls"]
OUTPUT = HERE / "skies-of-baal-synced-storm-60s.mp4"
MIX = HERE / "synced-storm-effects.wav"


def squall(t):
    t = np.asarray(t) % LENGTH
    amount = np.zeros_like(t, dtype=np.float64)
    for cue in CUES:
        rise = previous.smooth((t-cue["rise_start"])/(cue["crest"]-cue["rise_start"]))
        fall = 1-previous.smooth((t-cue["hold_end"])/(cue["clears"]-cue["hold_end"]))
        amount = np.maximum(amount, rise*fall)
    return amount


class SyncedStorm(previous.FullStorm):
    def __init__(self):
        super().__init__()
        rng = np.random.default_rng(5824)
        self.fields = [rng.random((122, spec["grid_width"]), dtype=np.float32) for spec in SETTINGS["dust_layers"]]
        self.occlusion_checks = []
        for i, ((core, _, _, cloud, ground), (_, _, (cloud_x, cloud_y), _, _)) in enumerate(zip(self.forks, previous.EVENTS)):
            # Bury the starting section behind a soft, irregular lower cloud edge.
            # Light can still scatter into the cloud above the emerging branch.
            edge = CUES[i]["cloud_edge_y"] + 8*np.sin((self.x-cloud_x)/23) + 4*np.sin((self.x-cloud_x)/9 + i)
            edge = np.maximum(edge, cloud_y+22)
            visibility = previous.smooth((self.y-edge)/SETTINGS["cloud_edge_feather_px"])
            masked = core*visibility
            self.occlusion_checks.append(bool(np.max(masked[self.y < cloud_y+20]) == 0 and np.max(masked) > .5))
            self.forks[i] = (masked, cv2.GaussianBlur(masked, (0,0), 2.0), cv2.GaussianBlur(masked, (0,0), 8.5), cloud, ground)
        assert all(self.occlusion_checks)

    def dust(self, t):
        t %= LENGTH
        phase = t/LENGTH
        angle = phase * 2*np.pi
        surge = float(squall(t))
        veil = np.zeros_like(self.dx)
        for i, (field, spec) in enumerate(zip(self.fields, SETTINGS["dust_layers"])):
            u = self.dx/spec["width_per_cell"] - phase * spec["laps"] * spec["grid_width"]
            v = self.dy/spec["height_per_cell"] + .36*np.sin(u*2*np.pi/12 + angle) + .18*np.sin(angle*(i+1) + self.dx/217)
            texture = cv2.remap(field, u, v, cv2.INTER_CUBIC, borderMode=cv2.BORDER_WRAP)
            texture = previous.smooth((texture-.16)/.70)
            if i == 0:
                # Slow volume is most substantial around the horizon.
                depth = .48 + .52*previous.gauss((self.dy-327)/134)
                gain = .66 + .23*surge
            elif i == 1:
                # The middle sheets cross the entire aperture.
                depth = .76 + .24*np.sin(self.dy/69 + self.dx/385 - angle*3)
                gain = .52 + .52*surge
            else:
                # Faster ribbons lift over the parapet and briefly fill the view.
                lift = 335 - 60*surge + 58*np.sin(self.dx/380 - angle*3)
                depth = .40 + .60*previous.gauss((self.dy-lift)/107)
                gain = .46 + .62*surge
            opacity = texture*depth*gain*spec["strength"]
            veil += (1-veil)*opacity
        veil = cv2.resize(veil*.80 + .070 + .023*surge, (previous.RIGHT-previous.LEFT, previous.BOTTOM),
                          interpolation=cv2.INTER_LINEAR) * self.mask

        grit = np.zeros_like(veil, np.uint8)
        first = SETTINGS["front_grit_laps"][0]
        width = len(SETTINGS["front_grit_laps"])
        px = 130+1260*((self.grains[:,0]+phase*(first+np.floor(self.grains[:,2]*width)))%1)
        py = 8+568*self.grains[:,1]+12*np.sin(px/97+self.grains[:,0]*8-angle*4)
        for x,y,size,power in zip(px,py,self.grains[:,2],self.grains[:,3]):
            ix,iy = int(x)-previous.LEFT,int(y)
            if not (12 <= ix < grit.shape[1] and 2 <= iy < grit.shape[0]-2 and self.mask[iy,ix] > .1):
                continue
            alpha = int((9+29*power)*(.61+.52*surge)*(.52+1.45*veil[iy,ix]))
            cv2.line(grit, (ix-(4+int(size*7)),iy-1), (ix,iy), alpha, 1, cv2.LINE_AA)
        return veil, grit.astype(np.float32)*(self.mask/255)


def read_stem(name):
    with wave.open(str(previous.PREVIOUS / name), "rb") as audio:
        assert (audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getnframes()) == (2,2,48000,LENGTH*48000)
        return np.frombuffer(audio.readframes(audio.getnframes()), dtype="<i2").reshape(-1,2)/32767


def write_mix():
    wind = read_stem("storm-wind-grit.wav")
    thunder = read_stem("rolling-thunder.wav")
    previous_cues = json.loads((previous.PREVIOUS / "sound-checks.json").read_text(encoding="utf-8"))["cues"]
    assert [cue["crest"] for cue in CUES] == [event[0] for event in previous.EVENTS]
    assert all(any(prior["flash_s"] == cue["crest"] and prior["thunder_start_s"] == cue["thunder_start"] for prior in previous_cues) for cue in CUES)
    t = np.arange(len(wind))/48000
    floor, crest = SETTINGS["wind_grit_gain_floor_db"], SETTINGS["wind_grit_gain_crest_db"]
    gain = 10**((floor+(crest-floor)*squall(t))/20)
    mix = wind*gain[:, None]+thunder
    assert np.isfinite(mix).all() and np.max(np.abs(mix)) < 1
    pcm = np.rint(mix*32767).astype("<i2").tobytes()
    if MIX.exists():
        with wave.open(str(MIX), "rb") as audio:
            assert (audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getnframes()) == (2,2,48000,len(mix))
            assert audio.readframes(len(mix)) == pcm
    else:
        with wave.open(str(MIX), "wb") as audio:
            audio.setparams((2,2,48000,len(mix),"NONE","not compressed"))
            audio.writeframes(pcm)
    return {"settings_sha256": previous.sha(HERE / "settings.json"), "synchronized_squalls": CUES,
            "dust_speeds_preview_px_per_second": [p["grid_width"]*p["width_per_cell"]*p["laps"]/LENGTH for p in SETTINGS["dust_layers"]],
            "cloud_tips_hidden_in_both_strikes": True, "audio_source_thunder_sha256": previous.sha(previous.PREVIOUS / "rolling-thunder.wav"),
            "audio_source_wind_grit_sha256": previous.sha(previous.PREVIOUS / "storm-wind-grit.wav")}


if __name__ == "__main__":
    assert not OUTPUT.exists()
    previous.main(SyncedStorm, OUTPUT, MIX, write_mix())
