from pathlib import Path
import json

root = Path('G:/AI/colony')
brief = 'music/spirewatch-animation-v1/improvement-audit/v2-improvement-brief.txt'
p = root / 'music/digital-city-concepts-v1/current-direction.json'
d = json.loads(p.read_text(encoding='utf-8'))
d['status'] = 'User says v1 needs substantial improvement; audit and v2 proposal saved; v2 not rendered'
d['user_motion_approved'] = False
d['improvement_brief'] = brief
d['latest_feedback'] = 'this scene feels like theres ALOT of improvements needed, can you think long and hard and figure out how we can improve things 500%'
p.write_text(json.dumps(d, indent=2) + '\n', encoding='utf-8')

p = root / 'music/spirewatch-animation-v1/README.md'
s = p.read_text(encoding='utf-8')
s = s.replace('## Implemented', '## Current user verdict — 2026-10-10\n\nUser says the scene needs substantial improvement. V1 is an unapproved checkpoint. The [audit and proposed v2 rebuild](improvement-audit/v2-improvement-brief.txt) prioritizes flowing waterfall material, crisp basin detail, atmospheric depth, restrained city transit and readable room activity. Findings are based on code and twelve decoded-frame samples, not continuous playback. Proposed changes are not implemented.\n\n## Implemented', 1)
s = s.replace('User motion review remains pending.', 'User has reviewed the scene and says substantial improvement is needed; no positive motion verdict is recorded.')
p.write_text(s, encoding='utf-8')

p = root / 'PRODUCTION_PIPELINE.md'
s = p.read_text(encoding='utf-8')
a = s.index('## Unnumbered city concept — Spirewatch')
b = s.index('## Next concept exploration', a)
s = s[:a] + '''## Unnumbered city concept — Spirewatch

2026-10-10: user says the [v1 minute draft](music/spirewatch-animation-v1/README.md) needs substantial improvement. Preserve it as an unapproved checkpoint. [Audit and v2 proposal](music/spirewatch-animation-v1/improvement-audit/v2-improvement-brief.txt) identifies fixed waterfall streaks beneath brightness modulation, softened basin detail, restricted low-atmosphere coverage and underused city/room activity. These are assistant diagnoses from code and twelve decoded-frame samples; the user gave an overall verdict rather than these specific defects. Next: short principal-motion proofs, then a combined candidate and genuine minute v2. V2 has not been rendered. Technical v1 checks remain valid but do not establish artistic quality. Source remains the cleaned 1672x941 artwork; 4K, long music and assembly are separate. Vast Unfamiliar World remains a short musical direction. No catalog number assigned; Farpoint and releases 11–14 are unchanged.

''' + s[b:]
p.write_text(s, encoding='utf-8')

p = root / 'AGENTS.md'
s = p.read_text(encoding='utf-8')
a = s.index('Current Spirewatch animation (2026-10-10):')
b = s.index('\n\n', a)
s = s[:a] + '''Current Spirewatch animation (2026-10-10): user says v1 needs substantial improvement and requests a deep improvement proposal. Preserve music/spirewatch-animation-v1/ as an unapproved checkpoint. Audit and proposed v2 are at music/spirewatch-animation-v1/improvement-audit/v2-improvement-brief.txt. Assistant inspected renderer and twelve colour-aware decoded-frame samples, not continuous playback. Diagnoses: moving brightness over fixed waterfall streaks; softened basin reflections; conservative skyline/mountain exclusions restricting low mist; tiny window/screen activity while dominant routes/spire remain static. The user did not identify these individual defects; distinguish diagnosis from their general negative verdict. Proposed rebuild: flowing waterfall material and restrained spray, crisp calm basin reflections, depth-separated clouds/mist, carefully mapped sparse transit, distributed occupancy and readable map activity. These remain proposals, not implemented/approved presets; first make short principal-motion proofs. Same immutable cleaned source hash 22553e407a8aac902a7eb55ddf52d544752a642856b3265ef2368741a0eadcba, native 1672x941. V1 minute/repeat decode, source protection and loop checks remain valid but do not prove visual quality. No v2, 4K, extended audio, assembly, commit or push in the audit turn. Unnumbered concept; other releases unchanged.''' + s[b:]
p.write_text(s, encoding='utf-8')

p = root / 'creative/ANIMATION_KNOWLEDGE_BANK.md'
s = p.read_text(encoding='utf-8')
s = s.replace('[Unnumbered v1 draft](../music/spirewatch-animation-v1/README.md), user review pending.', '[Unnumbered v1 draft](../music/spirewatch-animation-v1/README.md): user now says substantial improvement is needed; unapproved checkpoint.')
s = s.replace('this distinguishes positional flow from pure brightness pulsing but does not establish natural-looking playback.', 'this measures the downward-moving brightness field, while the photographed streaks themselves remain fixed. It does not establish natural-looking water flow.')
needle = 'Candidate methods are not accepted visual presets.'
pos = s.index(needle, s.index('## Spirewatch waterfall candidate')) + len(needle)
s = s[:pos] + '''

Follow-up audit: [v2 improvement brief](../music/spirewatch-animation-v1/improvement-audit/v2-improvement-brief.txt). Code and twelve decoded-frame samples indicate that multiplicative waterfall density retains static material features and reconstructed basin patches soften fine reflections. Conservative geometry exclusions also restrict low-atmosphere coverage. Tiny lamps/markers do not establish full-composition habitation when the dominant transport corridor remains static. Proposed fixes are transported waterfall detail with restrained spray, detail-preserving calm reflections, depth-specific mist and carefully mapped transit/monitor events. No fixes implemented yet. Do not promote these diagnoses to user-specific complaints or the proposals to accepted techniques. Prioritize short material-motion proofs and compare source sharpness before a full-minute render. "500%" is an ambition, not a measured claim.
''' + s[pos:]
p.write_text(s, encoding='utf-8')
print('Updated Spirewatch feedback, production state and knowledge bank; preserved media and technical delivery records.')
