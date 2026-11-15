import sys; sys.path.insert(0,'work4')
from geom import *
import numpy as np
pins,pst,nets,wires,vias=load_pcb()
D=pickle.load(open('work4/conn.pkl','rb')); items=D['items'];roots=D['roots']
ends=collections.defaultdict(list)
for i,w in enumerate(wires):
    for k,e in enumerate(w['pts']): ends[w['layer']].append((e,i,k))
hyp=[]
for l,es in ends.items():
    P=np.array([e[0] for e in es])
    for a,(e,i,k) in enumerate(es):
        d=np.hypot(P[:,0]-e[0],P[:,1]-e[1])
        same=[b for b,(e2,i2,k2) in enumerate(es) if i2==i]
        d[same]=1e9
        if d.min()<0.01: continue
        for b in np.where(d<10.0)[0]:
            if wires[es[b][1]]['net']==wires[i]['net'] and a<b:
                hyp.append((l,wires[i]['net'],e,tuple(P[b]),min(wires[i]['w'],wires[es[b][1]]['w'])))
print('hypothetical <10 mil segments between same-net free ends:',len(hyp))
widx={it['ref']:i for i,it in enumerate(items) if it['kind']=='wire'}
netroot={}
for i,it in enumerate(items): netroot.setdefault(it['net'],roots[i])
bylayer=collections.defaultdict(list)
for i,it in enumerate(items): bylayer[it['layer']].append(i)
trees={l:(STRtree([items[i]['geom'] for i in idx]),idx) for l,idx in bylayer.items()}
worst=1e9
for l,net,p,q,w in hyp:
    g=LineString([p,q]).buffer(w/2,16)
    t,idx=trees[l]
    for x in t.query(g,predicate='dwithin',distance=9.84):
        i=idx[x]
        if roots[i]!=netroot[net]:
            d=g.distance(items[i]['geom']); worst=min(worst,d)
            print('hyp seg clearance %.2f'%d,net,'vs',items[i]['net'],items[i]['kind'],'L'+l,'(%.0f,%.0f)'%(p[0],p[1]-YOFF))
print('done; worst',worst)
