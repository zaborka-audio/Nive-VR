import sys,json,math;sys.path.insert(0,'mz')
from geo import load
from shapely.geometry import Point,LineString,box
from shapely.strtree import STRtree
H=9850
ps,pins,pinnet,wires,vias=load('v10.dsn')
O=json.load(open('../fixes/k6/vrb_k6pcb.json',encoding='utf-8'))['c']
CU=json.load(open('cur10.json'))
RIP={'BP','BN','BL','QS4_1','QS4_2','QS4_3','QS4_4','VR','VIN_F','VIN_RAW'}
MOV=['K25','F5','R195','D23','R196','D24','R197','D25','U29','F1']
FIX={'J11':(2052,-9417,90)}
geo=[];gn=[];gw=[]
for pid,(pst,x,y) in pins.items():
  if not(0<x<13850 and 0<y<9850): continue
  sh=ps[pst].get('TopLayer') or list(ps[pst].values())[0];r=sh[1][0]/2 if sh[0]=='circle' else 40
  geo.append(Point(x,y-H));gn.append(pinnet.get(pid,''));gw.append(r)
for r in CU:
  if r['net'] in RIP: continue
  p=r['path']
  for a,b in zip(p,p[1:]):
    if (a[1],a[2])==(b[1],b[2]): geo.append(Point(a[1],a[2]-H));gn.append(r['net']);gw.append(16)
    elif a[0]==b[0]: geo.append(LineString([(a[1],a[2]-H),(b[1],b[2]-H)]));gn.append(r['net']);gw.append(r['w']/2)
tree=STRtree(geo)
bbs=[];bnames=[]
for d,c in O.items():
  if d in MOV or d in FIX or not c['bb']: continue
  b=c['bb']
  if b['maxY']<-9900: continue
  bbs.append(box(b['minX']+10,b['minY']+10,b['maxX']-10,b['maxY']-10));bnames.append(d)
# targets: pins by net (fixed parts)
tgt={}
for d,c in O.items():
  if d in MOV: continue
  for p in c['pins']:
    if p[3] and p[2]>-9900: tgt.setdefault(p[3],[]).append((p[1],p[2]))
def rot(x,y,r):
  for _ in range(r//90%4): x,y=-y,x
  return x,y
def rel(d):
  c=O[d];b=c['bb'];cx,cy=c['x'],c['y']
  return [(p[0],p[1]-cx,p[2]-cy,p[3]) for p in c['pins']],(b['minX']-cx,b['minY']-cy,b['maxX']-cx,b['maxY']-cy)
def padr(n): return 40
placed={}
def ok(d,x,y,r):
  pp,bb=rel(d)
  xs=[];ys=[]
  for X,Y in [(bb[0],bb[1]),(bb[2],bb[3]),(bb[0],bb[3]),(bb[2],bb[1])]:
    a,b=rot(X,Y,r);xs.append(a);ys.append(b)
  body=box(x+min(xs),y+min(ys),x+max(xs),y+max(ys))
  if body.bounds[0]<60 or body.bounds[2]>13790 or body.bounds[1]<-9790 or body.bounds[3]>-60: return None
  for b in bbs+[v[3] for v in placed.values()]:
    if body.intersects(b): return None
  P=[]
  for n,px,py,net in pp:
    a,b=rot(px,py,r);pt=Point(x+a,y+b)
    for i in tree.query(pt.buffer(100)):
      if gn[i]!=net and geo[i].distance(pt)<padr(n)+gw[i]+14: return None
    for v in placed.values():
      for q in v[4]:
        if q[1]!=net and pt.distance(q[0])<95: return None
    P.append((pt,net))
  return body,P
def score(P):
  s=0
  for pt,net in P:
    T=tgt.get(net,[])+[(q[0].x,q[0].y) for v in placed.values() for q in v[4] if q[1]==net]
    if T: s+=min(math.hypot(pt.x-a,pt.y-b) for a,b in T)
  return s
JOBS=[('R195',(2400,-1900,3500,-300)),('D23',(2400,-1900,3500,-300)),('R196',(2200,-1900,3500,-300)),('D24',(2200,-1900,3500,-300)),('R197',(2400,-2000,3800,-300)),('D25',(2400,-2000,3800,-300)),
 ('K25',(2800,-4000,7600,-500)),('F5',(2800,-4000,7800,-300)),('U29',(800,-5000,2500,-3500)),('F1',(2200,-9800,3400,-8900))]
for d,(x0,y0,x1,y1) in JOBS:
  best=None;st=25
  for x in range(x0,x1+1,st):
    for y in range(y0,y1+1,st):
      for r in (0,90,180,270):
        res=ok(d,x,y,r)
        if not res: continue
        s=score(res[1])
        if not best or s<best[0]: best=(s,x,y,r,res[0],res[1])
  if not best: print(d,'NO PLACE');continue
  placed[d]=best
  tg={}
  for pt,net in best[5]: tg.setdefault(net,[]).append(1)
  print(d,round(best[0]),best[1],best[2],best[3],[(round(p.x),round(p.y),n) for p,n in best[5]])
  best=(best[0],best[1],best[2],best[3],best[4],best[5])
  placed[d]=(best[1],best[2],best[3],best[4],best[5])
json.dump({d:v[:3] for d,v in placed.items()},open('../fixes/k6/placed.json','w'))
