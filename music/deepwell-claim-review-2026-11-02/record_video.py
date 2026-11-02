"""Point the release and reupload package to the validated revised file."""
from pathlib import Path
import json,shutil,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];D=H/'video-v2';F=R/'final/12-deepwell-station';U=F/'upload-2026-11-02'
def read(p):return p.read_bytes().decode('utf-8-sig')
def write(p,s):p.write_bytes(s.encode('utf-8'))
def save(p,x):write(p,json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
delivery=json.loads(read(D/'delivery-validation.json'));assert delivery['status']=='passed'
U.mkdir(exist_ok=True)
for name in ['youtube-title.txt','description.txt','youtube-tags.txt']:shutil.copy2(F/name,U/name)
thumb=R/'music/deepwell-thumbnail-v2/Deepwell-title-v2.jpg';shutil.copy2(thumb,U/'thumbnail-recommended.jpg')
write(U/'upload-notes.txt',f'''Deepwell Station — revised upload,2026-11-02

UPLOAD THIS NEW FILE:
{delivery['output']}

Exact1:00:00,3840x2160,30fps. All video pictures/opening unchanged. Approved revised audio replaces Waterworks Gallery30–51s in all10 occurrences with6s crossfade handles. Original video preserved; use the v2-audio-revised filename.

Use the accompanying title,description and tags unchanged. thumbnail-recommended.jpg is the existing new one-word DEEPWELL candidate, not a newly generated image.

Upload unlisted initially and wait for copyright checks and4K processing. No claim-free result is guaranteed; new upload has not been checked. Listen to the revised passage around19:54–20:15 and verify the opening. Audio silence to5s and fade to20s are intentional. Only then publish/schedule as appropriate. The old upload has not been changed or deleted.
''')
save(U/'package.json',{'date':'2026-11-02','status':'Ready for user reupload; fresh YouTube checks pending','video':delivery,'files':{p.name:sha(p) for p in U.iterdir() if p.is_file() and p.name!='package.json'},'title_description_tags_unchanged':True,'thumbnail':'Existing recommended one-word candidate; no new selection inferred','uploaded':False,'old_youtube_upload_modified':False})
old=read(F/'README.md');archive=D/'previous-release-README.md'
if not archive.exists():write(archive,old)
old=old.replace('Current delivery (2026-11-01):','Previous delivery (2026-11-01; superseded for reupload):',1)
heading_end=old.index('\n')
note='''
Current delivery(2026-11-02): [revised one-hour4K video](../../exports/12-deepwell-station/Deepwell-Station-1-Hour-4K-v2-audio-revised.mp4) with user-approved replacement audio after the reported Good Energy/Flowstate Content ID claim. All108,000 picture packets and timestamps match the original; only audio is re-encoded with the same opening gain. Waterworks30–51s replaced in all10 occurrences, with6s crossfade handles. [Validation and recipe](../../music/deepwell-claim-review-2026-11-02/video-v2/README.md) · [Reupload package](upload-2026-11-02/). Original retained. No upload or fresh YouTube clearance yet.

'''
write(F/'README.md',old[:heading_end+1]+note+old[heading_end+1:])
approval=json.loads(read(D/'user-approval.json'))
recipe=json.loads(read(H/'replacement-v1/replacement-recipe.json'));recipe['status']='User-approved replacement audio; revised video delivered; fresh YouTube checks pending';recipe['approval']=approval;recipe['new_video_muxed']=True;recipe['video_delivery']=delivery['output'];save(H/'replacement-v1/replacement-recipe.json',recipe)
val=json.loads(read(H/'replacement-v1/validation.json'));val['user_review_pending']=False;val['user_approval_record']='../video-v2/user-approval.json';save(H/'replacement-v1/validation.json',val)
write(D/'README.md',f'''# Deepwell revised full video —2026-11-02

User accepts the replacement excerpt and requests the complete video for reupload. Exact approval in user-approval.json.

[New upload file](../../../exports/12-deepwell-station/Deepwell-Station-1-Hour-4K-v2-audio-revised.mp4) · [Reupload package](../../../final/12-deepwell-station/upload-2026-11-02/).

Output:3600s,3840x2160,30fps,108000frames; H.264 BT.709 TV, AAC192kb/s stereo48kHz. Bytes:{delivery['bytes']}. SHA256:{delivery['sha256']}.

Video stream copied from the hash-verified original. Every packet payload, DTS/PTS, duration, size, codec extradata and timebase matches the earlier validated packet record. Original full video decode evidence therefore applies; a redundant hour-long4K decode was not performed. No new artistic inspection or animation change.

Replacement audio is the approved hour candidate from replacement-v1/. The original Colony graph is reapplied once: no sound until5s, hsin fade5–20s. Existing closing fade retained. All172800000 stereo audio frames decoded and compared against the complete approved mix through that graph; finite/unclipped, correlation/SNR/gain checks pass. Source fingerprints, exact command, probes and diagnostic results retained in assembly-settings.json,video-validation.json,audio-validation.json and delivery-validation.json.

Original video/audio and former release README retained. Title/description/tags unchanged; current recommended one-word thumbnail copied to a dated reupload pack. No upload, account change, old-upload removal, claim dispute, new generation, commit or push. YouTube copyright clearance remains unverified and requires a new upload check. No assistant listening or full combined user playback claimed.

Reproduction: export_video.py then record_video.py. FFmpeg and Python/NumPy required; use fresh output paths because the exporter refuses overwrite. Large exports and cache remain local under existing media policy.
''')
write(H/'CURRENT-DELIVERY.txt',f"Approved revised video ready for user reupload:\n{delivery['output']}\nSee video-v2/README.md and final/12-deepwell-station/upload-2026-11-02/. Fresh YouTube checks pending.\n")
print('Release pointer and dated reupload package updated.')
