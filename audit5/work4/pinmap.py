import sys; sys.path.insert(0,'work4')
from model import *
import pickle
comps,j=load_sch_json()
pins,pst,nets,wires,vias=load_pcb()
assign,g=pickle.load(open('work4/assign.pkl','rb'))
assign['8b7b97d49794ecfe']='J7';assign['bc845b9982dbd27e']='J8'
def nk(s):
    m=re.match(r'([A-Za-z]*)(\d+)',s); return (m.group(1),int(m.group(2)))
ok=0;bad=[]
for k,d in assign.items():
    pl=g[k]; sp=sorted(comps[d]['pins'],key=nk)
    a=[pins[x]['net'] or '' for x in pl]; b=[comps[d]['pins'][n]['net'] for n in sp]
    if d in('J7','J8'): a=a[2:]
    if a==b: ok+=1
    else: bad.append((d,len(pl),comps[d]['props'].get('Footprint'),sum(x!=y for x,y in zip(a,b))))
print(ok,len(bad))
for b in sorted(bad,key=lambda x:x[2] or ''): print(b)
