import sys; sys.path.insert(0,'work4')
from model import *
import pickle
pins,pst,nets,wires,vias=load_pcb()
pinmap=pickle.load(open('work4/pinmap.pkl','rb'))
for J in ('J1','J2'):
    rows=collections.defaultdict(list); amb=[]
    for pid,(d,c) in pinmap.items():
        if d!=J: continue
        p=pins[pid]
        if len(c)==1:
            m=re.match(r'([A-C]?)(\d+)',c[0]); rows[m.group(1)].append((int(m.group(2)),p['x'],p['y']-9850,p['net']))
        else: amb.append((c,p['x'],p['y']-9850,p['net']))
    print(J,'ambiguous pads',len(amb))
    for r,l in sorted(rows.items()):
        l.sort()
        ys={round(y,1) for n,x,y,_ in l}
        # fit x vs n
        import numpy as np
        n=np.array([a[0] for a in l]);x=np.array([a[1] for a in l])
        if len(l)>1 and r:
            k,b=np.polyfit(n,x,1); res=np.abs(x-(k*n+b)).max()
            print('  row',r,'pins',len(l),'y',ys,'pitch %.2f x(n=1)=%.1f maxresid %.2f'%(k,k+b,res))
        else: print('  row',repr(r),l)
    # ambiguous pads positions: which row/col slots free
    for c,x,y,n in sorted(amb,key=lambda a:(a[2],a[1])): print('    amb',n,'(%.1f,%.1f)'%(x,y),'|'.join(c)[:60])
