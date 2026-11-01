# Below the Snowline — nine-minute pair, v1

User asks to analyse the two correct five-minute samples and pair them into a potentially loopable ten-minute file. User chooses natural transitions at roughly9–10minutes rather than padding/stretching to exactly10:00.

## Listen

- [Complete nine-minute listening copy](Below-the-Snowline-paired-loop-9min-v1.mp3)
- [Lossless24-bit48kHz stereo loop master](Below-the-Snowline-paired-loop-9min-v1.flac)
- [Shelter to Outpost —60s transition check](Shelter-to-Outpost-transition-60s.mp3)
- [Outpost back to Shelter —60s loop-boundary check](Outpost-to-Shelter-loop-boundary-60s.mp3)

Both short checks crossfade at0:20–0:40. The second crosses the actual end/start of the master at0:40. The main file starts inside the music to work as a circular loop; an opening fade belongs only on a future full-length assembly. Use the FLAC master for assembly or gapless repetition: a playback app may otherwise insert pauses between files. MP3 is a listening copy.

## Analysis

Measurements use the existing analyser snapshot at ../../deepwell-production-2026-11-01/review-against-learnings/analyzer_snapshot.py. Exact script hash, source hashes and methods are retained in source-analysis.json. No audio-listening tool is available: instrument, melody, harmonic-join and aesthetic claims are not established by measurements.

| Source | Full LUFS | Full LRA | Interior LRA30–270s | Stereo correlation, full |
|---|---:|---:|---:|---:|
| Shelter on the Ice Plain | -14.6 | 13.0LU | 10.2LU | 0.287 |
| Outpost on the Ice | -15.4 | 13.5LU | 11.8LU | 0.232 |

Both have substantial internal level variation beyond the opening/ending fades. They retain more measured dynamic contrast than the approved Deepwell hour(4.3LU), though the pieces and durations differ. The paired mix is−23.19LUFS,11.4LU LRA and−8.63dBTP. Its level changes may be part of the character the user likes; do not compress automatically before listening feedback.

Both are midrange weighted with very little sub80Hz power(Shelter0.044%,Outpost0.090%). Shelter has more power above1kHz(3.286% versus0.465%); energy is not perceived loudness or instrument identity. There is no measurement-led reason to apply the earlier Ringfall bass-cut experiment. Whole-file Outpost90s feature recurrence was not confirmed by strong sampled waveform matches(max0.096); Shelter had no full-file candidate. This does not prove absence of repeated musical phrases. These statistics cannot establish fidelity to the Hoth reference.

## Arrangement and checks

Each source retains4–294s. Fixed gains based on the30–270s interior aim at−23LUFS: Shelter−8.5dB,Outpost−8.0dB. Preserve dynamic changes; no compression, limiting, EQ, pitch shifting or time stretching. Both overlaps use20s sine/cosine equal-power fades. The ten source minutes become9:00 after20s total source-edge trims and40s total overlaps.

- 0:00–4:10: Shelter source0:24–4:34.
- 4:10–4:30: Shelter4:34–4:54 into Outpost0:04–0:24.
- 4:30–8:40: Outpost0:24–4:34.
- 8:40–9:00: Outpost4:34–4:54 into Shelter0:04–0:24; continuous with the master start.

The actual generated fades are retained within overlaps except for the first4s and final6s near-silent edges. Quiet transition breathing may remain; these are listening candidates, not harmonic approval. No artificial repeat material or environmental effects added.

delivery-validation.json records complete source/output audio decoding, unchanged original hashes, exact540s/25,920,000 stereo-frame master, finite/unclipped samples, full recipe comparisons and native/decoded seam steps compared with nearby ordinary sample differences. Decoded FLAC tail/head was compared with the intended wrapped preview. These check signal continuity and faithful encoding, not perceived musical flow. User review of both joins is pending.

build.py reproduces the files from the preserved originals and existing analysis cache; it refuses to overwrite media. mix-recipe.json stores timing/gains and source fingerprints. Earlier incorrect one-minute downloads remain preserved separately. The exact30s seed, model, generation prompt and cost remain unverified. No generation, publication, commit or push performed.
