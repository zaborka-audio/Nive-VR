import sys,json,math;sys.path.insert(0,'mz')
from geo import load
from shapely.geometry import Point,LineString
from shapely.ops import nearest_points
from shapely.strtree import STRtree
ps,pins,pinnet,w,v=load(sys.argv[1]);F=json.load(open(sys.argv[2]));NETS=set(sys.argv[4].split(','));NEW=set(json.dumps(x,sort_keys=True) for x in json.load(open(sys.argv[5])))
CL=9.95
def obst(skip_idx):
  geo=[];gw=[];gl=[];gn=[]
  for pid,(pst,x,y) in pins.items():
    sh=ps[pst].get('TopLayer') or list(ps[pst].values())[0]
    if sh[0]=='circle': geo.append(Point(x,y));gw.append(sh[1][0]/2)
    else:
      a=sh[1][1:];from shapely.geometry import Polygon
      geo.append(Polygon([(x+a[i],y+a[i+1]) for i in range(0,len(a)-1,2)]).buffer(0));gw.append(0)
    gl.append(-1);gn.append(pinnet.get(pid,''))
  for k,r in enumerate(F):
    if k==skip_idx: continue
    p=r['path']
    for a,b in zip(p,p[1:]):
      if (a[1],a[2])==(b[1],b[2]) or a[0]!=b[0]: geo.append(Point(a[1],a[2]));gw.append(15.75);gl.append(-1);gn.append(r['net'])
      else: geo.append(LineString([(a[1],a[2]),(b[1],b[2])]));gw.append(r['w']/2);gl.append(a[0]);gn.append(r['net'])
  return geo,gw,gl,gn
tot=0
for k,r in enumerate(F):
  if r['net'] not in NETS or json.dumps(r,sort_keys=True) not in NEW or r.get('via'): continue
  geo,gw,gl,gn=obst(k);T=STRtree(geo)
  for it in range(30):
    p=r['path'];moved=False
    for i in range(len(p)-1):
      a,b=p[i],p[i+1]
      if a[0]!=b[0] or (a[1],a[2])==(b[1],b[2]): continue
      s=LineString([(a[1],a[2]),(b[1],b[2])])
      for j in T.query(s.buffer(40)):
        if gn[j]==r['net'] or (gl[j]!=-1 and gl[j]!=a[0]): continue
        d=s.distance(geo[j])-gw[j]-r['w']/2
        if d<CL:
          q1,q2=nearest_points(s,geo[j]);dx,dy=q1.x-q2.x,q1.y-q2.y;L=math.hypot(dx,dy) or 1
          sh=(CL-d)+0.2
          # don't move endpoints that are pin/pad ends (first/last point)
          for idx in (i,i+1):
            if idx in (0,len(p)-1): continue
            p[idx]=[p[idx][0],p[idx][1]+dx/L*sh,p[idx][2]+dy/L*sh]
          moved=True;tot+=1;break
      if moved: break
    if not moved: break
print('nudges',tot);json.dump(F,open(sys.argv[3],'w'))
