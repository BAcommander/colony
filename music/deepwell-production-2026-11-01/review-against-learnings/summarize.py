from pathlib import Path
import json, numpy as np
H=Path(__file__).resolve().parent;P=H.parent;R=P.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
rows=[]
for name,title,gain in [('waterworks','Waterworks Gallery',-8.35),('sheltered','Sheltered Replenishment',-6.8)]:
 for scope in ['full','body']:
  report=read(H/(name+'-'+scope)/'analysis.json');m=report['measurements'];v=np.array([r['rms_dbfs'] for r in m['timeline']]);b=list(m['band_energy_percent'].values())
  rows.append({'name':title,'scope':scope,'seconds':m['decoded_duration_seconds'],'raw_lufs':m['integrated_lufs'],'source_gain_db_in_mix':gain,'approx_lufs_after_fixed_gain':m['integrated_lufs']+gain,'lra':m['loudness_range_lu'],'sub80_percent':b[0],'80_250_percent':b[1],'250_1k_percent':b[2],'above1k_percent':sum(b[3:]),'stereo_correlation':m['stereo_correlation'],'side_percent':m['side_energy_percent'],'median_abs_1s_change_db':float(np.median(abs(np.diff(v)))),'p95_abs_1s_change_db':float(np.percentile(abs(np.diff(v)),95)),'recurrence':m['recurrence_candidates'],'source_hash':report['source']['sha256']})
