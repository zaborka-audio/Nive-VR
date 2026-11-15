import sys; sys.path.insert(0,'work4')
from geom import *
pins,pst,nets,wires,vias=load_pcb()
pinmap=pickle.load(open('work4/pinmap.pkl','rb'))
D=pickle.load(open('work4/conn.pkl','rb')); items=D['items'];roots=D['roots'];touch=D['touch'];thru=D['thru']
# spokes sanity
ns=0;bad=0
for i,it in enumerate(items):
    if it['kind']=='spoke':
        ns+=1
        k={items[o]['kind'] for o in touch.get(i,())}
        if 'pour' not in k or not (k&{'pad','via'}): bad+=1; print('spoke not bridging pour<->pad',it['ref'],k)
print('spokes',ns,'not bridging',bad)
st=collections.Counter(); weak=[]
for ids in thru:
    it0=items[ids[0]]
    if it0['net'] not in('GND','GNDA'): continue
    sp=0;direct=False;tr=0
    for i in ids:
        for o in touch.get(i,()):
            k=items[o]['kind']
            if k=='spoke': sp+=1
            elif k=='pour': direct=True
            elif k in('wire',): tr+=1
    st[(it0['kind'],it0['net'],'direct' if direct else 'spokes=%d'%sp,'tracks' if tr else 'no-tracks')]+=1
    if not direct and sp<2 and tr==0:
        if it0['kind']=='pad': p=pins[it0['ref']]; weak.append((it0['net'],pinmap.get(it0['ref'],('HOLE',[]))[0],p['x'],p['y']-YOFF,sp))
        else: v=vias[it0['ref']]; weak.append((it0['net'],'via',v['x'],v['y']-YOFF,sp))
for k,v in sorted(st.items()): print(k,v)
print('pins/vias on GND/GNDA with <2 spokes and no tracks:',weak)
