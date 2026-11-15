# widen.py dsn model.json out.json NET x0,y0,x1,y1 [widths]
# Greedy widening of one net's tracks inside a box (DSN coords). Each straight segment is cut
# into pieces <= STEP mil; every piece gets the largest width that keeps CL to foreign copper.
# Only layers 0/1 (outer) are widened unless INNER=1.
import sys,os,json,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('MZG','25')
from geo import load,LAY
from shapely.geometry import Point,Polygon,LineString
from shapely.strtree import STRtree
dsn,src,dst,NET,box=sys.argv[1:6]
WS=[float(v) for v in (sys.argv[6] if len(sys.argv)>6 else '100,80,64,50,40').split(',')]
X0,Y0,X1,Y1=[float(v) for v in box.split(',')]
CL=float(os.environ.get('CL','9.84'))+0.4
STEP=float(os.environ.get('STEP','80'))
INNER=os.environ.get('INNER')=='1'
ps,pins,pinnet,wires,vias=load(dsn);R=json.load(open(src))
def padgeom(sh,x,y):
    k,a=sh
    if k=='circle': return Point(x+(a[1] if len(a)>1 else 0),y+(a[2] if len(a)>2 else 0)).buffer(a[0]/2,16)
    a=a[1:];return Polygon([(x+a[i],y+a[i+1]) for i in range(0,len(a)-1,2)])
geo=[[],[],[]]
for pid,(pst,x,y) in pins.items():
    n=pinnet.get(pid) or ('nc'+pid)
    if n==NET: continue
    for z,L in enumerate(LAY):
        if L in ps[pst]: geo[z].append(padgeom(ps[pst][L],x,y))
for r in R:
    if r['net']==NET: continue
    p=r['path'];w=r.get('w',12)
    for a,b in zip(p,p[1:]):
        if a[0]!=b[0]:
            for z in range(3): geo[z].append(Point(a[1],a[2]).buffer(15.75,16))
        else: geo[a[0]].append(LineString([(a[1],a[2]),(b[1],b[2])]).buffer(w/2,8))
    if r.get('endvia'):
        for z in range(3): geo[z].append(Point(p[-1][1],p[-1][2]).buffer(15.75,16))
# board edge: keep 20 mil
edge=Polygon([(0,0),(13850,0),(13850,9850),(0,9850)]).exterior.buffer(20+CL)
T=[STRtree(g) for g in geo]
def ok(z,ls,w):
    g=ls.buffer(w/2,8)
    if g.intersects(edge): return False
    for j in T[z].query(g.buffer(CL)):
        if g.distance(geo[z][j])<CL: return False
    return True
inb=lambda p:X0<=p[1]<=X1 and Y0<=p[2]<=Y1
out=[];stat={}
for r in R:
    if r['net']!=NET or r.get('via'):
        out.append(r);continue
    p=r['path'];w0=r.get('w',12)
    # keep layer-change structure: emit pieces as separate 2-point items; vias at layer changes
    for a,b in zip(p,p[1:]):
        if a[0]!=b[0]:
            out.append({'net':NET,'w':12,'path':[list(a),list(b)]});continue
        if not (inb(a) and inb(b)) or (a[0]==2 and not INNER):
            out.append({'net':NET,'w':w0,'path':[list(a),list(b)]});continue
        L=math.hypot(b[1]-a[1],b[2]-a[2]);n=max(1,math.ceil(L/STEP))
        pts=[(a[1]+(b[1]-a[1])*k/n,a[2]+(b[2]-a[2])*k/n) for k in range(n+1)]
        pieces=[]
        for k in range(n):
            ls=LineString([pts[k],pts[k+1]]) if L>0 else Point(pts[k])
            w=w0
            for c in WS:
                if c<=w0: break
                if ok(a[0],ls,c): w=c;break
            pieces.append([k,w])
        # merge equal-width neighbours
        k=0
        while k<n:
            j=k
            while j+1<n and pieces[j+1][1]==pieces[k][1]: j+=1
            w=pieces[k][1];stat[w]=stat.get(w,0)+1
            out.append({'net':NET,'w':w,'path':[[a[0],round(pts[k][0],2),round(pts[k][1],2)],[a[0],round(pts[j+1][0],2),round(pts[j+1][1],2)]]})
            k=j+1
# stitching: at every layer change inside the box add up to 4 extra vias around it
nst=0
if os.environ.get('STITCH','1')=='1':
    vg=[]
    for r in R:
        if r['net']!=NET: continue
        p=r['path']
        for a,b in zip(p,p[1:]):
            if a[0]!=b[0] and inb(a): vg.append((a[1],a[2]))
        if r.get('via') and inb(p[0]): vg.append((p[0][1],p[0][2]))
    from shapely.ops import unary_union
    own={z:unary_union([LineString([(o['path'][0][1],o['path'][0][2]),(o['path'][1][1],o['path'][1][2])]).buffer(o['w']/2,8)
         for o in out if o['net']==NET and not o.get('via') and len(o['path'])==2 and o['path'][0][0]==o['path'][1][0]==z]) for z in (0,1,2)}
    for (x,y) in vg:
        zs=[z for z in (0,1,2) if own[z].contains(Point(x,y))]
        if len(zs)<2: continue
        for dx,dy in ((22,22),(-22,22),(22,-22),(-22,-22)):
            c=Point(x+dx,y+dy).buffer(15.75,16)
            if all(own[z].contains(c) for z in zs) and all(not any(c.distance(geo[z][j])<CL for j in T[z].query(c.buffer(CL))) for z in range(3)):
                out.append({'net':NET,'w':12,'path':[[0,x+dx,y+dy],[1,x+dx,y+dy]],'via':True});nst+=1
print('stitch vias',nst)
json.dump(out,open(dst,'w'))
print('pieces by width',dict(sorted(stat.items())))
