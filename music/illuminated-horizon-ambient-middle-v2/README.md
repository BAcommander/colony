# Illuminated Horizon — ambient middle v2

Rejected by the user: the middle sounds like a drone and is not good. Preserved as history; signal checks did not establish musical quality.

Historical listening candidate made locally on 2026-10-21. The user rejected v1 because
whole-mix time stretching was audible and sounded poor. Requested revision:
make the middle more ambient, reduce its repeating pulse and restore the pulse
gradually. Original source and v1 remain preserved.

This version uses the **original 8:30 timeline**. No time stretching, tempo
remapping, pitch-shifting filter, paid generation, download or model is used.

## Review

Start with **Ambient-Middle-Review-45s.mp3**. This is the revised centre at
original source time 3:20–4:05. Original-Middle-Level-Matched-45s.mp3 is the same
source passage with matched broad RMS for comparison.

Complete track: Illuminated-Horizon-Ambient-Middle-v2.mp3. A matching 24-bit,
48 kHz stereo WAV is included.

| Complete track | Treatment |
| --- | --- |
| 0:00–1:30 | Original recording |
| 1:30–3:00 | Gradual morph into the sustained bed; dry pulse recedes |
| 3:00–5:00 | Ambient bed dominant; original direct mix is 5% |
| 5:00–6:30 | Original mix and pulse gradually restored |
| 6:30–8:30 | Original recording and existing ending |

Other excerpts: Ambient-Entry-Review-v2.mp3 (full track 1:40–3:50) and
Pulse-Return-Review-v2.mp3 (4:45–6:45). Review excerpts have brief edge fades;
no new full-track opening or closing fades are added.

## What this edit does

The supplied file is a stereo master, without isolated instrument stems. A
first internal attempt using sustained-spectrum masking and diffuse tails still
left too much rhythmic envelope activity (only -2.35 dB in the test band) and
was not delivered.

The delivered approach reconstructs a new sustained texture from the source's
contemporaneous spectrum. Continuous oscillator phases and several seconds of
amplitude smoothing remove the original note attacks. Spectral leakage bins are
collapsed onto persistent peaks with fractional-bin frequency estimates, avoiding
the artificial beating of the first full-grid internal test. A short-envelope
leveler affects only the reconstructed pad to suppress residual beating while
retaining broad phrase dynamics. Restrained convolution
adds diffuse space to that bed. The source timeline is unchanged. The bed and
original are blended across two 90-second cosine ramps; a slow broad-energy
correction reduces the level dip in the blend. A single fixed headroom gain is
applied across the final track.

This changes the middle's timbre and fine phase/pitch detail. It is a spectral
texture reconstruction, not a cleanly isolated pad stem or an independently
composed musical passage. The oscillator grid spacing is about 0.732 Hz. The
existing pulse is attenuated through the blend and reconstruction; it is not
cleanly muted as a separate instrument. The pulse-power check is an engineering
gate; the change in sound must be judged from the listening excerpt.

## Evidence and limits

delivery-v2.json records exact settings, hashes, decoded duration and signal
checks. The source is SHA-256
a60986de41c0cd5418ad9dd56bdbf442ac01b8a284dd6f9b8a6c2930e39443db.
Before fixed output gain/encoding, source samples outside 1:30–6:30 are
unchanged. The 510-second audio stream is used; the source container has 4.4
additional seconds of video.

The pulse-envelope comparison measures normalized RMS-envelope power in
0.7–8 Hz during 3:00–5:00. It does not identify a particular instrument,
establish musical quality or substitute for listening. The assistant performed
signal checks, not continuous auditioning. User listening review remains
pending; this is not an approved soundtrack or a long-form assembly.

Reproduce with build_ambient.py, local Python/NumPy and FFmpeg, in a new empty
version folder. The sibling v1 source-original.mp4 is the preserved source.
Output files are protected from overwrite. Intermediate PCM files are
regenerable. No commit, push or remote media backup was performed.
