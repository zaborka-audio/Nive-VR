import sys; sys.path.insert(0,'work4')
from geom import *
pins,pst,nets,wires,vias=load_pcb()
pt=(8072.0,-8039.2+YOFF)
for i,w in enumerate(wires):
    if w['net']=='OUT2_C' and min(math.dist(p,pt) for p in w['pts'])<60: print('wire',w['layer'],w['w'],[(round(a,1),round(b-YOFF,1)) for a,b in w['pts']])
for v in vias:
    if math.dist((v['x'],v['y']),pt)<80: print('via',v['net'],v['x'],v['y']-YOFF)
for p in pins.values():
    if p['ps']!=VIAPS and math.dist((p['x'],p['y']),pt)<120: print('pad',p['net'],p['x'],p['y']-YOFF,p['ps'])
