from pathlib import Path
root = Path('G:/AI/colony')
out = root/'final/07-icebound-weather-post/music/long-source-v1'
out.mkdir(parents=True, exist_ok=True)
src = root/'final/06-last-cable-station/music/long-source-v1/analyze.py'
target = out/'analyze.py'
assert not target.exists()
s = src.read_text().replace('Mineral_Valley_Transit_2026-10-03T144345.mp4','Winter_Colony_Night_2026-10-04T155903.mp4').replace('06-last-cable-station','07-icebound-weather-post')
target.write_text(s,encoding='utf-8')
print(target)
