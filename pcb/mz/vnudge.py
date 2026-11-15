# vnudge.py dsn in.json out.json  -- fix small clearance misses by moving shared track vertices
# Works on 2-point segment models: a vertex shared only by same-net/same-layer segments (not on a pad
# or via) is moved away from the offending foreign object; all segments sharing it move together.
import sys,os,json,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from geo import load,LAY
from shapely.geometry import Point,Polygon,LineString
from shapely.ops import nearest_points
from shapely.strtree import STRtree
ps,pins,pinnet,_,_=load(sys.argv[1]);R0=json.load(open(sys.argv[2]));R=[]
for r in R0:
    p=r['path']
    if r.get('via'): R.append(r);continue
    for a,b in zip(p,p[1:]):
        if a[0]!=b[0]: R.append({'net':r['net'],'w':12,'path':[list(a),list(b)],'via':True})
        elif (a[1],a[2])!=(b[1],b[2]): R.append({'net':r['net'],'w':r.get('w',12),'path':[list(a),list(b)]})
    if r.get('endvia'): R.append({'net':r['net'],'w':12,'path':[[0,p[-1][1],p[-1][2]],[1,p[-1][1],p[-1][2]]],'via':True})
CL=float(os.environ.get('CL','9.84'));TGT=CL+0.4
def padgeom(sh,x,y):
    k,a=sh
    if k=='circle': return Point(x+(a[1] if len(a)>1 else 0),y+(a[2] if len(a)>2 else 0)).buffer(a[0]/2,16)
    a=a[1:];return Polygon([(x+a[i],y+a[i+1]) for i in range(0,len(a)-1,2)])
def build():
    G=[[],[],[]];O=[[],[],[]]
    for pid,(pst,x,y) in pins.items():
        n=pinnet.get(pid) or 'nc'+pid
        for z,L in enumerate(LAY):
            if L in ps[pst]: G[z].append(padgeom(ps[pst][L],x,y));O[z].append((n,'pad',None))
    for i,r in enumerate(R):
        p=r['path']
        for a,b in zip(p,p[1:]):
            if a[0]!=b[0]:
                for z in range(3): G[z].append(Point(a[1],a[2]).buffer(15.75,16));O[z].append((r['net'],'via',i))
            else: G[a[0]].append(LineString([(a[1],a[2]),(b[1],b[2])]).buffer(r.get('w',12)/2,8));O[a[0]].append((r['net'],'seg',i))
    return G,O
def fixed(net,z,x,y):
    pt=Point(x,y)
    for pid,(pst,px,py) in pins.items():
        if abs(px-x)<80 and abs(py-y)<80 and pinnet.get(pid)==net:
            for L in ps[pst]:
                if padgeom(ps[pst][L],px,py).contains(pt): return True
    for r in R:
        if r['net']==net and r['path'][0][0]!=r['path'][-1][0] and abs(r['path'][0][1]-x)<16 and abs(r['path'][0][2]-y)<16: return True
    return False
moves=0
for it in range(40):
    G,O=build();T=[STRtree(g) for g in G];bad=None
    for z in range(3):
        for i,g in enumerate(G[z]):
            if O[z][i][1]!='seg': continue
            for j in T[z].query(g.buffer(CL)):
                if O[z][j][0]==O[z][i][0]: continue
                d=g.distance(G[z][j])
                if d<CL: bad=(z,i,j,d);break
            if bad: break
        if bad: break
    if not bad: break
    z,i,j,d=bad;k=O[z][i][2];r=R[k];a,b=r['path'][0],r['path'][1]
    q1,q2=nearest_points(LineString([(a[1],a[2]),(b[1],b[2])]),G[z][j])
    # pick endpoint nearer to the conflict that is movable
    cand=sorted([a,b],key=lambda p:math.hypot(p[1]-q1.x,p[2]-q1.y))
    done=False
    for v in cand:
        if fixed(r['net'],z,v[1],v[2]): continue
        dx,dy=q1.x-q2.x,q1.y-q2.y;L=math.hypot(dx,dy) or 1
        if q1.distance(q2)<1e-6:
            c=G[z][j].centroid;dx,dy=q1.x-c.x,q1.y-c.y;L=math.hypot(dx,dy) or 1
        s=(TGT-d)*1.6;ox,oy=v[1],v[2];nx,ny=ox+dx/L*s,oy+dy/L*s
        for rr in R:
            if rr['net']!=r['net']: continue
            for p in rr['path']:
                if abs(p[1]-ox)<0.01 and abs(p[2]-oy)<0.01: p[1],p[2]=round(nx,2),round(ny,2)
        moves+=1;done=True;print('move',r['net'],z,(round(ox),round(oy)),'->',(round(nx,1),round(ny,1)),'d',round(d,2));break
    if not done: print('stuck',r['net'],z,O[z][j][:2],round(d,2),(round(q1.x),round(q1.y)));break
json.dump(R,open(sys.argv[3],'w'));print('moves',moves)
