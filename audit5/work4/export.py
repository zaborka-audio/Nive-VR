import sys,csv; sys.path.insert(0,'work4')
from geom import *
weak=pickle.load(open('work4/weak.pkl','rb')); ant=pickle.load(open('work4/antenna.pkl','rb'))
with open('work4/weak_joints.csv','w',newline='',encoding='utf8') as f:
    w=csv.writer(f); w.writerow(['neck_mil','net','layer','x','y','only_path(bridge)','item_a','item_b'])
    for r in weak: w.writerow(['%.2f'%r['neck'],r['net'],{'1':'Top','2':'Bottom','15':'Inner1','16':'Inner2'}[r['layer']],'%.0f'%r['x'],'%.0f'%r['y'],'YES' if r['bridge'] else 'no',r['a'],r['b']])
with open('work4/dead_end_stubs.csv','w',newline='',encoding='utf8') as f:
    w=csv.writer(f); w.writerow(['length_mil','net','layers','vias_in_stub','free_end','attached_to'])
    for r in ant: w.writerow(['%.0f'%r[0],r[1],'/'.join(r[2]),r[3],r[4],'; '.join(r[5])])
b=[r for r in weak if r['bridge']]
print(len(weak),len(b),sum(r['neck']<6 for r in weak),sum(r['neck']<8 for r in b))
print(collections.Counter(r['kinds'] for r in weak))
comps,j=load_sch_json()
print('sch NC pins',sum(1 for c in comps.values() for p in c['pins'].values() if not p['net']))
pins,pst,nets,wires,vias=load_pcb()
print('widths',sorted({w['w'] for w in wires}))
print('net pin counts max',sorted(((len(v),k) for k,v in nets.items()),reverse=True)[:4])
