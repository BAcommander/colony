# Illuminated Horizon — short neural separation test

Local test, 2026-10-21. User authorized testing a short section of the untouched
original before building an arrangement tool. The two preceding DSP edits were
rejected: whole-mix stretching sounded poor; spectral resynthesis sounded like a
drone. Neither rejected edit is input to this experiment.

## Result

**AudioSep did not selectively isolate the repeating synth in this sample.**
Across three descriptions, its estimated target is almost the entire recording.
This does not establish a usable route for the requested ambient breakdown.
The clips are diagnostic listening material, not a finished or approved edit.

| Description | Target/source waveform correlation | Remainder RMS below original |
| --- | ---: | ---: |
| a repeating synthesizer arpeggio | 0.99688 | 22.03 dB |
| a pulsing electronic synthesizer | 0.99775 | 23.40 dB |
| a synthesizer playing a repetitive melody | 0.999997 | 51.85 dB |

The model responds to query changes: a ten-second control run extracts very
little signal for dog barking or speech, but extracts almost the entire mix for
both the repeating-arpeggio and sustained-synth-chords descriptions. This
supports interpreting the result as insufficiently fine source discrimination
on this recording, rather than a missing conditioning branch. It is not proof
of general model performance.

## Listen

All files are the same 45 seconds, original time **3:20–4:05**, at 32 kHz stereo.
One shared -2.5891 dB gain applies to every clip. Remainders are deliberately not
independently normalized: doing so would hide the amount of signal removed.
All excerpts have identical 20-ms edge fades. WAV and MP3 copies are included.

Start with these four files:

1. **01-original-3m20-to-4m05.mp3** — original reference, resampled only.
2. **02-arpeggio-extracted.mp3** — what the model thinks is the repeating synth.
3. **02-arpeggio-removed.mp3** — original minus that complete estimate.
4. **02-arpeggio-reduced.mp3** — original minus 75% of the estimate; retains the
   estimated target at 25% amplitude. This is a gentler diagnostic, not success.

03-pulse-* and 04-sequence-* contain the equivalent tests for the other two
descriptions. A nearly silent remainder does not show successful pulse removal
while preserving the wanted music. Compare the extracted target with the
original to hear collateral removal.

## Method and reproducibility

SAM Audio was considered but requires approved Hugging Face access, which is
not configured. No access restriction was bypassed. This test uses the public
[AudioSep implementation](https://github.com/Audio-AGI/AudioSep), commit
944583f18b84589dc965de3ad77525c945334252, and its author's public checkpoint.
Model download metadata and SHA-256 verification are saved. Your audio was
never uploaded. No paid service or music-generation credits were used.

The ResUNet30 inference code is unchanged. The harness loads the checkpoint's
trained CLAP RoBERTa text branch and projection directly, following the upstream
pooler-output, ReLU projection and L2-normalization calculation. All 332 separator
weight/buffer tensors, 199 text-branch tensors and four projection tensors load
strictly. Only an obsolete position-ID buffer is omitted. The unused audio-query
branch and Lightning training wrappers are not instantiated. weights_only=True
is used for checkpoint loading. There is no retraining or substituted model.

The published model is trained for mono at 32 kHz. Here left/right are processed
as a two-item mono batch with the same query and boundaries. That adaptation
retains two-channel outputs but is not a stereo-trained separation guarantee.
Ten-second windows with five-second hops are joined using Hann overlap-add.
Input context is original 3:10–4:15, then cropped to the central 45-second review.

Runtime: bundled Python 3.12.14; existing ComfyUI-site PyTorch 2.11.0+cu128;
RTX 3090; roughly 3.25 GiB peak PyTorch allocated GPU memory. Small additional
audio libraries, source checkout and checkpoint are isolated under
music/.local/audiosep-separation/. Existing Python environments are not modified.
The old ComfyUI launcher was not used or repaired; its libraries were reused
read-only by the working bundled Python runtime.

Run run_separation.py with that runtime to reproduce in an empty output folder.
--inspect lists checkpoint structure; --control runs the short query controls.
download_assets.py downloads the public checkpoint and tokenizer, never audio.
The scripts contain this machine's paths. Outputs are protected from overwrite.

## Verification and scope

- All ten 45-second MP3s fully decode to exactly 1,440,000 stereo frames, with
  finite values and no full-scale samples.
- Extracted estimate plus remainder reconstructs the original within floating
  point precision. This checks subtraction math, not artistic separation.
- All comparisons share timing, sample rate, gain and excerpt-edge fades.
- Exact source/model/output hashes, prompts and checks are in
  delivery-test-v1.json; query controls and comparison measurements are separate.
- Assistant performed signal and implementation checks, not continuous listening.
  User listening verdict remains pending. No good separation is claimed.

No stretching, spectral texture reconstruction, additional music, full-track
remix, interface, Colony assembly, commit, push or remote media backup was made.
