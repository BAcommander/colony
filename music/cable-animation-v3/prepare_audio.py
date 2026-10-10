from pathlib import Path
R=Path('G:/AI/colony');H=Path(__file__).resolve().parent
s=(R/'final/05-saltline-receiver/music/long-source-v1/make-two-hours-v1.py').read_text()
s=s.replace('Red World Basin','Mineral Valley Transit').replace('Saltline Receiver','Last Cable Station')
s=s.replace('ROOT=Path(__file__).resolve().parents[4]',"ROOT=Path('G:/AI/colony')")
s=s.replace('REPORT=Path(__file__).resolve().parent',"REPORT=ROOT/'final/06-last-cable-station/music/long-source-v1'")
s=s.replace('exports/05-saltline-receiver/Saltline-Receiver-Red-World-Basin-2-Hours-v1.mp3','exports/06-last-cable-station/Last-Cable-Station-Mineral-Valley-Transit-2-Hours-v1.mp3')
s=s.replace('88143466d2f9f4f72200a04619cd7ce0bcc51939b271d9160ecfbd57f94fb28b','7154f7e3bf623d29e2b7419aba4efa8079b0237ae5ee0551150b2482d68300d8')
s=s.replace('twelve-second','sixteen-second')
s=s.replace('transition is fine, make the 2 hour long  version','Audio previously accepted as good enough; user requested combined final and confirmed 2 hours on 2026-10-03')
out=H/'make-two-hours-v1.py';assert not out.exists();out.write_text(s,encoding='utf-8')
print('Prepared two-hour soundtrack runner')
