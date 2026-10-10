from pathlib import Path
import re
for p in [Path('G:/AI/colony/PRODUCTION_PIPELINE.md'),Path('G:/AI/colony/final/07-icebound-weather-post/music/README.md')]:
    s=p.read_text(encoding='utf-8')
    def fix(m):
        try:return m.group().encode('cp1252').decode('utf-8')
        except UnicodeError:return m.group()
    s=re.sub(r'[^\x00-\x7f]+',fix,s)
    p.write_text(s,encoding='utf-8')
