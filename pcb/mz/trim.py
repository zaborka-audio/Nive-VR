# trim.py dsn in.json out.json [keep_points.json] : iteratively delete dead-end track segments
import sys,os,json,subprocess,ast
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from geo import load,LAY
from shapely.geometry import Point,Polygon,LineString
from shapely.strtree import STRtree
ps,pins,pinnet,_,_=load(sys.argv[1]);R0=json.load(open(sys.argv[2]))
KEEP=[tuple(k) for k in json.load(open(sys.argv[4]))] if len(sys.argv)>4 else []
R=[]
for r in R0:
    p=r['path']
    if r.get('via'): R.append(r);continue
    for a,b in zip(p,p[1:]):
        if a[0]!=b[0]: R.append({'net':r['net'],'w':12,'path':[list(a),list(b)],'via':True})
        elif (a[1],a[2])!=(b[1],b[2]): R.append({'net':r['net'],'w':r.get('w',12),'path':[list(a),list(b)]})
def padgeom(sh,x,y):
    k,a=sh
    if k=='circle': return Point(x+(a[1] if len(a)>1 else 0),y+(a[2] if len(a)>2 else 0)).buffer(a[0]/2,16)
    a=a[1:];return Polygon([(x+a[i],y+a[i+1]) for i in range(0,len(a)-1,2)])
PG=[[],[],[]];PN=[[],[],[]]
for pid,(pst,x,y) in pins.items():
    n=pinnet.get(pid)
    if not n: continue
    for z,L in enumerate(LAY):
        if L in ps[pst]: PG[z].append(padgeom(ps[pst][L],x,y));PN[z].append(n)
PT=[STRtree(g) for g in PG]
removed=[]
for it in range(200):
    G=[[],[],[]];N=[[],[],[]]
    for i,r in enumerate(R):
        p=r['path']
        if r.get('via'):
            for z in range(3): G[z].append(Point(p[0][1],p[0][2]).buffer(15.75));N[z].append((r['net'],i))
        else: G[p[0][0]].append(LineString([(p[0][1],p[0][2]),(p[1][1],p[1][2])]).buffer(r['w']/2));N[p[0][0]].append((r['net'],i))
    T=[STRtree(g) for g in G];dead=set()
    for i,r in enumerate(R):
        if r.get('via'): continue
        n=r['net'];w=r['w']
        for e in r['path']:
            z=e[0];pt=Point(e[1],e[2])
            if any(abs(e[1]-k[2])<1 and abs(e[2]-k[3])<1 and k[0]==n for k in KEEP): continue
            if any(PN[z][j]==n and PG[z][j].distance(pt)<w/2 for j in PT[z].query(pt.buffer(w))): continue
            if any(N[z][j][0]==n and N[z][j][1]!=i and G[z][j].distance(pt)<w/2 for j in T[z].query(pt.buffer(w))): continue
            dead.add(i)
    # orphan vias: touching own copper on fewer than 1 layer item
    for i,r in enumerate(R):
        if not r.get('via'): continue
        p=r['path'][0];pt=Point(p[1],p[2]).buffer(15.75);n=r['net']
        cnt=sum(1 for z in range(3) for j in T[z].query(pt) if N[z][j][0]==n and N[z][j][1]!=i and G[z][j].intersects(pt))
        pad=any(PN[z][j]==n and PG[z][j].intersects(pt) for z in range(3) for j in PT[z].query(pt))
        if cnt<=1 and not pad and n not in ('GND','GNDA'): dead.add(i)
    if not dead: break
    short=0
    for i in sorted(dead):
        r=R[i]
        if r.get('via'): continue
        n=r['net'];w=r['w'];a,b=r['path'];z=a[0]
        # which end is dead?
        def alive(e):
            pt=Point(e[1],e[2])
            if any(abs(e[1]-k[2])<1 and abs(e[2]-k[3])<1 and k[0]==n for k in KEEP): return True
            if any(PN[z][j]==n and PG[z][j].distance(pt)<w/2 for j in PT[z].query(pt.buffer(w))): return True
            return any(N[z][j][0]==n and N[z][j][1]!=i and G[z][j].distance(pt)<w/2 for j in T[z].query(pt.buffer(w)))
        if alive(a): S,E=a,b
        elif alive(b): S,E=b,a
        else: continue
        L=LineString([(S[1],S[2]),(E[1],E[2])]);best=0
        for j in T[z].query(L.buffer(w)):
            if N[z][j][0]!=n or N[z][j][1]==i: continue
            g=G[z][j]
            if g.distance(L)>=w/2: continue
            # farthest point of L within reach of g
            near=L.intersection(g.buffer(w/2-1.5))
            if near.is_empty: continue
            for c in (near.geoms if hasattr(near,'geoms') else [near]):
                for q in c.coords: best=max(best,L.project(Point(q)))
        if best>1:
            q=L.interpolate(best);E[1],E[2]=round(q.x,2),round(q.y,2);short+=1;dead.discard(i)
    dead=set(dead)
    for i in sorted(dead,reverse=True): removed.append(R.pop(i))
    if short and not dead: continue
json.dump(R,open(sys.argv[3],'w'))
import collections
print('removed',len(removed),collections.Counter(r['net'] for r in removed).most_common(30))
