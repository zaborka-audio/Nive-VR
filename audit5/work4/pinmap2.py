import sys; sys.path.insert(0,'work4')
from model import *
import pickle
comps,j=load_sch_json()
pins,pst,nets,wires,vias=load_pcb()
assign,g=pickle.load(open('work4/assign.pkl','rb'))
assign['8b7b97d49794ecfe']='J7';assign['bc845b9982dbd27e']='J8'
byfp=collections.defaultdict(list)
for k,d in assign.items(): byfp[comps[d]['props'].get('Footprint')].append(k)
pinmap={}
tot=uniq=amb=0; single=[]
for fp,ks in byfp.items():
    n=len(g[ks[0]]); assert all(len(g[k])==n for k in ks)
    cand={}
    for r in range(n):
        c=None
        for k in ks:
            d=assign[k]; pn=pins[g[k][r]]['net'] or ''
            cs={m for m,p in comps[d]['pins'].items() if p['net']==pn}
            c=cs if c is None else c&cs
        cand[r]=c
    npins=len(comps[assign[ks[0]]]['pins'])
    changed=True
    while changed:
        changed=False
        for s,c in cand.items():
            if len(c)==1:
                for s2,c2 in cand.items():
                    if s2!=s and c&c2: cand[s2]=c2-c; changed=True
    empt=[s for s,c in cand.items() if not c]
    u=sum(len(c)==1 for c in cand.values()); a=sum(len(c)>1 for c in cand.values())
    tot+=n*len(ks);uniq+=u*len(ks);amb+=a*len(ks)
    if len(ks)==1: single.append((assign[ks[0]],n))
    if len(empt)!=n-npins:
        print('INCONSISTENT',fp,[assign[k] for k in ks][:6],'pads',n,'pins',npins,'unique',u,'ambig',a,'empty',empt)
    for k in ks:
        for r in range(n): pinmap[g[k][r]]=(assign[k],sorted(cand[r]))
print('total pads',tot,'unique',uniq,'ambiguous(same-net/NC pins)',amb)
print('single-instance footprints',single)
pickle.dump(pinmap,open('work4/pinmap.pkl','wb'))
# per-pin partition check using pinmap: every pad net == sch net for all candidates
bad=0
for pid,(d,c) in pinmap.items():
    for m in c:
        if (pins[pid]['net'] or '')!=comps[d]['pins'][m]['net']: bad+=1;print('MISMATCH',d,m,pins[pid]['net'])
print('mismatches',bad)
