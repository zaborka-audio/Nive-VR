# chk2.py dsn result.json : clearance check (different nets, same layer) with shapely
import sys,os,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('MZG','25')
from geo import load,LAY
from shapely.geometry import Point,Polygon,LineString
from shapely.strtree import STRtree
ps,pins,pinnet,wires,vias=load(sys.argv[1]);R=json.load(open(sys.argv[2]))
CL=float(os.environ.get('CL','9.8'))
geo=[[],[],[]];own=[[],[],[]]
def padgeom(sh,x,y):
    k,a=sh
    if k=='circle': return Point(x+(a[1] if len(a)>1 else 0),y+(a[2] if len(a)>2 else 0)).buffer(a[0]/2,16)
    a=a[1:];return Polygon([(x+a[i],y+a[i+1]) for i in range(0,len(a)-1,2)])
for pid,(pst,x,y) in pins.items():
    n=pinnet.get(pid) or ('nc'+pid)
    for z,L in enumerate(LAY):
        if L in ps[pst]: geo[z].append(padgeom(ps[pst][L],x,y));own[z].append((n,'pad '+pid))
for i,r in enumerate(R):
    p=r['path'];w=r.get('w',12)
    for a,b in zip(p,p[1:]):
        if a[0]!=b[0]:
            for z in range(3): geo[z].append(Point(a[1],a[2]).buffer(15.75,16));own[z].append((r['net'],'via%d'%i))
        else:
            geo[a[0]].append(LineString([(a[1],a[2]),(b[1],b[2])]).buffer(w/2,8));own[a[0]].append((r['net'],'seg%d'%i))
    if r.get('endvia'):
        for z in range(3): geo[z].append(Point(p[-1][1],p[-1][2]).buffer(15.75,16));own[z].append((r['net'],'via%d'%i))
bad=[]
for z in range(3):
    t=STRtree(geo[z])
    for i,g in enumerate(geo[z]):
        for j in t.query(g.buffer(CL)):
            if j<=i or own[z][j][0]==own[z][i][0]: continue
            d=g.distance(geo[z][j])
            if d<CL: bad.append((round(d,1),z,own[z][i],own[z][j],tuple(round(v) for v in g.centroid.coords[0])))
bad.sort()
print('violations',len(bad))
for b in bad[:30]: print(b)
