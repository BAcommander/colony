"""Configurable layered local animation for Ringfall. No network calls.

python scripts/render_ringfall_v6.py --stage preview --version v6-a
python scripts/render_ringfall_v6.py --stage final --version v6-a
python scripts/render_ringfall_v6.py --qa-only
python scripts/render_ringfall_v6.py --only planet_atmosphere --version planet-test
"""
from pathlib import Path
import argparse
import json
import hashlib
import cv2
import numpy as np
from PIL import Image, ImageDraw
import render_ringfall as core

ROOT = core.ROOT
OUT = core.OUTPUT
CONFIG = ROOT / "creative/ringfall/animation/scene-v6.json"
LAYERS = ["planet_atmosphere", "colony_work_lights", "window_reflections",
          "coffee_steam", "laptop_scan", "mast_beacon"]


def smooth_mask(shape, polygons, origin, feather):
    mask = np.zeros(shape, np.uint8)
    for polygon in polygons:
        points = np.array(polygon, np.int32) - np.array(origin, np.int32)
        cv2.fillPoly(mask, [points], 255)
    distance = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    a = np.clip(distance / feather, 0, 1)
    return a * a * (3 - 2 * a)


class LivingRingfall(core.Ringfall):
    def __init__(self, enabled=None):
        super().__init__()
        self.config = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.enabled = set(enabled or LAYERS)
        self.rois = {}
        self.grids = {}
        self.masks = {}
        self.layer_masks = {}
        for name, section in [("planet_atmosphere", "planet"),
                              ("colony_work_lights", "colony"),
                              ("window_reflections", "window")]:
            c = self.config[section]
            x0, y0, x1, y1 = c["roi"]
            shape = (y1 - y0, x1 - x0)
            yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            self.rois[name] = (x0, y0, x1, y1)
            self.grids[name] = (xx, yy)
            if section == "planet":
                mask = smooth_mask(shape, [c["surface_polygon"]], (x0,y0), c["feather_pixels"])
                rings = smooth_mask(shape, [c["protected_rings_polygon"]], (x0,y0), 1)
                # Feather away from protected rings without changing any ring pixel.
                clear = (rings == 0).astype(np.uint8)
                ring_distance = cv2.distanceTransform(clear, cv2.DIST_L2, 5)
                mask *= np.clip((ring_distance - 3) / 9, 0, 1)
                patch = self.base[y0:y1,x0:x1].astype(np.float32)
                # Directional separation keeps the near-vertical lighting terminator
                # in the static shading while extracting horizontal cloud-band detail.
                self.shading = cv2.GaussianBlur(patch, (0,0), sigmaX=c["shading_sigma"][0], sigmaY=c["shading_sigma"][1])
                self.planet_detail = patch - self.shading
            elif section == "colony":
                mask = smooth_mask(shape, c["ground_polygons"], (x0,y0), c["feather_pixels"])
                blockers = smooth_mask(shape, c["rock_occluders"], (x0,y0), 1)
                mask *= 1 - blockers
            else:
                mask = smooth_mask(shape, [c["glass_polygon"]], (x0,y0), 5)
            self.masks[name] = mask.astype(np.float32)
            full = np.zeros(self.base.shape[:2], bool)
            full[y0:y1,x0:x1] = mask > 0
            self.layer_masks[name] = full
        for name, box in [("coffee_steam", self.steam_box), ("laptop_scan", self.screen_box), ("mast_beacon", self.beacon_box)]:
            full = np.zeros(self.base.shape[:2], bool)
            x0,y0,x1,y1 = box
            full[y0:y1,x0:x1] = True
            self.layer_masks[name] = full
        self.active = np.logical_or.reduce([self.layer_masks[k] for k in self.enabled])
        self.effect_descriptions = {
            "planet_atmosphere": "Masked periodic cloud-detail advection with fixed shading, rings and silhouette",
            "colony_work_lights": "Two textured warm pools sweeping over terrain with occlusion masks",
            "window_reflections": "Broad faint glass reflections driven by the work-light phases",
            "coffee_steam": "Overlapping advected vapor volumes with continuous birth and dissipation",
            "laptop_scan": "Perspective-confined scan and telemetry",
            "mast_beacon": "Independent slow amber cycle"
        }

    def steam(self, phase):
        c = self.config["steam"]
        x0,y0,x1,y1 = self.steam_box
        yy,xx = np.mgrid[y0:y1,x0:x1].astype(np.float32)
        seconds = phase / core.TAU * 10
        density = np.zeros_like(xx)
        count = c["puff_count"]
        for i in range(count):
            # Each parcel rises monotonically then vanishes before wrapping.
            age = ((seconds / c["lifetime_seconds"]) + i / count) % 1
            envelope = np.sin(np.pi * age) ** 1.6
            cy = 513 - c["height"] * age
            cx = 250 + age * (9 * np.sin(6.0 * age + i * 1.9) + 7 * np.sin(phase + i * 2.3))
            sx = 1.6 + 7.5 * age
            sy = 6 + 11 * age
            u = (xx - cx - 3 * age * np.sin((yy-cy)/10 + phase)) / sx
            v = (yy-cy) / sy
            puff = np.exp(-0.5 * (u*u + v*v))
            density += c["opacity"] * envelope * puff * (0.6 + 0.2 * np.sin(i * 2.4))
        # Smooth spatial boundary, especially where emission meets the mug rim.
        h = np.clip((515 - yy) / 145, 0, 1)
        density *= np.minimum(1, h * 14) * np.minimum(1, (1-h)*9)
        density *= np.clip((xx-x0)/6,0,1) * np.clip((x1-1-xx)/6,0,1)
        return np.clip(cv2.GaussianBlur(density,(0,0),0.9),0,0.34)

    def frame(self, t, output_size=True):
        phase = self.phase(t)
        # Preserve already-implemented foreground effects without duplicating code.
        frame = super().frame(t, False)
        for name in ["coffee_steam", "laptop_scan", "mast_beacon"]:
            if name not in self.enabled:
                m = self.layer_masks[name]
                frame[m] = self.base[m]

        if "planet_atmosphere" in self.enabled:
            name = "planet_atmosphere"
            x0,y0,x1,y1 = self.rois[name]
            xx,yy = self.grids[name]
            c = self.config["planet"]
            u = (xx - 1158) / 194
            v = (yy - 235) / 150
            # Elliptical local trajectories with spatial phase variation. No global reversal.
            dx = c["flow_x_pixels"] * (0.72*np.sin(phase+v*3.5) + 0.28*np.sin(2*phase+v*7+u*2))
            dy = c["flow_y_pixels"] * (0.7*np.cos(phase+v*3.5) + 0.3*np.sin(2*phase+u*5))
            map_x = (xx-x0+dx).astype(np.float32)
            map_y = (yy-y0+dy).astype(np.float32)
            warped = cv2.remap(self.planet_detail, map_x, map_y, cv2.INTER_CUBIC,
                               borderMode=cv2.BORDER_REFLECT_101)
            patch = self.base[y0:y1,x0:x1].astype(np.float32)
            delta = (warped - self.planet_detail) * c["detail_gain"]
            # Both ends of every sample must stay inside the atmospheric mask.
            # This prevents pulling sky, rings or the silhouette into the cloud layer.
            valid_sample = cv2.remap(self.masks[name],map_x,map_y,cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_CONSTANT,borderValue=0)
            mask = (self.masks[name] * valid_sample)[...,None]
            frame[y0:y1,x0:x1] = np.rint(np.clip(patch + delta*mask,0,255)).astype(np.uint8)

        if "colony_work_lights" in self.enabled:
            name = "colony_work_lights"
            x0,y0,x1,y1 = self.rois[name]
            xx,yy = self.grids[name]
            patch = frame[y0:y1,x0:x1].astype(np.float32)
            illumination = np.zeros_like(xx)
            for lamp in self.config["colony"]["lights"]:
                p = phase + lamp["phase"]
                cx = lamp["center"][0] + lamp["travel"][0]*np.sin(p)
                cy = lamp["center"][1] + lamp["travel"][1]*np.cos(p)
                dx = (xx-cx) / lamp["width"][0]
                dy = (yy-cy+0.035*(xx-cx)) / lamp["width"][1]
                illumination += lamp["gain"]*np.exp(-0.5*(dx*dx+dy*dy))
            illumination *= self.masks[name]
            # Multiplication preserves the actual terrain texture, plus modest bounce.
            warm = np.array([1.0,0.65,0.30],np.float32)
            patch += illumination[...,None]*(patch*0.70+8)*warm
            frame[y0:y1,x0:x1] = np.rint(np.clip(patch,0,255)).astype(np.uint8)

        if "window_reflections" in self.enabled:
            name = "window_reflections"
            x0,y0,x1,y1 = self.rois[name]
            xx,yy = self.grids[name]
            alpha = np.zeros_like(xx)
            for reflection in self.config["window"]["reflections"]:
                lamp = self.config["colony"]["lights"][reflection["light_index"]]
                p = phase + lamp["phase"]
                cx = reflection["center"][0] - 25*np.sin(p)
                cy = reflection["center"][1] + 7*np.cos(p)
                dx = (xx-cx + 0.07*(yy-cy)) / reflection["width"][0]
                dy = (yy-cy) / reflection["width"][1]
                alpha += reflection["opacity"] * (0.65+0.35*np.cos(p)) * np.exp(-0.5*(dx*dx+dy*dy))
            alpha *= self.masks[name]
            patch = frame[y0:y1,x0:x1].astype(np.float32)
            warm = np.array([214,180,125],np.float32)
            frame[y0:y1,x0:x1] = np.rint(patch*(1-alpha[...,None])+warm*alpha[...,None]).astype(np.uint8)

        return cv2.resize(frame,core.SIZE,interpolation=cv2.INTER_LANCZOS4) if output_size else frame

    def save_masks(self):
        folder = OUT / "masks-v6"
        folder.mkdir(exist_ok=True)
        overlay = self.base.astype(np.float32)
        colors = [(100,170,255),(255,176,60),(180,110,230)]
        for (name,mask),color in zip(self.masks.items(),colors):
            x0,y0,x1,y1 = self.rois[name]
            full = np.zeros(self.base.shape[:2],np.uint8)
            full[y0:y1,x0:x1] = np.rint(mask*255).astype(np.uint8)
            Image.fromarray(full).save(folder / f"{name}.png")
            a = mask[...,None]*0.45
            overlay[y0:y1,x0:x1] = overlay[y0:y1,x0:x1]*(1-a)+np.array(color)*a
        Image.fromarray(np.uint8(overlay)).save(folder / "mask-overlay.png")


