# SAM Audio — access setup for a short separation experiment

Prepared 2026-10-21 following the failed AudioSep test. This folder currently
contains access helpers, not a working SAM Audio inference setup or any new
audio. The original Illuminated Horizon source and previous results are intact.

1. Sign in to Hugging Face and open
   https://huggingface.co/facebook/sam-audio-small . Review the terms/access
   form and submit it yourself. The form shares the account information stated
   on that page with the model author. Approval may be immediate or pending;
   do not assume it is granted until the page or checker confirms it.
2. Double-click sign-in.cmd. Choose **Log in with your browser** and complete
   Hugging Face's displayed URL/code flow. No token or password belongs in chat.
   The helper uses the installed official huggingface_hub library's login flow.
3. The helper checks small-model and large-model access by requesting only
   configuration-file metadata. A separate large-model request is optional for
   a later trial; lack of large-model access does not block a small-model test.
   check-access.cmd can repeat the check after an approval arrives.

Account credentials are saved by Hugging Face in
music/.local/sam-audio-separation/hf-cache/ (Git ignored). They are not added to
Git credentials or to access-status.json. No tokens are printed or accepted as
command-line arguments by this helper. Do not share the cache or token files.

The helper downloads no model and uploads no audio. The future experiment is
a short excerpt of the untouched original, with text-directed extraction and
both target/residual reviews. Start with the small model, short chunks and a
memory-saving text-only configuration on the current RTX 3090 24-GB GPU.
Hardware suitability and musical separation quality still require testing.

SAM Audio supports text and temporal prompts, but whether it can distinguish
the repeating synth from wanted synth harmony in this recording is unproven.
A successful login is not evidence of a successful music edit. No further
stretching or spectral-drone reconstruction is proposed.

Sources checked:
- https://github.com/facebookresearch/sam-audio
- https://huggingface.co/facebook/sam-audio-small
- https://huggingface.co/docs/huggingface_hub/en/guides/cli
- https://huggingface.co/docs/hub/models-gated

Helpers use the working bundled Python 3.12 runtime and read the existing
ComfyUI-site huggingface_hub package. Existing Python environments are unchanged.
Only offline imports and the no-credential state were verified at preparation;
the browser login and gated access cannot be verified until the user completes
their own authentication and model-access request.
