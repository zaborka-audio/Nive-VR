import sys; sys.path.insert(0,'work4')
from model import *
import pickle
comps,j=load_sch_json()
parts,_=load_sch_pads()
pins,pst,nets,wires,vias=load_pcb()
assign,g=pickle.load(open('work4/assign.pkl','rb'))
def shape(ps):
    s=pst[ps][0]
    if s[0]=='circle': return 'circ%s'%s[2]
    xs=[float(v) for v in s[3::2]];ys=[float(v) for v in s[4::2]]
    return 'poly%dpt %.0fx%.0f'%(len(xs),max(xs)-min(xs),max(ys)-min(ys))
byfp=collections.defaultdict(list)
for k,d in assign.items():
    if len(g[k])<=3: byfp[parts[d]].append(k)
for fp,ks in sorted(byfp.items()):
    st=collections.Counter()
    ex={}
    for k in ks:
        d=assign[k]
        # map sch pin -> pad shape
        key=[]
        for m,p in sorted(comps[d]['pins'].items()):
            sh=sorted({shape(pins[x]['ps']) for x in g[k] if (pins[x]['net'] or '')==p['net']})
            key.append(f"{m}/{p['name']}:{'|'.join(sh)}")
        st[tuple(key)]+=1; ex.setdefault(tuple(key),[]).append(d)
    print(fp,len(ks))
    for kk,v in st.items(): print('    ',v,kk,ex[kk][:8])