def qa(anim):
    anim.save_masks()
    times = [0,2,4,6,8]
    montage = Image.new("RGB",(1280,720*3),(15,18,23))
    for i,t in enumerate(times):
        im = Image.fromarray(anim.frame(t,False)).resize((640,360),Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(im)
        draw.rectangle((0,0,100,23),fill=(15,18,23))
        draw.text((8,5),f"{t}s / full scene",fill="white")
        montage.paste(im,((i%2)*640,(i//2)*720))
        crop = Image.fromarray(anim.frame(t,False)).crop((960,127,1355,348)).resize((640,360))
        montage.paste(crop,((i%2)*640,(i//2)*720+360))
    montage.save(OUT/f"{core.STEM}-temporal-review.png")
    Image.fromarray(anim.frame(2)).save(OUT/f"{core.STEM}-poster.png")
    # Per-layer change diagnostics are independent of full-scene aggregate motion.
    metrics = {}
    for layer in LAYERS:
        if layer not in anim.enabled:
            continue
        isolated = LivingRingfall([layer])
        m = isolated.layer_masks[layer]
        samples = [isolated.frame(t,False).astype(np.float32) for t in [0,0.0333333333,2,4,6,8,9.9666666667,10]]
        assert np.array_equal(samples[0],samples[-1]), layer
        assert all(np.array_equal(f[~m],isolated.base[~m]) for f in samples), f"Mask leak: {layer}"
        change = np.abs(samples[2]-samples[0]).max(axis=2)
        metrics[layer] = {
            "mean_0_to_2s_change_in_mask": float(change[m].mean()),
            "pixels_changing_by_over_3_levels": int((change>3).sum()),
            "seam_mean_rgb_change": float(np.abs(samples[-2]-samples[0])[m].mean()),
            "periodic_endpoint_identical": True,
            "no_change_outside_layer_mask": True
        }
    (OUT/f"{core.STEM}-layer-checks.json").write_text(json.dumps(metrics,indent=2))
    print(json.dumps(metrics,indent=2),flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage",choices=["preview","final"],default="preview")
    parser.add_argument("--version",default="v6-a")
    parser.add_argument("--qa-only",action="store_true")
    parser.add_argument("--only",choices=LAYERS,nargs="+")
    args = parser.parse_args()
    if not args.version or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in args.version):
        parser.error("Invalid version label")
    core.SIZE = (1280,720) if args.stage=="preview" else (3840,2160)
    core.STEM = f"ringfall-{args.version}-{args.stage}"
    OUT.mkdir(exist_ok=True)
    destination = OUT/f"{core.STEM}.mp4"
    if destination.exists() and not args.qa_only:
        raise FileExistsError(destination)
    anim = LivingRingfall(args.only)
    qa(anim)
    if not args.qa_only:
        core.render(anim,destination)
        core.validate(anim,destination)
        manifest = {"config": str(CONFIG.relative_to(ROOT)),
                    "config_values": anim.config,
                    "config_sha256": hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
                    "renderer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    "shared_renderer_sha256": hashlib.sha256(Path(core.__file__).read_bytes()).hexdigest(),
                    "enabled_layers": sorted(anim.enabled),"output":str(destination.relative_to(ROOT)),
                    "source_is_native_4k":False,"stage":args.stage}
        (OUT/f"{core.STEM}-manifest.json").write_text(json.dumps(manifest,indent=2))


if __name__=="__main__":
    main()
