# unr3.py dsn result.json : unrouted connections per net (pads+wires+vias union; GND/GNDA pins inside own plane count as connected)
import sys,os,json,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('MZG','25')
from geo import load,LAY
from shapely.geometry import Point,Polygon,LineString
from shapely.strtree import STRtree
ps,pins,pinnet,_,_=load(sys.argv[1]);R=json.load(open(sys.argv[2]))
H=float(os.environ.get('MZH','9850'))
def P(L): return Polygon([(L[i],L[i+1]+H) for i in range(0,len(L),2)])
GA=[P([4470,-15,9200,-15,9200,-4250,5980,-4250,5980,-6380,4470,-6380]),P([8880,-8500,10935,-8500,10935,-9835,8880,-9835]),P([11295,-8500,13560,-8500,13560,-9835,11295,-9835])]
inA=lambda x,y:any(g.contains(Point(x,y)) for g in GA)
whichA=lambda x,y:next((k for k,g in enumerate(GA) if g.contains(Point(x,y))),None)
items=[]  # (net,layerset,geom,id)
def padg(sh,x,y):
    k,a=sh
    if k=='circle': return Point(x,y).buffer(a[0]/2,8)
    a=a[1:];return Polygon([(x+a[i],y+a[i+1]) for i in range(0,len(a)-1,2)])
for pid,(pst,x,y) in pins.items():
    n=pinnet.get(pid)
    if n: items.append((n,(0,1,2),padg(ps[pst].get('TopLayer') or list(ps[pst].values())[0],x,y),'P'+pid,(x,y)))
for i,r in enumerate(R):
    p=r['path']
    for a,b in zip(p,p[1:]):
        if a[0]!=b[0] or r.get('via'): items.append((r['net'],(0,1,2),Point(a[1],a[2]).buffer(15.7,8),'V%d'%i,None))
        else: items.append((r['net'],(a[0],),LineString([(a[1],a[2]),(b[1],b[2])]).buffer(r.get('w',12)/2,4),'W%d'%i,None))
    if r.get('endvia'): items.append((r['net'],(0,1,2),Point(p[-1][1],p[-1][2]).buffer(15.7,8),'E%d'%i,None))
par=list(range(len(items)+2))
def f(a):
    while par[a]!=a: par[a]=par[par[a]];a=par[a]
    return a
PG,PA=len(items),len(items)+1
PA2,PA3=len(items)+2,len(items)+3
par+=[PA2,PA3]
AREAS=json.loads(os.environ.get('AREAS','[]'))
par+=list(range(len(par),len(par)+len(AREAS)))
AG=[(a[0],P(a[1])) for a in AREAS]
par+=list(range(len(par),len(par)+len(AREAS)+4))
tree=STRtree([it[2] for it in items])
for i,it in enumerate(items):
    for j in tree.query(it[2]):
        if j<=i: continue
        jt=items[j]
        if jt[0]==it[0] and set(jt[1])&set(it[1]) and it[2].intersects(jt[2]): par[f(i)]=f(j)
    if it[4] and it[0] in('GND','GNDA'):
        x,y=it[4];a=inA(x,y)
        if it[0]=='GNDA' and a: par[f(i)]=f([PA,PA2,PA3][whichA(x,y)])
        if it[0]=='GND' and not a: par[f(i)]=f(PG)
    if it[3][0] in 'VE' and it[0] in ('GND','GNDA'):
        x,y=it[2].centroid.coords[0];a=inA(x,y)
        if it[0]=='GNDA' and a: par[f(i)]=f(PA)
        if it[0]=='GND' and not a: par[f(i)]=f(PG)
for i,it in enumerate(items):
    for k,(an,ag) in enumerate(AG):
        if it[0]==an and 2 in it[1] and it[2].intersects(ag): par[f(i)]=f(PA3+1+k)
groups=collections.defaultdict(lambda:collections.defaultdict(list))
for i,it in enumerate(items):
    if it[3][0]=='P': groups[it[0]][f(i)].append(it[4])
tot=0;res={}
for n,g in groups.items():
    if len(g)>1: tot+=len(g)-1;res[n]=[[tuple(round(v) for v in pts[0]) for pts in g.values()]]
print('unrouted connections',tot,'nets',len(res))
for n,v in sorted(res.items()): print(n,len(v[0])-1,v[0][:8])
json.dump(res,open(sys.argv[2]+'.unr.json','w'))
