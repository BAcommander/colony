from pathlib import Path
import hashlib,json
R=Path('G:/AI/colony'); P=R/'final/07-icebound-weather-post'
tags=['space ambient music','ambient music','sci fi ambient music','space ambience','sci fi ambience','relaxing ambient music','ambient music for studying','ambient music for focus','background music for work','music for reading','atmospheric music','ambient synth music','1 hour ambient music','winter ambience','Ambient Colony']
text=', '.join(tags)+'\n'
assert len(text)<500 and len(tags)==len(set(tags))
p=P/'youtube-tags.txt'; old=p.read_bytes(); backup=P/'youtube-tags-v1.txt'
if backup.exists():assert backup.read_bytes()==old,'Preserve previous version'
else:backup.write_bytes(old)
p.write_text(text,encoding='utf-8')
m=json.loads((P/'manifest.json').read_text(encoding='utf-8'))
meta=m['youtube_metadata'];old_count=meta['tags_characters_including_separators']
meta.update(status='Publication drafts; tags revised for delivered one-hour soundtrack on 2026-10-04',tags_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),tags_characters_including_separators=len(text.strip()),tags_characters_including_file_newline=len(text),tags_count=len(tags),keyword_note='Revised around music genre and intended listening use; no measured search-volume or ranking claim. Removed obscure scene lore. User-generated soundtrack direction selected and one-hour runtime verified.',tags_revision={'date':'2026-10-04','previous_file':backup.name,'previous_sha256':hashlib.sha256(old).hexdigest(),'user_feedback':"the tags for this video are a bit shit, no-one is searhcing half of those on youtube for this video",'guidance':'https://support.google.com/youtube/answer/146402?hl=en-GB'})
(P/'manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
p=P/'README.md';s=p.read_text(encoding='utf-8').replace(f'[Studio tags](youtube-tags.txt): {old_count} characters, under 500.',f'[Studio tags](youtube-tags.txt): {len(text.strip())} characters, under 500; revised around music and listening use.');p.write_text(s,encoding='utf-8')
print(f'Saved {len(tags)} tags; {len(text.strip())} characters. Original preserved in {backup.name}.')
print(text)
