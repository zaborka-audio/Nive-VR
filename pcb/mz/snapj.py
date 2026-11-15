# snapj.py dsn_noviapins.dsn live_lines.json weak_joints.csv stubdel.json out.json  (EasyEDA coords)
# For sole-path weak joints not already bridged by a short live segment: close the gap exactly.
import sys,os,json,csv,re,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from geo import load,LAY
from shapely.geometry import Point,Polygon,LineString
H=9850;LZ={1:0,2:1,16:2};LN={'L1':1,'L2':2,'L16':16}
ps,pins,pinnet,_,_=load(sys.argv[1]);D=json.load(open(sys.argv[2]));SD=json.load(open(sys.argv[4]))
gone=set(SD['lines'])|set(SD['vias'])
L=[l[:] for l in D['L'] if l[0] not in gone];V=[v for v in D['V'] if v[0] not in gone]
def padgeom(sh,x,y):
    k,a=sh
    if k=='circle': return Point(x+(a[1] if len(a)>1 else 0),y+(a[2] if len(a)>2 else 0)).buffer(a[0]/2,16)
    a=a[1:];return Polygon([(x+a[i],y+a[i+1]) for i in range(0,len(a)-1,2)])
PADS=[(pinnet.get(pid),z,padgeom(ps[pst][Ly],x,y-H)) for pid,(pst,x,y) in pins.items() for z,Ly in enumerate(LAY) if Ly in ps[pst]]
def clear(net,ly,a,b,w):
    g=LineString([a,b]).buffer(w/2,8);z=LZ[ly];m=99
    for n,zz,pg in PADS:
        if zz==z and n!=net: m=min(m,g.distance(pg))
    for l in L:
        if l[1]!=net and l[2]==ly: m=min(m,g.distance(LineString([(l[3],l[4]),(l[5],l[6])]).buffer(l[7]/2,8)))
    for v in V:
        if v[1]!=net: m=min(m,g.distance(Point(v[2],v[3]).buffer(v[5]/2,16)))
    return m
short=[l for l in L if math.hypot(l[5]-l[3],l[6]-l[4])<10.5]
def pt(s): return [tuple(map(float,m)) for m in re.findall(r'\((-?[\d.]+),(-?[\d.]+)\)',s)]
mods={};new=[];rep=[]
for r in csv.DictReader(open(sys.argv[3])):
    if r['only_path(bridge)']!='YES': continue
    x,y=float(r['x']),float(r['y']);n=r['net']
    if any(l[1]==n and min(math.hypot(l[3]-x,l[4]-y),math.hypot(l[5]-x,l[6]-y))<12 for l in short): continue
    A,B=r['item_a'],r['item_b']
    if not A.startswith('wire'): A,B=B,A
    ly=LN[A.split()[1]];(a1,a2)=pt(A)
    la=[l for l in L if l[1]==n and l[2]==ly and {(round(l[3],1),round(l[4],1)),(round(l[5],1),round(l[6],1))}=={a1,a2}]
    if not la: rep.append(('NOTFOUND',n,A));continue
    l=la[0];ea=0 if math.hypot(l[3]-x,l[4]-y)<math.hypot(l[5]-x,l[6]-y) else 1
    P=(l[3],l[4]) if ea==0 else (l[5],l[6])
    if B.startswith('pad'):
        c=pt(B)[0];m=clear(n,ly,P,c,l[7]);new.append([n,ly,P[0],P[1],c[0],c[1],l[7]]);rep.append(('pad-ext',n,P,c,round(m,2)));continue
    def trymove(P,T,commit):
        worst=99;moved=0;ch=[]
        for q in L:
            if q[1]!=n or q[2]!=ly: continue
            qq=q[:]
            for k in (3,5):
                if abs(qq[k]-P[0])<0.05 and abs(qq[k+1]-P[1])<0.05: qq[k],qq[k+1]=T;moved+=1
            if qq!=q: ch.append((q,qq));worst=min(worst,clear(n,ly,(qq[3],qq[4]),(qq[5],qq[6]),qq[7]))
        if commit:
            for q,qq in ch: q[3:7]=qq[3:7];mods[q[0]]=q
        return worst,moved
    cands=[]
    if B.startswith('via'): cands.append((P,pt(B)[0]))
    else:
        (b1,b2)=pt(B);lb=LineString([b1,b2]);pr=lb.interpolate(lb.project(Point(P)))
        cands.append((P,(round(pr.x,2),round(pr.y,2))))
        Q=b1 if math.hypot(b1[0]-P[0],b1[1]-P[1])<math.hypot(b2[0]-P[0],b2[1]-P[1]) else b2
        if math.hypot(Q[0]-P[0],Q[1]-P[1])<12:
            lq=[q for q in L if q[1]==n and q[2]==ly and any(abs(q[k]-Q[0])<0.15 and abs(q[k+1]-Q[1])<0.15 for k in (3,5))]
            for q in lq:
                for k in (3,5):
                    if abs(q[k]-Q[0])<0.15 and abs(q[k+1]-Q[1])<0.15: cands.append(((q[k],q[k+1]),P))
    best=None
    for c in cands:
        w,m=trymove(c[0],c[1],False)
        if m and (best is None or w>best[0]): best=(w,c)
        if m and w>=9.9: break
    if best is None: rep.append(('NOFIX',n,P));continue
    trymove(best[1][0],best[1][1],True);rep.append(('move',n,best[1][0],'->',best[1][1],'clr',round(best[0],2)))
for x in rep: print(x)
json.dump({'mod':list(mods.values()),'new':new},open(sys.argv[5],'w'))
