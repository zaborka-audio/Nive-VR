import sys; sys.path.insert(0,'work4')
from model import *
import pickle
comps,j=load_sch_json(); parts,_=load_sch_pads()
pins,pst,nets,wires,vias=load_pcb()
pinmap=pickle.load(open('work4/pinmap.pkl','rb'))
bycomp=collections.defaultdict(list)
for pid,(d,c) in pinmap.items(): bycomp[d].append((pid,c))
def nk(s):
    m=re.match(r'([A-Za-z]*)(\d+)',s); return (m.group(1),int(m.group(2)))
seen=set()
for d in sorted(bycomp,key=lambda x:(parts[x],x)):
    fp=parts[d]
    if len(bycomp[d])<4 or fp in seen: continue
    seen.add(fp)
    # sch net for each pad
    rows=[]
    for pid,c in bycomp[d]:
        p=pins[pid]; sq = pst[p['ps']][0][0]=='polygon' and len(pst[p['ps']][0])<=3+16
        rows.append((c,p['x'],p['y'],sq,p['net']))
    uni=[r for r in rows if len(r[0])==1]
    print('==',fp,d,'pads',len(rows),'unique',len(uni))
    if len(rows)>40: 
        continue
    for r in sorted(rows,key=lambda r:nk(r[0][0]) if r[0] else ('',0)):
        print('   %-14s (%8.1f,%8.1f) %s %s'%('|'.join(r[0]),r[1],r[2]-9850,'SQ' if r[3] else '  ',r[4]))
