# Glacier replacement: Amber Refuge Beneath the Stone

Current status, reconciled 2026-09-29: user approved the join with "loop sounds fine"; four-hour MP3 and MP4 delivered and technically validated. See delivery-v2.md. Complete replacement YouTube checks and full-length listening approval remain pending. The preparation and audition notes below document the earlier stages, not outstanding rebuild work.

User supplied 2026-09-27 after returning to the alternative original Amber Sanctuary test direction. Actual source is preserved in exports/03-glacier-sanctuary/source/Amber_Refuge_Beneath_the_Stone_2026-09-27T204853.mp4. Existing claimed soundtrack/video untouched.

FFmpeg fully decoded the audio without reported errors. Approximately 9:00.01 of audio inside a 9:04.40 video container, stereo 48 kHz AAC. Integrated loudness -13.3 LUFS, loudness range 2.2 LU, true peak -1.4 dBFS. Not a ten-minute audio export despite the requested generation setting. No assistant listening claimed.

Initial screening step (subsequently completed for the source): user uploads the supplied MP4 privately to YouTube and waits for Checks. The reported result was No notices. This source check is screening, not a guarantee against future claims or a check of the full replacement export.

## Loop audition v1

User supplied YouTube screenshot showing the private Amber Refuge upload with No notices. This is a current screening result, not a future clearance guarantee. The user subsequently approved the join and the four-hour rebuild was delivered; see delivery-v2.md.

Candidate source section: 0:29-8:31 (482 seconds), 15-second equal-power crossfade, repetition interval 467 seconds (7:47). Selected by average level and spectral balance, not assistant listening. Preview exports/03-glacier-sanctuary/Glacier-Amber-Refuge-join-v1.mp3 is 65 seconds. Transition occupies 0:25-0:40; source windows 7:51-8:31 and 0:29-1:09. Gain -4.7 dB, aiming near the previous -18 LUFS long soundtrack; final assembled loudness must be measured independently. Full preview decode and true peak measured in preview-loudness.txt. Originals preserved.

Reproduction filter: [0:a]asplit=2[a][b];[a]atrim=start=471:end=511,asetpts=PTS-STARTPTS[x];[b]atrim=start=29:end=69,asetpts=PTS-STARTPTS[y];[x][y]acrossfade=d=15:c1=qsin:c2=qsin,volume=-4.7dB[out]
