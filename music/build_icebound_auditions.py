from pathlib import Path
root=Path('G:/AI/colony')
old=root/'final/06-last-cable-station/music/long-source-v1/make-auditions-v1.py'
target=root/'final/07-icebound-weather-post/music/long-source-v1/make-auditions-v1.py'
assert not target.exists()
s=old.read_text()
s=s.replace('Cable Station','Icebound Weather Post').replace('06-last-cable-station','07-icebound-weather-post')
s=s.replace('Mineral_Valley_Transit_2026-10-03T144345.mp4','Winter_Colony_Night_2026-10-04T155903.mp4')
s=s.replace('START,END,OVERLAP=38,463,16','START,END,OVERLAP=83,414,8').replace('GAIN_DB=-7.0','GAIN_DB=-8.0')
s=s.replace('7154f7e3bf623d29e2b7419aba4efa8079b0237ae5ee0551150b2482d68300d8','57232ba3451862836625c88aaabf22a2d7d3d056c50417bb86fcc85d85fbb626')
s=s.replace('Last-Cable-Station-Mineral-Valley-Transit','Icebound-Weather-Post-Winter-Colony-Night')
s=s.replace('bytecount+=len(chunk)','assert np.isfinite(np.frombuffer(chunk,np.float32)).all()\n  bytecount+=len(chunk)')
s=s.replace('Best tested level/coarse-spectrum candidate: source 0:38 to 7:43, 425 seconds retained, 16-second overlap. Mean overlap level difference 0.018 dB, coarse spectral distance 0.310 dB. Fixed -7 dB gain targets approximately -20 LUFS for comfortable comparison with the preceding release. No compression, harmonic compatibility or assistant listening claim.', 'Best tested level/coarse-spectrum candidate: source 1:23 to 6:54, 331 seconds retained, eight-second overlap. Mean overlap level difference 0.011 dB, coarse spectral distance 2.148 dB. Fixed -8 dB gain gives listening headroom. No compression, harmonic compatibility, absence-of-vocals or assistant listening claim.')
s=s.replace('[25,41]', '[25,33]').replace('[[409,425],[818,834]]','[[323,331],[646,654]]')
s=s.replace("summary=loud.stderr.decode(errors='replace').rsplit('Summary:',1)[-1].strip()", "summary=loud.stderr.decode(errors='replace').rsplit('Summary:',1)[-1].strip()\n import re\n true_peak=float(re.search(r'Peak:\\s*([-\\d.]+) dBFS',summary).group(1))\n assert true_peak<0, true_peak")
target.write_text(s,encoding='utf-8')
print(target)
