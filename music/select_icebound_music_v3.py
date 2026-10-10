from pathlib import Path
import json, hashlib

root = Path('G:/AI/colony')
folder = root / 'final/07-icebound-weather-post/music'
source = Path('C:/Users/jazzs/Downloads/Colony_Winter_Night_2026-10-04T154416.mp4')
with source.open('rb') as f:
    selected = {'path': source.as_posix(), 'bytes': source.stat().st_size, 'sha256': hashlib.file_digest(f, 'sha256').hexdigest()}
prompt = '''Instrumental only throughout, seven minutes. Use the reference for its instrumental palette, warmth, harmonic movement and spaciousness. Carry all melodic phrases on synthesizers, with no human voice.

Melodic space ambient: warm analog chords, a rounded synth lead, gently moving bass and soft string-like synth layers. Quiet companionship and distant wonder on a winter colony night.

Start with the chord progression, bass and a short synth melody already established. During the first two minutes, vary the melody's replies and chord voicings. From two to four minutes, introduce a gentle countermelody, then let it recede. From four to six minutes, explore related harmonies and alternate the lead with brief instrumental rests while the chords keep moving. In the final minute, return naturally to the opening palette with fresh phrasing, maintaining the same calm energy.

Clear midrange, modest bass, smooth treble and spacious reverb with distinct notes. Even level; end with the musical texture still moving, without a final cadence or fade to silence.

No vocals, lyrics, humming, choir, drums, sound effects, static drones or climaxes.
'''
target = folder / 'elevenlabs-long-version-v3.txt'
assert not target.exists()
target.write_text(prompt, encoding='utf-8')
p = folder / 'generation-record.json'
r = json.loads(p.read_text(encoding='utf-8-sig'))
r['feedback_history'] = [{'date': r['feedback_date'], 'prompt': 'elevenlabs-prompt-v2.txt', 'feedback': r['user_feedback'], 'selection': None}]
r['short_test_files'].append(selected)
r.update(status='Colony Winter Night selected for musical direction; unwanted lyrics reported; seven-minute instrumental generation pending',
         selected_test=selected, user_feedback="i like this one but it put some lyrics in it, i can turn that off and genereate the 6-7 minute version? i think i want it to be an hour",
         selected_direction_approved=True, audio_approval=False,
         approval_scope='Musical direction liked; vocals unwanted; no final instrumental or long audio approved',
         delivery_duration_seconds=3600, requested_source_duration_range_seconds=[360,420],
         current_long_prompt=target.name, long_prompt_status='V3 seven-minute instrumental prompt prepared; user generation pending')
p.write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
p = folder / 'README.md'
s = p.read_text(encoding='utf-8')
start = s.index('Status 2026-10-04:'); end = s.index('\n\n', start)
s = s[:start] + 'Status 2026-10-04: user selected Colony Winter Night for its musical direction but reported unwanted lyrics. Current longer prompt is elevenlabs-long-version-v3.txt, requesting seven instrumental minutes from the selected reference. One hour is the requested final delivery target. Long export and join review remain pending. Assistant has not listened to the supplied files.' + s[end:]
s = s.replace('After a revised short test is selected, prepare a matching longer prompt. The saved v2 long prompt is historical and carries the rejected airy-texture direction; do not use it for the revised direction yet. A reference guides feel and palette, not exact continuation.', 'Use Colony Winter Night as the reference, enable the instrumental-only setting and paste elevenlabs-long-version-v3.txt into the prompt field. Request seven minutes and one version. A reference guides feel and palette, not exact continuation. Review the new export for unwanted voices before looping.')
s = s.replace('No duration has been selected for this scene.', 'The user requested one hour for the final delivery.')
s = s.replace('The record now contains the two supplied test paths, hashes and rejection feedback; unknown settings remain null.', 'The record contains all three supplied test paths and hashes, rejected v2 feedback and the selected v3 direction; unknown settings remain null.')
s = s.replace('V2 short tests were rejected by the user; v3 is untested.', 'V2 short tests were rejected; the user liked the v3 direction in Colony Winter Night but reported lyrics. The v3 longer prompt is untested.')
s = s.replace('The long prompt says "about five minutes". If you choose ten minutes, edit that number before pasting.', 'The current long prompt requests seven minutes; the final local loop target is one hour.')
p.write_text(s, encoding='utf-8')
p = root / 'PRODUCTION_PIPELINE.md'
s = p.read_text(encoding='utf-8')
s = s.replace('Two v2 tests rejected as repetitive/SFX-like; v3 melodic prompt ready, untested', 'Colony Winter Night direction selected; vocals unwanted; seven-minute instrumental prompt ready; one-hour target')
s = s.replace('audition revised v3 music direction', 'await instrumental long export and audition join')
p.write_text(s, encoding='utf-8')
p = root / 'AGENTS.md'
s = p.read_text(encoding='utf-8'); start = s.index('Current Icebound music ('); end = s.index('\n\n', start)
s = s[:start] + 'Current Icebound music (2026-10-04): user selected Colony Winter Night for its musical direction but reported unwanted lyrics. Source download path/hash and exact feedback are in final/07-icebound-weather-post/music/generation-record.json. Current long prompt elevenlabs-long-version-v3.txt requests seven minutes with the selected reference and instrumental-only output. User requested a one-hour final delivery. Longer generation, vocal-free listening review, join audition and assembly remain pending. Earlier two v2 tests were rejected as repetitive/SFX-like; v1/v2 prompts and all originals remain preserved. Selection approves musical direction, not unwanted vocals or any long export. No assistant listening, paid generation, commit or push.' + s[end:]
p.write_text(s, encoding='utf-8')
print('Saved seven-minute instrumental prompt, selected source hash and one-hour delivery target.')
