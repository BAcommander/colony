"""Periodic local gust renewal, preserving the accepted source-scale transport speed."""
import copy
import numpy as np
from dust_transport import DustTransport

def smooth(value):
    value=np.clip(value,0,1)
    return value*value*(3-2*value)

class PeriodicDust:
    def __init__(self,x,y,config,duration):
        self.c=config;self.duration=duration;self.shape=x.shape;self.entries=[]
        for schedule in config['loop_schedule']:
            gust=copy.deepcopy(config['gusts'][schedule['gust_index']])
            gust['x']=schedule['birth_x']
            c=copy.deepcopy(config);c['gusts']=[gust];c.pop('incoming_gusts',None)
            # Recover each un-clipped optical depth before applying the shared cap.
            c['max_opacity']=.999999
            transport=DustTransport(x,y,c,duration)
            transport.local_x+=schedule['gust_index']*93
            self.entries.append((schedule,transport))

    def density(self,t,prototype=False):
        tau=np.zeros(self.shape,np.float32);weighted_color=np.zeros((*self.shape,3),np.float32)
        for schedule,transport in self.entries:
            age=(float(t)+schedule['age_at_zero'])%self.duration
            fade=smooth(age/schedule['fade_in'])*smooth((self.duration-age)/schedule['fade_out'])
            alpha,color=transport.density(age,True)
            optical=-np.log1p(-np.minimum(alpha,.999999))*fade
            tau+=optical;weighted_color+=color*optical[...,None]
        alpha=np.minimum(-np.expm1(-tau),self.c['max_opacity'])
        color=weighted_color/np.maximum(tau[...,None],1e-8)
        return alpha,color
