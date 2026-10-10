from pathlib import Path
p=Path('G:/AI/colony/final/07-icebound-weather-post/music/long-source-v1')
for name in ['analysis.json','analyze.py']:
    target=p/(Path(name).stem+'-initial'+Path(name).suffix)
    assert not target.exists()
    target.write_bytes((p/name).read_bytes())
s=(p/'analyze.py').read_text()
s=s.replace('range(10,46)', 'range(5,91)').replace('range(n-50,n-5)', 'range(n-75,n-1)')
(p/'analyze.py').write_text(s)
