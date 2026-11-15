import sys; sys.path.insert(0,'work4')
from geom import *
pins,pst,nets,wires,vias=load_pcb()
print('via0',pst['via0'])
vp={(round(v['x'],2),round(v['y'],2)):v['net'] for v in vias}
fp={(round(p['x'],2),round(p['y'],2)):p['net'] for p in pins.values() if p['ps']==VIAPS}
print(len(vp),len(fp),'same coords',set(vp)==set(fp),'same nets',vp==fp)
j=json.load(open('pcb_pours4.json',encoding='utf8'))
P=[(p['x'],p['y']) for p in pins.values()]
import numpy as np
P=np.array(P)
for sign in (1,-1):
    cs=[]
    for p in j['poured']:
        for f in p['PourFills']:
            if f['fill']:
                for sub in f['path']['complexPolygon']: path_pts(sub,sign,cs)
    hit=0
    for cx,cy,r,a in cs[:3000]:
        d=np.hypot(P[:,0]-cx,P[:,1]-cy).min()
        if d<1: hit+=1
    print('sign',sign,'arcs',len(cs),'centered on a pad (first 3000):',hit)
cs=[]
for p in j['poured']:
    for f in p['PourFills']:
        if f['fill']:
            for sub in f['path']['complexPolygon']: path_pts(sub,1,cs)
c=collections.Counter()
ex=[]
for cx,cy,r,a in cs:
    d=np.hypot(P[:,0]-cx,P[:,1]-cy).min()
    c[(d<1, round(r,1))]+=1
    if d>=1 and len(ex)<15: ex.append((round(cx,1),round(cy,1),round(r,2),round(a,1),round(d,1)))
print(sorted(c.items(),key=lambda x:-x[1])[:40]); print(ex)
