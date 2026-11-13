import sys,os,json,heapq,math,collections,numpy as np
sys.path.insert(0,'../mz')
from geo import *
ps,pins,pinnet,wires,vias=load(sys.argv[1])
targets=sys.argv[2].split(',')
nets=sorted(set(pinnet.values())|{w[0] for w in wires}|{v[0] for v in vias})
NID={n:i+1 for i,n in enumerate(nets)}
lab=[np.zeros((NY,NX),np.int32) for _ in range(3)]
thr=np.zeros((NY,NX),np.int32)  # through copper (pads/vias) labels
def paint(arr,fn,nid):
    im=Image.new('1',(NX,NY),0);dr=ImageDraw.Draw(im);fn(dr)
    m=np.array(im,bool);arr[m]=nid;return m
VIA=('circle',[31.5])
for pid,(pst,x,y) in pins.items():
    n=pinnet.get(pid);nid=NID.get(n,-1) if n else -1   # -1 = no-net copper
    sh=ps[pst]
    for z,L in enumerate(LAY):
        if L in sh: paint(lab[z],lambda dr:draw_pad(dr,sh[L],x,y),nid)
    paint(thr,lambda dr:draw_pad(dr,sh.get('TopLayer') or list(sh.values())[0],x,y),nid)
for n,x,y in vias:
    for z in range(3): paint(lab[z],lambda dr:draw_pad(dr,VIA,x,y),NID[n])
    paint(thr,lambda dr:draw_pad(dr,VIA,x,y),NID[n])
for n,L,w,pts in wires:
    if L not in LNUM: continue
    z=LNUM[L]
    paint(lab[z],lambda dr:[draw_line(dr,p,q,w) for p,q in zip(pts,pts[1:])],NID[n])
edge=np.ones((NY,NX),bool);e=int(25/G);edge[e:-e,e:-e]=False
KO=os.environ.get('MZKO','')
for k in [k for k in KO.split(';') if k]:
    x0,y0,x1,y1=map(float,k.split(','))
    c0,c1=int((x0-OX)/G),int((x1-OX)/G);r0,r1=int((OY-(y1+H))/G),int((OY-(y0+H))/G)
    for z in range(3): lab[z][max(r0,0):r1,max(c0,0):c1]=-1
print('raster done',flush=True)
import os
MG=float(os.environ.get('MZM','6'));TR=6+9.9+MG; VR=15.75+9.9+MG
out=[]
def comps(nid):
    L3=[];off=0;labs=[]
    for z in range(3):
        l,n=ndimage.label(lab[z]==nid,structure=np.ones((3,3)));l[l>0]+=off;labs.append(l);off+=n
    par=list(range(off+1))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]];a=par[a]
        return a
    tm=thr==nid
    for z in range(1,3):
        a=labs[0][tm];b=labs[z][tm]
        for u,v in set(zip(a.tolist(),b.tolist())):
            if u and v: par[f(u)]=f(v)
    for z in range(3): labs[z]=np.vectorize(f)(labs[z]) if off<5000 else labs[z]
    return labs
def route_net(n):
    nid=NID[n]
    labs=comps(nid)
    ids=sorted({int(v) for z in range(3) for v in np.unique(labs[z]) if v})
    # keep only comps containing a pin of this net
    pinpos=[(x,y) for pid,(pst,x,y) in pins.items() if pinnet.get(pid)==n]
    pc=set()
    for x,y in pinpos:
        cx,cy=int(round((x-OX)/G)),int(round((OY-y)/G))
        if not(0<=cx<NX and 0<=cy<NY): continue
        v=labs[0][cy,cx]
        if v: pc.add(int(v))
    pc=sorted(pc)
    if len(pc)<2: return 'nothing (%d comps)'%len(pc)
    free=[];
    for z in range(3):
        ob=(lab[z]!=0)&(lab[z]!=nid)
        d=ndimage.distance_transform_edt(~ob)*G
        free.append((d>=TR)&~edge)
    obany=np.zeros((NY,NX),bool)
    for z in range(3): obany|=(lab[z]!=0)&(lab[z]!=nid)
    dv=ndimage.distance_transform_edt(~obany)*G
    viaok=(dv>=VR)&~edge
    src=pc[0];res=[]
    merged={src}
    while len(merged)<len(pc):
        S=[labs[z]==src if False else np.isin(labs[z],list(merged)) for z in range(3)]
        T=[np.isin(labs[z],[c for c in pc if c not in merged]) for z in range(3)]
        tany=T[0]|T[1]|T[2]
        hz=ndimage.distance_transform_edt(~tany)
        path=astar(S,T,free,viaok,hz)
        if path is None: return 'FAIL after %d/%d'%(len(merged),len(pc))
        path=smooth(path,free,S,T)
        # which comp reached
        z,y,x=path[-1];c=None
        for zz in range(3):
            if T[zz][y,x]: c=int(labs[zz][y,x]);break
        merged.add(c); res.append(path)
        commit(path,nid)
        labs=comps(nid)  # recompute (new copper joined)
        # remap merged ids to new labels
        def pl(x,y):
            cx,cy=int(round((x-OX)/G)),int(round((OY-y)/G))
            return int(labs[0][cy,cx]) if (0<=cx<NX and 0<=cy<NY) else 0
        newsrc=int(labs[path[0][0]][path[0][1],path[0][2]])
        pc=sorted({pl(x,y) for x,y in pinpos}-{0})
        merged={newsrc}
    return 'ok %d paths'%len(res)
