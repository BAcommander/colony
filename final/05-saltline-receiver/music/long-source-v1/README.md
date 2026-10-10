# Saltline Receiver - Red World Basin loop audition

2026-10-03: user supplied Red_World_Basin_2026-10-03T133309.mp4 after requesting a seven-minute source for a two-hour delivery. Original download is preserved; its byte-identical copy is in exports/05-saltline-receiver/source/. Full decoded audio duration is 420.010667 seconds. Settings and exact generation prompt were not observed; no assistant listening claim.

Candidate uses source 0:15-6:47 (392 seconds) with a twelve-second sine/cosine equal-power crossfade. Repeat interval is 380 seconds. Among tested windows/overlaps, this scored best on combined level and coarse spectral similarity: 0.035 dB overlap mean-level difference and 0.426 dB spectral distance. This does not establish harmonic compatibility or an inaudible join.

The source measured -26.2 LUFS and -12.0 dBFS true peak. Auditions use a fixed +6 dB gain, without compression. Encoded short audition: -19.8 LUFS, -6.3 dBFS true peak. Three repeats: -20.4 LUFS, -6.3 dBFS true peak. Both files fully decoded to their exact sample counts. The short audition has brief edge fades; the longer preview has one five-second opening and ten-second closing fade. These outer preview fades are separate from the loop crossfades.

- Short join: exports/05-saltline-receiver/Saltline-Receiver-Red-World-Basin-join-v1.mp3, 62 seconds. Transition occupies 0:25-0:37.
- Three repeats: exports/05-saltline-receiver/Saltline-Receiver-Red-World-Basin-three-repeats-v1.mp3, 19:12. Transitions at 6:20-6:32 and 12:40-12:52.

Current outcome: user approved the transition with "transition is fine" and requested the two-hour version. The two-hour soundtrack is now delivered; see two-hour-delivery-v1.md. Combined-video assembly and extended listening remain pending. Source upload checks are not observed; follow the existing music workflow before long assembly.

Reproduction: run analyze.py followed by make-auditions-v1.py using the existing Python/NumPy runtime and installed ShareX FFmpeg. The audition renderer asserts the source hash and refuses to overwrite existing media. Exact analysis and delivery hashes are in analysis.json and audition-v1.json. Scripts/reports are saved locally; no commit/push is claimed. Source audio and auditions remain ignored exports and are not backed up by Git.
