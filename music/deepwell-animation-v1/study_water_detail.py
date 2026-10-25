"""Internal source-specific water scale study, before full preview rendering."""
from render_deepwell import *
s=Deepwell();c=dict(s.config['water']);c.update(wavelength_range=[.12,1.05],time_scale=.07,reflection_sigma_x=1.4,reflection_sigma_y=.65,displacement_scale=.38,reflection_contrast=.09,specular_strength=9,sampling_filter_pixels=1.05)
a,b,z,d=c['roi'];s.water=ChannelSurface(s.base[b:d,a:z],s.masks['water'][b:d,a:z],c,(a,b));s.config['water']=c
write_json('water-detail-proposed-config.json',c)
for t in [0,4,8,16]:Image.fromarray(s.frame(t)).save(H/f'water-detail-study-{t:02d}.png')
print('Fine brine detail study ready',flush=True)
