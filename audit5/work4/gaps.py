import sys; sys.path.insert(0,'work4')
from geom import *
import numpy as np
pins,pst,nets,wires,vias=load_pcb()
L=np.array([math.dist(*w['pts']) for w in wires])
print('segment length hist:',[(a,int(((L>=a)&(L<b)).sum())) for a,b in [(0,0.01),(0.01,2),(2,5),(5,8),(8,10),(10,12),(12,15),(15,20),(20,50)]])
# end-to-end gaps: endpoints (same layer, same net) not coincident with any other endpoint but with another endpoint within 15 mil
ends=collections.defaultdict(list)
for i,w in enumerate(wires):
    for k,e in enumerate(w['pts']): ends[w['layer']].append((e,i,k))
cnt=collections.Counter();gl=[]
out=[]
for l,es in ends.items():
    P=np.array([e[0] for e in es])
    for a,(e,i,k) in enumerate(es):
        d=np.hypot(P[:,0]-e[0],P[:,1]-e[1])
        d[[b for b,(e2,i2,k2) in enumerate(es) if i2==i]]=1e9
        if d.min()<0.01: continue
        b=int(d.argmin())
        if d[b]<20 and wires[es[b][1]]['net']==wires[i]['net']:
            # is the other end also 'free'?
            d2=np.hypot(P[:,0]-P[b,0],P[:,1]-P[b,1]); d2[[c for c,(e2,i2,k2) in enumerate(es) if i2==es[b][1]]]=1e9
            if d2.min()>=0.01 and a<b:
                gl.append(d[b]); out.append((wires[i]['net'],l,e,tuple(P[b]),d[b],wires[i]['w']))
print('free end pairs facing each other (<20 mil):',len(gl)); print(np.histogram(gl,bins=[0,2,4,6,8,10,12,15,20]))
for o in sorted(out,key=lambda x:-x[4])[:15]: print(o[0],'L'+o[1],'(%.1f,%.1f)->(%.1f,%.1f)'%(o[2][0],o[2][1]-YOFF,o[3][0],o[3][1]-YOFF),'gap %.2f w %.1f'%(o[4],o[5]))
