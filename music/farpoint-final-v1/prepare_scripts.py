from pathlib import Path
H=Path(__file__).parent
T=H.parent/'shoreless-final-v1'
assert not (H/'render_delivery.py').exists() and not (H/'assemble-with-colony.py').exists(),'Initial scaffolding only; preserve corrected delivery scripts'
s=(T/'render_delivery.py').read_text()
for a,b in [('ShorelessV3','FarpointV6'),('render_shoreless_v3','render_farpoint_v6'),('shoreless-animation-v3','farpoint-animation-v6'),('09-offshore-night-office','10-nightward-station'),('delivery-v3','delivery-v6'),('video-4k-v3','video-4k-v6'),('native v3','native v6')]:s=s.replace(a,b)
s=s.replace("assert s.loop_duration==60\n        cache=H/'.environment-cache'\n        assert json.loads((cache/'fingerprint.json').read_text())==s.fingerprint()\n        s.cache=cache", "assert s.duration==60\n        s.h,s.w=s.base.shape[:2]")
s=s.replace('transition is fine , water is fine, make the 2 hour loop, scale up the video quality etc etc?', 'i think for now lets just build out the full farpoint with this. since the track was only 5 minutes do you recommend 1 hour?')
s=s.replace('sixty-second v3','sixty-second v6').replace('two-hour Colony assembly','one-hour Colony assembly').replace('all 120','all 60')
(H/'render_delivery.py').write_text(s,encoding='utf-8')
s=(T/'assemble-with-colony.py').read_text()
for a,b in [('The Shoreless Colony','Farpoint Station'),('09-offshore-night-office','10-nightward-station'),('video-4k-v3','video-4k-v6'),('delivery-v3','delivery-v6'),('Shoreless-Colony-Alien-Sea-Viewport-with-Water-2-Hours-v1','Farpoint-Station-Unfolding-Warmth-1-Hour-v1'),('Shoreless-Colony-2-Hours-4K-v1','Farpoint-Station-1-Hour-4K-v1'),('two-hour','one-hour'),('7200','3600'),('216000','108000'),('v3 master','v6 master'),('all_120','all_60'),("'water':'Approved premixed water v2; no additional SFX layer'","'sfx':'None; approved Unfolding Warmth soundtrack only'")]:s=s.replace(a,b)
(H/'assemble-with-colony.py').write_text(s,encoding='utf-8')
