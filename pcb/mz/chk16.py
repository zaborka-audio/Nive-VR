import sys,json,math
sys.path.insert(0,'mz')
from geo import *
ps,pins,pinnet,wires,vias=load('ee16.dsn')
R=json.load(open(sys.argv[1]));H=9850
def dss(a,b,c,d):
    def dp(p,a,b):
        ax,ay=a;bx,by=b;dx,dy=bx-ax,by-ay;L=dx*dx+dy*dy
        t=0 if L==0 else max(0,min(1,((p[0]-ax)*dx+(p[1]-ay)*dy)/L));return math.hypot(p[0]-ax-t*dx,p[1]-ay-t*dy)
    return min(dp(a,c,d),dp(b,c,d),dp(c,a,b),dp(d,a,b))
LZ={1:'1',2:'2',16:'16'}
bad=[]
for n,L,x1,y1,x2,y2 in R['lines']:
    a=(x1,y1+H);b=(x2,y2+H)
    for wn,wl,ww,pts in wires:
        if wn==n or wl!=LZ[L]: continue
        for p,q in zip(pts,pts[1:]):
            d=dss(a,b,p,q)-6-ww/2
            if d<9.8: bad.append((round(d,1),n,'wire',wn,L,a))
    for vn,vx,vy in vias:
        if vn==n: continue
        d=dss(a,b,(vx,vy),(vx,vy))-6-15.75
        if d<9.8: bad.append((round(d,1),n,'via',vn,L,a))
print(len(bad));[print(b) for b in sorted(bad)[:30]]
bad=[]
for n,x,y in R['vias']:
    a=(x,y+H)
    for wn,wl,ww,pts in wires:
        if wn==n: continue
        for p,q in zip(pts,pts[1:]):
            d=dss(a,a,p,q)-15.75-ww/2
            if d<9.8: bad.append((round(d,1),n,'via-wire',wn,a))
    for vn,vx,vy in vias:
        if vn!=n and math.hypot(vx-a[0],vy-a[1])-31.5<9.8: bad.append(('vv',n,vn))
    for pid,(pst,px,py) in pins.items():
        if pinnet.get(pid)==n: continue
        sh=ps[pst].get('TopLayer');
        if not sh: continue
        if sh[0]=='circle': r=sh[1][0]/2
        else:
            aa=sh[1][1:];r=max(math.hypot(aa[i],aa[i+1]) for i in range(0,len(aa)-1,2))
        d=math.hypot(px-a[0],py-a[1])-r-15.75
        if d<9.8: bad.append((round(d,1),n,'via-pad',pinnet.get(pid),a))
print('vias',len(bad));[print(b) for b in sorted(bad,key=str)[:20]]
