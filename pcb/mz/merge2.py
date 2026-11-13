import json,sys,math,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from geo import load
ps,pins,pinnet,_,_=load('v2.dsn')
byn={}
for pid,(p,x,y) in pins.items():
    sh=ps[p].get('TopLayer');r=sh[1][0]/2 if sh[0]=='circle' else 25
    byn.setdefault(pinnet.get(pid),[]).append((x,y,r))
base=json.load(open(sys.argv[1]));new=[]
for f in sys.argv[2:-1]:
    pre,nm=f.split(':');n0=len(json.load(open(pre)));new+=json.load(open(nm))[n0:]
fix=0
for r in new:
    p=r['path']
    for end in (0,-1):
        z,x,y=p[end]
        q=min(byn.get(r['net'],[]),key=lambda q:math.hypot(q[0]-x,q[1]-y),default=None)
        if q and 0<math.hypot(q[0]-x,q[1]-y)<q[2]+10:
            if end==0: p.insert(0,(z,q[0],q[1]))
            else: p.append((z,q[0],q[1]))
            fix+=1
print('new',len(new),'snapped',fix)
json.dump(base+new,open(sys.argv[-1],'w'))
