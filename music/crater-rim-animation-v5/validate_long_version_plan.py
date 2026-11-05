"""Check the saved continuation recipe and restore the frozen V5 baseline; build no long video."""
import argparse
import hashlib
import json
from pathlib import Path

from render_scene import HERE, ROOT, Scene


def digest(path):
    with path.open('rb') as data:
        return hashlib.file_digest(data, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    path = HERE/'long-version-plan.json'
    plan = json.loads(path.read_text(encoding='utf-8'))
    assert plan['status'] == 'proposed_continuation_plan_not_implemented'
    assert plan['duration']['proposed_visual_schedule_seconds'] == 600
    assert plan['duration']['proposed_visual_schedule_frames'] == 600*30
    assert plan['duration']['final_program_seconds'] is None
    for relative, expected in plan['baseline']['reference_inputs'].items():
        assert digest(ROOT/relative) == expected, relative
    for media in plan['baseline']['reference_media']:
        assert digest(HERE/media['path']) == media['sha256'], media['path']
    scene = Scene()
    events = plan['attention_events']
    windows = []
    for cluster in events['lamp_clusters']:
        assert len(cluster['source_event_indices']) == len(cluster['relative_offsets'])
        for index, offset in zip(cluster['source_event_indices'], cluster['relative_offsets']):
            source = scene.c['lamp']['events'][index]
            start = cluster['start']+offset
            windows.append(('lamp', start, start+source['rise']+source['hold']+source['fall']))
    for event in events['greenhouse_glints']:
        source = scene.c['sun_glare']['events'][event['source_variant_index']]
        windows.append(('glint', event['start'], event['start']+source['rise']+source['hold']+source['fall']))
    for event in events['traffic_passages']:
        source = scene.c['traffic']['events'][event['source_variant_index']]
        windows.append(('traffic', event['start'], event['start']+source['seconds']))
    assert len(windows) == 10
    assert all(5 < start < end < 590 for _, start, end in windows)
    traffic = sorted((start, end) for name, start, end in windows if name == 'traffic')
    assert all(a[1] < b[0] for a, b in zip(traffic, traffic[1:]))
    assert all(start % 60 != 0 for _, start, _ in windows)
    # This tests the restored baseline and dependencies, not an unbuilt 600s renderer.
    frames = [scene.frame(t) for t in [0, 14.3, 19.8, 21.8, 48.5, 59+29/30]]
    assert all(frame.shape == (941, 1672, 3) for frame in frames)
    for control, frame in zip(plan['baseline']['native_resume_controls'], frames):
        assert hashlib.sha256(frame.tobytes()).hexdigest() == control['rgb_sha256'], control['time_seconds']
    manifest = json.loads((ROOT/'final/14-crater-rim-survey/manifest.json').read_text(encoding='utf-8'))
    brief = manifest['motion_preparation']['brief']
    assert digest(ROOT/brief['path']) == brief['sha256']
    assert manifest['long_version_preparation']['plan_sha256'] == digest(path)
    assert scene.duration == 60
    report = {'status': 'passed', 'long_renderer_implemented': False,
              'long_schedule_playback_approved': False, 'v5_source_inputs_and_two_media_hashes_verified': True,
              'baseline_native_frames_rendered': 6, 'plan_sha256': digest(path),
              'all_six_native_rgb_controls_exact': True, 'scene_manifest_plan_and_brief_hashes_valid': True,
              'attention_windows_seconds': windows, 'quiet_600s_join_in_draft_schedule': True,
              'final_runtime_and_soundtrack_pending': True}
    if not args.check_only:
        (HERE/'continuation-plan-validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
