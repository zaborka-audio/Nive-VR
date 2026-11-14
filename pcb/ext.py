import sys,json,math;sys.path.insert(0,'mz')
from geo import load
ps,pins,pinnet,w,v=load('v16.dsn')
F=json.load(open('k8k.json'));base=json.load(open('cur16.json'))
S=set(json.dumps(x,sort_keys=True) for x in base)
P={}
for pid,(pst,x,y) in pins.items():
  n=pinnet.get(pid)
  if n: P.setdefault(n,[]).append((x,y))
segs={}
for r in F:
  p=r['path']
  for a,b in zip(p,p[1:]):
    if a[0]==b[0] and (a[1],a[2])!=(b[1],b[2]): segs.setdefault(r['net'],[]).append((a,b))
add=0
for r in F:
  if json.dumps(r,sort_keys=True) in S or r.get('via'): continue
  for idx in (0,-1):
    e=r['path'][idx];L,x,y=e
    near=min(P.get(r['net'],[]),key=lambda q:math.hypot(q[0]-x,q[1]-y),default=None)
    if near and math.hypot(near[0]-x,near[1]-y)<=0.5: continue
    if near and math.hypot(near[0]-x,near[1]-y)<70:
      ext=[L,near[0],near[1]];(r['path'].insert(0,ext) if idx==0 else r['path'].append(ext));add+=1;continue
    best=None
    for a,b in segs.get(r['net'],[]):
      if a[0]!=L or e in (a,b): continue
      ax,ay,bx,by=a[1],a[2],b[1],b[2];dx,dy=bx-ax,by-ay;t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy)))
      px,py=ax+t*dx,ay+t*dy;d=math.hypot(px-x,py-y)
      if 0.5<d<25 and (not best or d<best[0]): best=(d,px,py)
    if best:
      ext=[L,best[1],best[2]];(r['path'].insert(0,ext) if idx==0 else r['path'].append(ext));add+=1
print('ext',add);json.dump(F,open('final21.json','w'))
n=[x for x in F if json.dumps(x,sort_keys=True) not in S];json.dump(n,open('new21.json','w'));print('new',len(n))
