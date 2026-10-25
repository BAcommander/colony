from pathlib import Path
import json
H=Path(__file__).parent
c=json.loads((H.parent/'snowline-animation-v1/scene.json').read_text())
c['feedback']='wierd glitch near the satelitte that needs fixed, we need more coloured lights, and also some of them dimming can we do any movement in the building? or internal lights or monitors and buttons belllows / on the sides of the minotiro, this is decent but needs a big 200% improvement, also the thumbnail sohuld take inspirtaion from the Tron one we made for video 11 but for Star Wars / hoth maybe?'
c['scope']='V2 refinement; v1 decent but needs improvement. Same source art. Motion and thumbnail pending review.'
# V1 missed the feed arm, left machinery and lower support; all fall outside
# this conservative sampling/transport exclusion. Static light masks are separate.
c['dish_guard']=[[800,151],[854,152],[889,191],[889,224],[868,228],[868,268],[807,267],[790,244],[797,211],[808,195]]
c['new_details']='Colored instrument buttons, phased mechanical key lamps, habitat telemetry, bridge practicals and local room lamp/spill. No new people or vehicles.'
c['button_groups']=[
 {'xy':[28,289],'size':[7,8],'color':[255,67,30],'phase':0},
 {'xy':[28,312],'size':[7,8],'color':[255,150,28],'phase':3.2},
 {'xy':[29,334],'size':[5,5],'color':[90,190,230],'phase':7.4},
 {'xy':[16,478],'size':[6,7],'color':[100,205,210],'phase':5.3},
 {'xy':[16,500],'size':[6,7],'color':[255,164,40],'phase':12.8},
 {'xy':[16,521],'size':[7,8],'color':[255,116,26],'phase':14.1},
 {'xy':[16,543],'size':[6,7],'color':[230,50,30],'phase':9.3},
 {'xy':[160,594],'size':[8,6],'color':[255,65,20],'phase':16.7}
]
c['keys']=[[[61,610],[76,608],[81,617],[65,619]],[[81,607],[96,605],[101,614],[85,616]],[[101,604],[115,602],[120,612],[105,613]],[[68,622],[83,619],[88,629],[73,632]],[[87,618],[103,616],[108,626],[92,629]],[[107,615],[121,614],[127,623],[112,626]],[[126,603],[139,601],[144,610],[132,612]]]
c['bridge_lights']=[{'poly':[[x,388],[x+20,388],[x+20,393],[x,393]],'phase':i*2.3} for i,x in enumerate([833,923,1015,1107,1198,1287,1377])]
c['habitat_screens']=[{'poly':[[445,329],[456,331],[456,342],[445,340]],'color':[105,205,224],'phase':2.6},{'poly':[[554,345],[562,346],[562,358],[554,357]],'color':[120,220,185],'phase':9.5}]
c['lamp_poly']=[[2,2],[173,53],[206,66],[193,86],[10,33]]
c['spill_poly']=[[1,157],[174,199],[217,248],[217,584],[255,653],[476,672],[466,731],[307,729],[186,677],[1,684]]
(H/'scene.json').write_text(json.dumps(c,indent=2)+'\n')
# Preserve original math while allowing region-local sampling coordinates.
p=H/'baseline.py';text=p.read_text();text=text.replace("mx=self.x-dx","mx=self.x-dx-getattr(self,'origin',(0,0))[0]\n    local_y=self.y-getattr(self,'origin',(0,0))[1]")
text=text.replace('mx,self.y,cv2.INTER_LINEAR','mx,local_y,cv2.INTER_LINEAR')
p.write_text(text)
