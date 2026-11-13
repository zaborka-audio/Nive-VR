import sys,os,json,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('MZG','25')
from geo import load
from shapely.geometry import Point,Polygon,LineString
from shapely.strtree import STRtree
ps,pins,pinnet,_,_=load(sys.argv[1]);R=json.load(open(sys.argv[2]))
nets=set(json.load(open(sys.argv[3]))) if len(sys.argv)>3 else None
items=[]
for pid,(pst,x,y) in pins.items():
    n=pinnet.get(pid)
    if not n or (nets and n not in nets): continue
    sh=ps[pst].get('TopLayer');g=Point(x,y).buffer(sh[1][0]/2,16) if sh[0]=='circle' else Polygon([(x+sh[1][1+i],y+sh[1][2+i]) for i in range(0,len(sh[1])-2,2)])
    items.append((n,(0,1,2),g,('P',pid,x,y)))
for i,r in enumerate(R):
    if nets and r['net'] not in nets: continue
    p=r['path']
    for a,b in zip(p,p[1:]):
        if r.get('via') or a[0]!=b[0]: items.append((r['net'],(0,1,2),Point(a[1],a[2]).buffer(15.7,16),('V',i,a[1],a[2])))
        else: items.append((r['net'],(a[0],),LineString([(a[1],a[2]),(b[1],b[2])]).buffer(r.get('w',12)/2,8),('W',i,a[1],a[2])))
    if r.get('endvia'): items.append((r['net'],(0,1,2),Point(p[-1][1],p[-1][2]).buffer(15.7,16),('V',i,p[-1][1],p[-1][2])))
par=list(range(len(items)))
def f(a):
    while par[a]!=a: par[a]=par[par[a]];a=par[a]
    return a
t=STRtree([it[2] for it in items])
for i,it in enumerate(items):
    for j in t.query(it[2]):
        if j>i and items[j][0]==it[0] and set(items[j][1])&set(it[1]) and it[2].intersects(items[j][2]): par[f(i)]=f(j)
g=collections.defaultdict(list)
for i,it in enumerate(items): g[(it[0],f(i))].append(it[3])
orph=collections.defaultdict(set);multi=collections.Counter()
for (n,root),m in g.items():
    if not any(k[0]=='P' for k in m): orph[n]|={k[1] for k in m}
for n in {k[0] for k in g}:
    pg=[m for (nn,r),m in g.items() if nn==n and any(k[0]=='P' for k in m)]
    if len(pg)>1: multi[n]=len(pg)-1
print('orphan fragment nets',len(orph),{n:sorted(v) for n,v in list(orph.items())[:20]})
print('split nets (exact geometry)',dict(multi))
json.dump({n:sorted(v) for n,v in orph.items()},open(sys.argv[2]+'.orph.json','w'))
