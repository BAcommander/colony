from pathlib import Path
import subprocess,numpy as np,json,re
R=Path(__file__).resolve().parent
FF=r'C:\Program Files\ShareX\ffmpeg.exe'
video=R/'Cyberpunk-Apartment-V3-4K.mp4'
# Full decode verifies that every delivered frame is readable; the compact decoded
# representation checks timing and continuity without allocating gigabytes of RAM.
decoded=subprocess.run([FF,'-hide_banner','-i',str(video),'-vf','scale=320:180','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
frames=np.frombuffer(decoded.stdout,np.uint8).reshape(-1,180,320,3)
assert len(frames)==600,f'Expected 600 frames, got {len(frames)}'
assert re.search(r'3840x2160',decoded.stderr.decode()),'Wrong output resolution'
assert re.search(r'60 fps',decoded.stderr.decode()),'Wrong frame rate'
a=frames.astype(np.int16)
diff=np.abs(a[1:]-a[:-1]).mean((1,2,3))
boundary=float(np.abs(a[-1]-a[0]).mean())
half_difference=float(np.abs(a[:300]-a[300:]).mean())
assert half_difference>.01,'Unexpected duplicated five-second halves'
report={'frames':len(frames),'seconds':len(frames)/60,'fps':60,'resolution':[3840,2160],'decoded_without_errors':True,'average_adjacent_difference':float(diff.mean()),'largest_adjacent_difference':float(diff.max()),'loop_boundary_difference':boundary,'halves_are_distinct':True,'half_difference':half_difference,'file_size_bytes':video.stat().st_size}
(R/'delivery-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
subprocess.run([FF,'-y','-v','error','-ss','3.2','-i',str(video),'-frames:v','1',str(R/'delivered-frame.png')],check=True)
