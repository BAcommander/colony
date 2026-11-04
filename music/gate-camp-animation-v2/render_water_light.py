"""Add moving water highlights and localized blue spill to Gate Camp's V1 warp."""
import json
from pathlib import Path
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
BASE_DIR = HERE.parent / "gate-camp-animation-v1"
sys.path.insert(0, str(BASE_DIR))
from render_portal import FFMPEG, PLAN, ROOT, Portal, sha, smooth

SETTINGS_PATH = HERE / "look-settings.json"
SETTINGS = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
OUTPUT = HERE / "Gate-Camp-water-and-light-v2-8s.mp4"


def band_fields(x, y):
    """Curved highlight fronts sweep across the surface at two scales."""
    fields = []
    for config in SETTINGS["light_bands"]:
        angle = np.deg2rad(config["direction_degrees"])
        along = x*np.cos(angle)+y*np.sin(angle)
        across = x*np.sin(angle)-y*np.cos(angle)
        curve = config["curve_px"]*np.sin(across/51+0.7)
        phase = (2*np.pi*(along+curve)/config["wavelength_px"]).astype(np.float32)
        rate = 2*np.pi/config["period_seconds"]
        fields.append((phase, rate, config["weight"]))
    return fields


def light_at(fields, t):
    light = np.zeros_like(fields[0][0])
    for phase, rate, weight in fields:
        crest = .5+.5*np.cos(phase-rate*t)
        light += weight*crest**3
    return light


class WaterLight:
    def __init__(self, source):
        self.portal = Portal(source)
        self.surface_fields = band_fields(self.portal.x-157, self.portal.y-174)
        self.aperture = self.portal.aperture.astype(np.float32)
        self.inset = smooth((self.portal.alpha-.22)/.78)
        self.blur = SETTINGS["surface"]["fine_detail_blur_px"]
        self.blur_weight = np.maximum(cv2.GaussianBlur(self.aperture,(0,0),self.blur),1e-6)
        left, top, right, bottom = SETTINGS["spill"]["roi"]
        self.spill_region = np.s_[top:bottom,left:right]
        self.stone = np.zeros((bottom-top,right-left),np.uint8)
        for polygon in SETTINGS["spill"]["stone_polygons"]:
            local = np.asarray(polygon,np.int32)-(left,top)
            cv2.fillPoly(self.stone,[local.astype(np.int32)],1)
        distance = cv2.distanceTransform(np.pad(self.stone,1),cv2.DIST_L2,5)[1:-1,1:-1]
        y,x = np.mgrid[top:bottom,left:right].astype(np.float32)
        # Project the same moving light fronts onto the receding stone.
        self.spill_fields = band_fields((x-1259)*1.25, 155+(y-435)*2.7)
        reach = np.exp(-.5*((x-1243)/100)**2-.5*((y-433)/33)**2)
        self.spill_alpha = smooth((distance-1)/SETTINGS["spill"]["feather_px"])*reach
        self.tint = np.array(SETTINGS["spill"]["rgb_lift"],np.float32)

    def frame(self,t):
        frame, determinant = self.portal.frame(t)
        settings = SETTINGS["surface"]
        surface = frame[self.portal.region]
        original = surface.copy()
        values = surface.astype(np.float32)
        # A normalized blur softens the finest sparkles without drawing rim pixels in.
        low = cv2.GaussianBlur(values*self.aperture[...,None],(0,0),self.blur)/self.blur_weight[...,None]
        values = low + settings["fine_detail_retention"]*(values-low)
        band = light_at(self.surface_fields,t)[...,None]
        values *= settings["base_gain"]+settings["rolling_gain"]*band
        pearl = np.array(settings["highlight_rgb"],np.float32)
        values += (pearl-values)*settings["highlight_mix"]*band
        surface[:] = np.clip(np.rint(original+(values-original)*self.inset[...,None]),0,255).astype(np.uint8)
        assert np.array_equal(surface[self.inset == 0],original[self.inset == 0])

        landing = frame[self.spill_region]
        strength = self.spill_alpha*(.21+.79*light_at(self.spill_fields,t))
        lift = np.rint(strength[...,None]*self.tint).astype(np.uint8)
        assert np.all(lift[self.stone == 0] == 0)
        landing[:] = cv2.add(landing,lift)
        return frame,determinant,int(lift[...,2].max())


def main():
    cv2.setNumThreads(1)
    source = ROOT / PLAN["source"]
    assert sha(source) == PLAN["source_sha256"]
    partial = OUTPUT.with_suffix(".partial.mp4")
    if OUTPUT.exists() or partial.exists():
        raise FileExistsError("Use a fresh destination for a new version")
    with Image.open(source) as image:
        effect = WaterLight(np.asarray(image.convert("RGB")))
    width,height = PLAN["preview_dimensions"]
    fps = PLAN["fps"]
    frames = fps*PLAN["preview_seconds"]
    command = [FFMPEG,"-v","error","-n","-f","rawvideo","-pix_fmt","rgb24","-s",f"{width}x{height}","-r",str(fps),
               "-i","pipe:0","-an","-vf","scale=out_color_matrix=bt709:out_range=tv,format=yuv420p","-c:v","libx264",
               "-preset","veryfast","-threads","4","-crf","17","-colorspace","bt709","-color_primaries","bt709",
               "-color_trc","bt709","-color_range","tv","-movflags","+faststart",str(partial)]
    protected = np.ones(effect.portal.artwork.shape[:2],bool)
    protected[effect.portal.region] &= ~effect.portal.active
    protected[effect.spill_region] &= effect.spill_alpha == 0
    reference = effect.portal.artwork[protected]
    jacobians,spill_peaks = [],[]
    with subprocess.Popen(command,stdin=subprocess.PIPE) as encoder:
        try:
            for index in range(frames):
                frame,jacobian,peak = effect.frame(index/fps)
                assert np.array_equal(frame[protected],reference),index
                jacobians.append(jacobian)
                spill_peaks.append(peak)
                encoder.stdin.write(cv2.resize(frame,(width,height),interpolation=cv2.INTER_AREA).tobytes())
        finally:
            encoder.stdin.close()
        assert encoder.wait() == 0
    assert 4 <= max(spill_peaks) <= 15
    result = subprocess.check_output([FFMPEG,"-v","error","-i",str(partial),"-map","0","-f","framehash","pipe:1"],text=True)
    assert f"#dimensions 0: {width}x{height}" in result and f"#tb 0: 1/{fps}" in result
    assert "#media_type 0: video" in result and "audio" not in result
    rows = [line.split(",") for line in result.splitlines() if line and not line.startswith("#")]
    assert [int(row[2]) for row in rows] == list(range(frames)) and len({row[-1] for row in rows}) == frames
    partial.rename(OUTPUT)
    report = {"path":OUTPUT.name,"sha256":sha(OUTPUT),"bytes":OUTPUT.stat().st_size,"source_sha256":sha(source),
              "settings_sha256":sha(SETTINGS_PATH),"renderer_sha256":sha(Path(__file__)),
              "v1_settings_sha256":sha(BASE_DIR/"scene-plan.json"),"v1_renderer_sha256":sha(BASE_DIR/"render_portal.py"),
              "decoded_frames":frames,"dimensions":[width,height],"fps":fps,"audio":False,"loop":False,
              "all_protected_pixels_exact_before_encode":True,"source_taps_inside_aperture":True,
              "minimum_warp_jacobian":min(jacobians),"peak_blue_lift_on_landing_codes":max(spill_peaks),"user_review":"pending"}
    (HERE/"delivery.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
