import sys; sys.path.insert(0,'work4')
from model import *
comps,j=load_sch_json()
parts,snets=load_sch_pads()
print('sch comps',len(comps),'pads parts',len(parts),'nets',len(snets))
# json vs pads
jn=collections.defaultdict(set)
for d,c in comps.items():
    for n,p in c['pins'].items():
        if p['net']: jn[p['net']].add(f'{d}.{n}')
pn={k:set(v) for k,v in snets.items()}
print('json nets',len(jn),'equal',jn==pn)
for k in set(jn)|set(pn):
    if jn.get(k)!=pn.get(k): print(' diff',k,jn.get(k,set())^pn.get(k,set()))
print('parts diff',set(parts)^set(comps))
print('sch pins',sum(len(c['pins']) for c in comps.values()),'unconnected',[(d,n,p['name']) for d,c in comps.items() for n,p in c['pins'].items() if not p['net']])
pins,pst,nets,wires,vias=load_pcb()
real={k:v for k,v in pins.items() if v['ps']!=VIAPS}
print('pcb real pins',len(real),'nets',len(nets),'no-net pins',sum(1 for v in real.values() if v['net'] is None))
print('pcb nets not in sch',sorted(set(nets)-set(pn)),'sch not in pcb',sorted(set(pn)-set(nets)))
print('via pins without net',sum(1 for v in pins.values() if v['ps']==VIAPS and v['net'] is None))
g=collections.defaultdict(list)
for k,v in real.items(): g[k[:16]].append(k)
print('groups',len(g))
cnt=collections.Counter(len(v) for v in g.values()); print(sorted(cnt.items()))
sc=collections.Counter(len(c['pins']) for c in comps.values()); print(sorted(sc.items()))
