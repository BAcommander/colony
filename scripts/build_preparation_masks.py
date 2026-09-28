"""Rasterize draft source-coordinate effect masks; never modifies the source artwork.

Usage: python scripts/build_preparation_masks.py final/04-floodplain-keeper/animation-prep-v1/scene-plan.json
These are planning masks, not a connected animation renderer or certified segmentation.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def draw(mask, shape, value):
    if shape['type'] == 'polygon':
        cv2.fillPoly(mask, [np.asarray(shape['points'], dtype=np.int32)], value)
    elif shape['type'] == 'ellipse':
        cv2.ellipse(mask, tuple(shape['center']), tuple(shape['radii']), 0, 0, 360, value, -1)
    else:
        raise ValueError(f"Unknown shape: {shape['type']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    args = parser.parse_args()
    plan_path = args.plan.resolve()
    root = Path(__file__).resolve().parents[1]
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    source = root / plan['source']['path']
    if sha(source) != plan['source']['sha256']:
        raise ValueError('Source hash changed: remap masks before continuing')
    with Image.open(source) as im:
        w, h = im.size
    if [w, h] != plan['source']['dimensions']:
        raise ValueError('Source dimensions changed')
    report = {'status': 'draft mask rasterization verified; visual edge review pending',
              'source_sha256': sha(source), 'plan_sha256': sha(plan_path),
              'dimensions': [w, h], 'animation_rendered': False, 'masks': []}
    for layer in plan['layers']:
        mask = np.zeros((h, w), dtype=np.uint8)
        for shape in layer['include']:
            draw(mask, shape, 255)
        for shape in layer['exclude']:
            draw(mask, shape, 0)
        if not np.any(mask):
            raise ValueError(f"Empty mask: {layer['name']}")
        path = plan_path.parent / layer['mask_path']
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(mask).save(path)
        with Image.open(path) as check:
            if not np.array_equal(np.asarray(check), mask):
                raise ValueError('Mask round-trip failed')
        report['masks'].append({'name': layer['name'], 'path': layer['mask_path'],
                                'sha256': sha(path), 'active_pixels': int(np.count_nonzero(mask))})
    (plan_path.parent / 'preparation-validation.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f"{plan['scene_name']}: {len(report['masks'])} draft masks saved; source hash verified")


if __name__ == '__main__':
    main()
