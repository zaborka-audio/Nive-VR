import sys; sys.path.insert(0,'work4')
from model import *
import pickle
comps,j=load_sch_json()
pins,pst,nets,wires,vias=load_pcb()
real={k:v for k,v in pins.items() if v['ps']!=VIAPS}
g=collections.defaultdict(list)
for k,v in real.items(): g[k[:16]].append(k)
def suf(k): return int(k[16:]) if k[16:] else 0
for k in g: g[k].sort(key=suf)
holes=[k for k,v in g.items() if len(v)==1]
print('single-pin groups',[(k,real[g[k][0]]['net'],real[g[k][0]]['x'],real[g[k][0]]['y']) for k in holes])
def ms(l): return tuple(sorted(x or '' for x in l))
sm=collections.defaultdict(list)
for d,c in comps.items(): sm[ms(p['net'] for p in c['pins'].values())].append(d)
pm=collections.defaultdict(list)
for k,v in g.items():
    if len(v)>1: pm[ms(real[x]['net'] for x in v)].append(k)
unm_s=[];unm_p=[];assign={}
for m in set(sm)|set(pm):
    a=sm.get(m,[]);b=pm.get(m,[])
    if len(a)==len(b):
        for x,y in zip(sorted(a),sorted(b)): assign[y]=x
    else:
        unm_s+= [(x,m) for x in a]; unm_p+=[(y,m) for y in b]
print('matched',len(assign),'unmatched sch',len(unm_s),'pcb',len(unm_p))
for x,m in unm_s: print(' S',x,len(m),comps[x]['pins'] if len(m)<8 else m[:6])
for y,m in unm_p: print(' P',y,len(m),[(k[16:],real[k]['net'],real[k]['x'],real[k]['y']) for k in g[y]][:8])
pickle.dump((assign,dict(g)),open('work4/assign.pkl','wb'))
