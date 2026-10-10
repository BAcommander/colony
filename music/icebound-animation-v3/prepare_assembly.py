from pathlib import Path
import re
R=Path('G:/AI/colony'); H=Path(__file__).resolve().parent
s=(R/'music/cable-animation-v3/assemble-with-colony.py').read_text(encoding='utf-8')
for a,b in {
 'Last Cable Station':'Icebound Weather Post',
 '06-last-cable-station':'07-icebound-weather-post',
 'Last-Cable-Station-Mineral-Valley-Transit-2-Hours-v1.mp3':'Icebound-Weather-Post-Winter-Colony-Night-1-Hour-v1.mp3',
 'Last-Cable-Station-2-Hours-4K-v1.mp4':'Icebound-Weather-Post-1-Hour-4K-v1.mp4',
 'video-4k-v3.mp4':'video-4k-v3-60s.mp4',
 'two-hour-delivery-v1.json':'one-hour-delivery-v1.json',
 'str(loop),20.0':'str(loop),60.0',
 "'-t','20'":"'-t','60'",
 '7200':'3600',
 '216000':'108000',
 'all_360':'all_60',
 'two-hour':'one-hour',
 '2026-10-03':'2026-10-04',
 '.read_text()':'.read_text(encoding="utf-8")',
}.items():s=s.replace(a,b)
s=re.sub(r'\b600\b','1800',s)
out=H/'assemble-with-colony.py'; assert not out.exists()
compile(s,str(out),'exec');out.write_text(s,encoding='utf-8')
print('Prepared Icebound runner for the actual Colony app engine')
