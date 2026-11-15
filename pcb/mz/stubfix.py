# stubfix.py dsn_noviapins.dsn live_lines.json stubs.csv out.json
# Connectivity-based removal of dead-end copper on the LIVE board (EasyEDA coords).
#  - stubs: start at each free end (from stubs.csv) and eat items in BFS order while every pad of the net stays connected
#  - vias: any non-GND via whose removal keeps the net's pads connected and that touches copper on <2 layers
# Writes {'lines':[ids],'vias':[ids]} to out.json
import sys,os,json,csv,ast,math,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from geo import load,LAY
from shapely.geometry import Point,Polygon,LineString
H=9850;LZ={1:0,2:1,16:2}
ps,pins,pinnet,_,_=load(sys.argv[1]);D=json.load(open(sys.argv[2]))
def padgeom(sh,x,y):
    k,a=sh
    if k=='circle': return Point(x+(a[1] if len(a)>1 else 0),y+(a[2] if len(a)>2 else 0)).buffer(a[0]/2,16)
    a=a[1:];return Polygon([(x+a[i],y+a[i+1]) for i in range(0,len(a)-1,2)])
# items per net: ('pad',pid) ('L',id) ('V',id) with geometry per layer
items=collections.defaultdict(dict)
for pid,(pst,x,y) in pins.items():
    n=pinnet.get(pid)
    if not n or n in ('GND','GNDA'): continue
    items[n][('P',pid)]={z:padgeom(ps[pst][L],x,y) for z,L in enumerate(LAY) if L in ps[pst]}
for i,n,ly,x1,y1,x2,y2,w in D['L']:
    if n in ('GND','GNDA') or ly not in LZ: continue
    a,b=(x1,y1+H),(x2,y2+H)
    g=LineString([a,b]).buffer(w/2,8) if a!=b else Point(a).buffer(w/2,8)
    items[n][('L',i)]={LZ[ly]:g}
for i,n,x,y,hd,dia in D['V']:
    if n in ('GND','GNDA'): continue
    c=Point(x,y+H).buffer(dia/2,16);items[n][('V',i)]={0:c,1:c,2:c}
def adj(it):
    keys=list(it);A={k:set() for k in keys}
    for i,k in enumerate(keys):
        for k2 in keys[i+1:]:
            if any(z in it[k2] and it[k][z].distance(it[k2][z])<0.05 for z in it[k]): A[k].add(k2);A[k2].add(k)
    return A
def connected(A,gone):
    P=[k for k in A if k[0]=='P' and k not in gone]
    if len(P)<2: return True
    s=[P[0]];seen={P[0]}
    while s:
        k=s.pop()
        for q in A[k]:
            if q not in gone and q not in seen: seen.add(q);s.append(q)
    return all(p in seen for p in P)
dl=[];dv=[];log=[]
for r in csv.DictReader(open(sys.argv[3])):
    n=r['net'];ends=ast.literal_eval(r['free_end'])
    if not ends or n not in items: continue
    it=items[n];A=adj(it)
    for fx,fy in ends:
        pt=Point(fx,fy+H)
        start=[k for k in it if k[0]!='P' and any(g.distance(pt)<1 for g in it[k].values())]
        gone=set(dl_k for dl_k in A if (dl_k[0]=='L' and dl_k[1] in dl) or (dl_k[0]=='V' and dl_k[1] in dv))
        q=collections.deque(start);seen=set(start);eaten=0;elen=0
        while q:
            k=q.popleft()
            if k[0]=='P': continue
            if not connected(A,gone|{k}): continue
            if min(g.distance(pt) for g in it[k].values())>float(r['length_mil'])+30: continue
            gone.add(k);eaten+=1
            (dl if k[0]=='L' else dv).append(k[1])
            for nb in A[k]:
                if nb not in seen and nb not in gone: seen.add(nb);q.append(nb)
        log.append((n,(fx,fy),eaten))
# one-layer vias
for n,it in items.items():
    A=None
    for k in list(it):
        if k[0]!='V' or k[1] in dv: continue
        c=it[k][0];lay=set()
        for k2,g2 in it.items():
            if k2==k or k2[0]=='V': continue
            for z,g in g2.items():
                if g.distance(c)<0.05: lay.add(z)
        if len(lay)<2:
            if A is None: A=adj(it)
            gone=set(x for x in A if (x[0]=='L' and x[1] in dl) or (x[0]=='V' and x[1] in dv))
            if connected(A,gone|{k}): dv.append(k[1]);log.append((n,'via',k[1],sorted(lay)))
            else: log.append((n,'via NEEDED?',k[1],sorted(lay)))
for l in log: print(l)
print('lines',len(dl),'vias',len(dv))
json.dump({'lines':dl,'vias':dv},open(sys.argv[4],'w'))
