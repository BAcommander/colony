from pathlib import Path
R=Path('G:/AI/colony');H=Path(__file__).resolve().parent
s=(R/'final/05-saltline-receiver/assembly-v1/assemble-with-colony.py').read_text()
s=s.replace('Saltline','Last Cable Station').replace('05-saltline-receiver','06-last-cable-station')
s=s.replace('Last Cable Station-Receiver-Red-World-Basin-2-Hours-v1.mp3','Last-Cable-Station-Mineral-Valley-Transit-2-Hours-v1.mp3')
s=s.replace('Last Cable Station-Receiver-2-Hours-4K-v1.mp4','Last-Cable-Station-2-Hours-4K-v1.mp4')
s=s.replace('video-4k-v7-60s.mp4','video-4k-v3.mp4')
s=s.replace("R/'music/saltline-animation-v1/v7-delivery-validation.json'","R/'final/06-last-cable-station/delivery-v3/delivery-validation.json'")
s=s.replace("assert sha(audio)=='4dd1f3eca00e073a75fc23bf04125d2a229a4164046d0a2bf04c9c0984d16ec7'","audio_delivery=json.loads((R/'final/06-last-cable-station/music/long-source-v1/two-hour-delivery-v1.json').read_text())\nassert sha(audio)==audio_delivery['sha256']")
s=s.replace('60.0,render.probe_video','20.0,render.probe_video').replace("'-t','60'","'-t','20'")
s=s.replace('1800','600').replace('v7','v3').replace('all_120','all_360')
s=s.replace('first-loop pictures','first-loop pictures').replace('first assembled minute','first assembled twenty seconds')
out=H/'assemble-with-colony.py';assert not out.exists();out.write_text(s,encoding='utf-8')
print('Prepared actual Colony engine assembly runner')