NB=[(0,1,1),(0,-1,1),(1,0,1),(-1,0,1),(1,1,1.4142),(1,-1,1.4142),(-1,1,1.4142),(-1,-1,1.4142)]
VC=40.0
NMAX=int(os.environ.get("MZN","3000000"))
def astar(S,T,free,viaok,hz):
    INF=1e18;dist={};prev={};pq=[]
    for z in range(3):
        ys,xs=np.nonzero(S[z]&(free[z]|S[z]))
        # seed only cells that are free or inside own copper
        for y,x in zip(ys.tolist(),xs.tolist()):
            k=(z,y,x);dist[k]=0;heapq.heappush(pq,(hz[y,x]*1.0,0.0,k))
    n=0
    while pq:
        f,g,k=heapq.heappop(pq)
        if g>dist.get(k,INF): continue
        z,y,x=k;n+=1
        if T[z][y,x] and not S[z][y,x]:
            p=[k]
            while k in prev: k=prev[k];p.append(k)
            return p[::-1]
        if n>NMAX: return None
        for dy,dx,c in NB:
            yy,xx=y+dy,x+dx
            if not(0<=yy<NY and 0<=xx<NX): continue
            if not(free[z][yy,xx] or T[z][yy,xx] or S[z][yy,xx]): continue
            k2=(z,yy,xx);g2=g+c
            if g2<dist.get(k2,INF): dist[k2]=g2;prev[k2]=k;heapq.heappush(pq,(g2+hz[yy,xx],g2,k2))
        if viaok[y,x] or S[0][y,x]&S[1][y,x]:
            for z2 in range(3):
                if z2==z: continue
                k2=(z2,y,x);g2=g+VC
                if (free[z2][y,x] or T[z2][y,x] or S[z2][y,x]) and g2<dist.get(k2,INF): dist[k2]=g2;prev[k2]=k;heapq.heappush(pq,(g2+hz[y,x],g2,k2))
    return None
def los(z,a,b,free,S,T):
    (y0,x0),(y1,x1)=a,b;n=int(max(abs(y1-y0),abs(x1-x0))*2)+1
    for i in range(n+1):
        t=i/n;y=int(round(y0+(y1-y0)*t));x=int(round(x0+(x1-x0)*t))
        if not(free[z][y,x] or S[z][y,x] or T[z][y,x]): return False
    return True
def smooth(path,free,S,T):
    out=[path[0]];i=0
    while i<len(path)-1:
        z=path[i][0];j=i+1
        # extent of same-layer run
        e=i
        while e+1<len(path) and path[e+1][0]==z: e+=1
        if e==i:  # layer change
            out.append(path[i+1]);i+=1;continue
        best=i+1
        for j in range(e,i,-1):
            if los(z,path[i][1:],path[j][1:],free,S,T): best=j;break
        out.append(path[best]);i=best
    return out
def commit(path,nid):
    # draw path copper into raster and record
    segs=[];vs=[]
    for a,b in zip(path,path[1:]):
        if a[0]!=b[0]: vs.append(a)
        else: segs.append((a,b))
    for z,y,x in vs:
        X,Y=OX+x*G,OY-y*G
        for zz in range(3): paint(lab[zz],lambda dr:draw_pad(dr,VIA,X,Y),nid)
        paint(thr,lambda dr:draw_pad(dr,VIA,X,Y),nid)
    for a,b in segs:
        paint(lab[a[0]],lambda dr:draw_line(dr,(OX+a[2]*G,OY-a[1]*G),(OX+b[2]*G,OY-b[1]*G),12),nid)
    out.append({'net':nets[nid-1],'path':[(z,OX+x*G,OY-y*G) for z,y,x in path]})
for n in targets:
    print(n,route_net(n),flush=True)
    json.dump(out,open(sys.argv[3],'w'))
json.dump(out,open(sys.argv[3],'w'))
