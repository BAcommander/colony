from pathlib import Path
import hashlib
import json

root = Path('G:/AI/colony')
folder = root / 'final/07-icebound-weather-post/music'
prompt = '''Instrumental only, 60 seconds. Melodic space ambient with warm analog synth chords, a soft rounded synth lead and a gently moving bass line. Spacious, smooth and richly layered. Mood: quiet companionship and distant wonder during a winter night at an inhabited colony.

Begin with a complete musical texture: a warm chord, its bass note and a clear three-note melodic phrase. Move through a slow four-chord progression, changing harmony roughly every eight to twelve seconds. Let the bass follow the chord changes while inner voices move independently. Around 15 seconds, answer the opening phrase with a different ending. Around 30 seconds, introduce a soft string-like synth countermelody in a separate register. Around 45 seconds, return to the opening idea with a new voicing and a small melodic variation. Leave breathing space between phrases while the harmony continues underneath.

Keep the music gentle and flowing, with audible chord changes and a melody clear at low volume. Use modest bass, smooth treble and spacious reverb that preserves note definition. Keep the level even and end on a continuing musical phrase.

No vocals, drums, percussion, sound effects, noise beds, static drones, risers or climaxes.
'''
target = folder / 'elevenlabs-prompt-v3.txt'
assert not target.exists(), 'Preserve existing v3 if present'
files = [Path('C:/Users/jazzs/Downloads') / name for name in [
    'Inhabited_Outpost_Beside_the_Frozen_Sea_2026-10-04T153447.mp4',
    'Station_Under_the_Ringed_Moon_2026-10-04T153447.mp4']]
sources = [{'path': p.as_posix(), 'bytes': p.stat().st_size,
            'sha256': hashlib.file_digest(p.open('rb'), 'sha256').hexdigest()}
           for p in files]
feedback = "this prompt is not good the sfx is like the same sound for the whole minute, it's boring and doesn't work"
target.write_text(prompt, encoding='utf-8')
record_path = folder / 'generation-record.json'
record = json.loads(record_path.read_text(encoding='utf-8-sig'))
record.update(status='Two user-supplied v2 short tests rejected; revised v3 short prompt awaiting generation',
              short_test_files=sources, user_feedback=feedback, selected_test=None,
              audio_approval=False, current_short_prompt=target.name,
              feedback_date='2026-10-04', assistant_listened=False,
              assessment_basis='User listening feedback and review of the v2 prompt; no audio analysis or assistant listening claimed',
              long_prompt_status='Historical v2 prompt retained; revise after a new short test is selected')
record_path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
readme = folder / 'README.md'
s = readme.read_text(encoding='utf-8-sig')
s = s.replace('Status: v1 prompts prepared 2026-09-28, rewritten as v2 on 2026-09-29; no audio generated or evaluated for this scene. These are musical design choices, not measurements of a reference recording.',
              'Status 2026-10-04: user supplied two v2 short tests and rejected the persistent, repetitive SFX-like sound. Current short prompt is v3, awaiting generation and listening review. No test is selected. Assistant has not listened to these files.')
s = s.replace('Paste `elevenlabs-prompt-v2.txt`', 'Paste `elevenlabs-prompt-v3.txt`')
s = s.replace('For the chosen user-generated test, use the available audio-reference control and `elevenlabs-long-version-v2.txt`. Aim for roughly five minutes and one variant if supported; follow the actual interface and reference limits. A reference guides feel and palette, not exact continuation.',
              'After a revised short test is selected, prepare a matching longer prompt. The saved v2 long prompt is historical and carries the rejected airy-texture direction; do not use it for the revised direction yet. A reference guides feel and palette, not exact continuation.')
s = s.replace('The files currently contain null values because nothing has been generated.', 'The record now contains the two supplied test paths, hashes and rejection feedback; unknown settings remain null.')
s = s.replace('Current: `elevenlabs-prompt-v2.txt` and `elevenlabs-long-version-v2.txt` (2026-09-29), written to the prompt writing rules in creative/MUSIC_WORKFLOW.md. `elevenlabs-prompt-v1.txt` and `elevenlabs-long-version.txt` are preserved history. Neither version has been generated or heard.',
              'Current short prompt: `elevenlabs-prompt-v3.txt` (2026-10-04). V1/v2 prompts are preserved. V2 short tests were rejected by the user; v3 is untested. The new direction replaces the air-like noise bed and rare accents with a changing four-chord progression, bass movement, a three-note phrase with varied replies and a later countermelody. This is a proposed correction based on feedback, not a claim about the generated audio. See generation-record.json for the exact feedback and supplied file hashes.')
readme.write_text(s, encoding='utf-8')
pipeline = root / 'PRODUCTION_PIPELINE.md'
s = pipeline.read_text(encoding='utf-8-sig')
lines = s.splitlines()
for i, line in enumerate(lines):
    if '| 07 |' in line:
        assert 'Short/long prompts ready; no audio' in line
        lines[i] = line.replace('Short/long prompts ready; no audio', 'Two v2 tests rejected as repetitive/SFX-like; v3 melodic prompt ready, untested').replace('run music tests separately', 'audition revised v3 music direction')
pipeline.write_text('\n'.join(lines) + '\n', encoding='utf-8')
agents = root / 'AGENTS.md'
s = agents.read_text(encoding='utf-8-sig')
note = 'Current Icebound music (2026-10-04): user supplied Inhabited Outpost Beside the Frozen Sea and Station Under the Ringed Moon v2 short tests, rejecting the persistent repetitive SFX-like sound as boring. Exact feedback, original download paths and SHA-256 hashes are saved in final/07-icebound-weather-post/music/generation-record.json. Current short prompt is elevenlabs-prompt-v3.txt: audible chord progression, moving bass, a small melodic phrase with varied replies and later countermelody; no noise bed/static drone. This proposed correction is ungenerated and unapproved. V1/v2 prompts and supplied originals remain unchanged. Revise the historical v2 long prompt only after a new short test is selected. No assistant listening, audio measurements, paid generation, commit or push claimed.\n\n'
assert 'Current Icebound music (2026-10-04)' not in s
first_break = s.index('\n') + 1
agents.write_text(s[:first_break] + '\n' + note + s[first_break:].lstrip('\n'), encoding='utf-8')
print(f'Saved {target}; {len(prompt.strip())} prompt characters. Recorded both rejected tests and updated current status.')
