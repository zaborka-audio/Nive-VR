# dangle.py dsn model.json : track ends touching nothing of own net (pad/via/other track)
import sys,os,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from geo import load,LAY
from shapely.geometry import Point,Polygon,LineString
from shapely.strtree import STRtree
ps,pins,pinnet,_,_=load(sys.argv[1]);R=json.load(open(sys.argv[2]))
def padgeom(sh,x,y):
    k,a=sh
    if k=='circle': return Point(x+(a[1] if len(a)>1 else 0),y+(a[2] if len(a)>2 else 0)).buffer(a[0]/2,16)
    a=a[1:];return Polygon([(x+a[i],y+a[i+1]) for i in range(0,len(a)-1,2)])
G=[[],[],[]];N=[[],[],[]];ends=[]
for pid,(pst,x,y) in pins.items():
    n=pinnet.get(pid)
    if not n: continue
    for z,L in enumerate(LAY):
        if L in ps[pst]: G[z].append(padgeom(ps[pst][L],x,y));N[z].append((n,-1))
for i,r in enumerate(R):
    p=r['path']
    for a,b in zip(p,p[1:]):
        if a[0]!=b[0]:
            for z in range(3): G[z].append(Point(a[1],a[2]).buffer(15.75));N[z].append((r['net'],i))
        else:
            G[a[0]].append(LineString([(a[1],a[2]),(b[1],b[2])]).buffer(r.get('w',12)/2));N[a[0]].append((r['net'],i))
    segs=[(a,b) for a,b in zip(p,p[1:]) if a[0]==b[0]]
    if segs and not r.get('via'): ends+= [(r['net'],i,p[0],r.get('w',12)),(r['net'],i,p[-1],r.get('w',12))]
T=[STRtree(g) for g in G];bad=[]
for n,i,e,w in ends:
    pt=Point(e[1],e[2]);z=e[0]
    if not any(N[z][j][0]==n and N[z][j][1]!=i and G[z][j].distance(pt)<w/2 for j in T[z].query(pt.buffer(w))): bad.append((n,z,round(e[1]),round(e[2])))
print('dangling ends',len(bad));[print(b) for b in bad[:40]]
