"""Reconstructed reflection surface: dense wind-wave normals, no sparse glint overlays."""
import cv2
import numpy as np

class ReflectionSurface:
 def __init__(self,plate,mask,settings):
  self.plate=plate.astype(np.float32);self.mask=mask.astype(np.float32);self.c=settings
  h,w=mask.shape;self.y,self.x=np.mgrid[:h,:w].astype(np.float32)
  # Remove fixed ice/shore from the sampled reflection texture before displacement.
  invalid=np.uint8(mask<.05)*255
  clean=cv2.inpaint(plate,invalid,7,cv2.INPAINT_TELEA)
  self.reflection=cv2.GaussianBlur(clean.astype(np.float32),(0,0),settings.get('reflection_sigma_x',9),sigmaY=settings.get('reflection_sigma_y',4))
  # A perspective plane, not a flat screen-space stripe field.
  distance=2600/(self.y+65)
  self.world_x=(self.x-w*.5)*distance/330
  self.world_z=distance
  rng=np.random.default_rng(settings['seed']);self.waves=[]
  for i in range(settings['components']):
   theta=rng.normal(1.10,.55);length=rng.uniform(*settings.get('wavelength_range',[5,35]));k=2*np.pi/length
   direction=np.array([np.cos(theta),np.sin(theta)])
   phase=k*(direction[0]*self.world_x+direction[1]*self.world_z)+rng.uniform(0,2*np.pi)
   # Dispersion yields different velocities rather than synchronized pulsation.
   omega=np.sqrt(9.81*k)*settings['time_scale']
   amplitude=(length/settings.get('wavelength_range',[5,35])[1])**.4
   self.waves.append((phase,omega,amplitude,direction))
  self.norm=sum(v[2]**2 for v in self.waves)**.5
 def frame(self,t):
  nx=np.zeros_like(self.x);nz=np.zeros_like(self.x)
  for phase,omega,amp,d in self.waves:
   slope=np.cos(phase-omega*t)*amp
   nx+=slope*d[0];nz+=slope*d[1]
  nx/=self.norm;nz/=self.norm
  depth=np.clip(self.y/self.y.max(),0,1)
  mx=self.x+nx*(9+9*depth);my=self.y+nz*(6+9*depth)
  reflected=cv2.remap(self.reflection,mx.astype(np.float32),my.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
  # Broad sky reflection response plus localized crest glints from changing normals.
  orientation=np.tanh(nz*.85+nx*.25)
  glint=np.exp(-((nx-.18)**2+(nz+.48)**2)/.19)
  surface=reflected*(1+orientation[...,None]*.16)
  surface+=(glint-.16)[...,None]*self.c['specular_strength']*np.array([.82,.93,1.0],np.float32)
  alpha=self.mask[...,None]
  return np.clip(self.plate*(1-alpha)+surface*alpha,0,255)