reference=read(R/'creative/music/reference-analysis/comparison-2026-10-30/comparison.json')['tracks']
recipe=read(P/'delivery-hour-v1/mix-recipe.json');music=recipe['music_schedule']
starts={name:[s['start'] for s in music if s['track']==name] for name in ['A','B']}
intervals={name:list(np.diff(values).astype(int).tolist()) for name,values in starts.items()}
assert intervals['A'][0]==392 and set(intervals['A'][1:])=={388} and set(intervals['B'])=={388}
out={'date':'2026-11-01','scope':'Waterworks Gallery and Sheltered Replenishment, original dry sources plus equal interior windows; unchanged released mix assessed separately.','new_tracks':rows,'archived_comparators':reference,'rendered_mix':read(P/'delivery-hour-v1/delivery-validation.json')['full_mix_measurements'],'music_recurrence':{'first_A_restart_seconds':392,'subsequent_cycle_seconds':388,'cycle_display':'6:28','segment_start_intervals':intervals,'sfx_schedule':'Water/wind/pump timing varies separately; this changes the combined texture but does not remove recurring dry music.','source_internal_loop_result':'Waterworks feature candidates lack consistent strong waveform confirmation; Sheltered has no candidate in this bounded test. Neither result proves absence of internal repetition.'},'limits':['Four-minute dry sources versus archived thirty-minute published mixes including SFX; not identical duration or treatment.','160-second windows from20–180s exclude source entrance and ending fades; LRA is duration sensitive and not a tempo score.','FFmpeg9 used now versus7.1 in archived comparison; same analysis functions and spectral method.','No assistant listening/instrument/vocal identification or retention prediction. User accepted the mix; no full-hour listening result recorded.','Correlation and band-energy percentages are descriptors, not quality targets. Listening ratings override resemblance to WINTER WATCH.']}
(H/'comparison.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'tracks':rows,'music_recurrence':out['music_recurrence'],'final_mix':out['rendered_mix']},indent=2))
table='| Track / window | LRA (LU) | <80 Hz | 80–250 Hz | 250 Hz–1 kHz | >1 kHz | Stereo correlation | Median 1s change |\n|---|---:|---:|---:|---:|---:|---:|---:|\n'
for x in rows:
 table+=f"| {x['name']} ({x['scope']}) | {x['lra']:.1f} | {x['sub80_percent']:.3f}% | {x['80_250_percent']:.1f}% | {x['250_1k_percent']:.1f}% | {x['above1k_percent']:.2f}% | {x['stereo_correlation']:.3f} | {x['median_abs_1s_change_db']:.2f} dB |\n"
for x in reference:
 if x['id'] in ['reference','rainline','shoreless','spirewatch']:
  b=x['bands_percent'];table+=f"| {x['name']} (archived30min mix) | {x['lra']:.1f} | {b[0]:.2f}% | {b[1]:.1f}% | {b[2]:.1f}% | {sum(b[3:]):.2f}% | {x['stereo_correlation']:.3f} | {x['median_absolute_1s_level_change_db']:.2f} dB |\n"
report='''# Deepwell — comparison against this week’s learnings

The accepted mix does not need a speculative bass cut or stereo treatment based on these numbers. Both sources are near-zero in sub-bass, with most energy below1kHz. That is very different from sub-heavy Ringfall and closer in broad distribution to the preferred Rainline/Shoreless direction. This does not prove the same perceived pace or comfort. The main remaining listening question is whether recognizable musical detail becomes tiring when the6:28 dry cycle returns.

## Measurements

Full means each original four-minute dry source. Body means source20–180s (160seconds), excluding entrance and terminal fades. Comparators are archived thirty-minute published/reference mixes including any SFX. Energy is not perceived loudness; correlation is not a quality score. Same analyser functions, using installed FFmpeg9 instead of archived7.1. Original script preserved; only FFmpeg path discovery adapted locally.

'''+table+'''
## Findings

- **Waterworks Gallery:** 73.3% of energy in250Hz–1kHz, stereo correlation0.744. More midrange concentrated and more similar left/right channels than Sheltered. Its interior LRA4.4LU retains movement; do not call it static. Its correlation resembles Spirewatch’s0.724, but this cannot imply Spirewatch’s rejected fast musical pace. Audition for a persistent midrange figure or a centred sound becoming tiring; do not widen or brighten automatically.
- **Sheltered Replenishment:** 43.0% in80–250Hz and56.6% in250Hz–1kHz; correlation0.525. It supplies relatively more low-mid weight and channel difference. Full-source LRA9.8LU falls to3.2LU in the interior window: the apparent high range is strongly influenced by its ending fade, not evidence of huge internal swells. Accepted assembly trims/overlaps the generated tails.
- **Bass and level:** both have less than0.01% energy below80Hz, unlike Ringfall’s70.5%. A blanket bass cut is unsupported. Final accepted hour is−22.71LUFS,4.3LU LRA,−9.41dBTP before the video’s opening envelope. Video audio has already passed complete source/envelope comparison. No new normalization or processing applied.
- **Recurrence:** the recipe repeats the A/B dry arrangement every388seconds (6:28) after the initial entrance. Water, wind and pump use a separate staggered schedule; this varies the composite but does not erase the music’s recurrence. Waterworks’~53second feature candidate does not have consistently strong waveform matches; Sheltered has no candidate in this search. Do not claim an internal loop, or claim either source has no repetition.
- **Our actual preference evidence:** Rainline/Shoreless/WINTER WATCH tied at4/5; Spirewatch scored3/5 and was “too fast really to be ambient”. Ringfall’s diagnostic bass cut did not improve its3.5/5 rating. Those user ratings outweigh spectral similarity. Here the user accepted the current Deepwell balance and requested the hour/video, but no30–60minute work-session verdict is recorded.

## Decision

Keep the accepted export. Listen for recognition/fatigue over30–60minutes while working; the dry arrangement returns at roughly6½minute intervals. A short-window waveform metric cannot establish whether music is too busy, whether a foreground melody distracts, or whether voices are present. No assistant listening verdict or retention improvement is claimed. Reopen the mix only for a concrete audible issue, not to force the WINTER WATCH numbers.

## Detailed reports

- [Waterworks complete source](waterworks-full/report.html), [interior window](waterworks-body/report.html)
- [Sheltered complete source](sheltered-full/report.html), [interior window](sheltered-body/report.html)
- [Exact comparison and recipe evidence](comparison.json), [method adapter](method-adapter.json)
- Earlier ratings: creative/music/reference-analysis/comparison-2026-10-30/feedback-2026-10-30/README.md

Source files and exported audio/video are unchanged. No paid generation, publication or Git action.
'''
(H/'REPORT.md').write_text(report,encoding='utf-8')
if __name__=='__main__':pass
