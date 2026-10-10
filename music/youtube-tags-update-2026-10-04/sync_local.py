from pathlib import Path
import json,hashlib
R=Path('G:/AI/colony');H=Path(__file__).resolve().parent
evidence=json.loads((H/'studio-update.json').read_text(encoding='utf-8'))
folders={'nWrYvsZlNj4':'04-floodplain-keeper','SoZ7xOtRCL8':'05-saltline-receiver','OwzP2clTWR8':'06-last-cable-station'}
for item in evidence['after']:
    assert item['save_disabled'] and item['title_description_unchanged']
    p=R/'final'/folders[item['id']]; target=p/'youtube-tags.txt'; old=target.read_bytes()
    backup=p/'youtube-tags-before-studio-update-2026-10-04.txt'
    assert not backup.exists();backup.write_bytes(old)
    text=', '.join(item['tags'])+'\n';assert len(text)<500
    target.write_text(text,encoding='utf-8')
    mp=p/'manifest.json';m=json.loads(mp.read_text(encoding='utf-8'));meta=m['youtube_metadata'];old_count=meta['tags_characters_including_separators']
    meta.update(tags_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),tags_characters_including_separators=len(text.strip()),tags_characters_including_file_newline=len(text),tags_count=len(item['tags']),keyword_note='Updated to music genre, intended listening use and verified duration; no measured search volume or ranking claim.',tags_revision={'date':'2026-10-04','previous_file':backup.name,'previous_sha256':hashlib.sha256(old).hexdigest(),'studio_video_id':item['id'],'studio_saved':True,'studio_character_count':len(text.strip())+len(item['tags'])+1,'evidence':'../../music/youtube-tags-update-2026-10-04/studio-update.json'})
    mp.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
    readme=p/'README.md';s=readme.read_text(encoding='utf-8').replace(f'{old_count} characters, under 500',f'{len(text.strip())} characters, under 500');readme.write_text(s,encoding='utf-8')
    print(f"{folders[item['id']]}: {len(item['tags'])} tags, {len(text.strip())} text characters; Studio saved and local copy synchronized")
