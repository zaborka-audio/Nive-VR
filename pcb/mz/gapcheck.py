# gapcheck.py model.json : places where a track end is near (<w) but not exactly on (>0.05) another own-net end/via
import json,sys,math
R=json.load(open(sys.argv[1]))
E=[];V=[]
for i,r in enumerate(R):
    p=r['path']
    if r.get('via') or p[0][0]!=p[-1][0] and len(p)==2: V.append((r['net'],p[0][1],p[0][2],i));continue
    E.append((r['net'],p[0][0],p[0][1],p[0][2],i,r['w']));E.append((r['net'],p[-1][0],p[-1][1],p[-1][2],i,r['w']))
from collections import defaultdict
g=defaultdict(list)
for e in E: g[(e[0],e[1])].append(e)
vg=defaultdict(list)
for v in V: vg[v[0]].append(v)
bad=[]
for e in E:
    n,z,x,y,i,w=e
    exact=any(o[4]!=i and abs(o[2]-x)<0.05 and abs(o[3]-y)<0.05 for o in g[(n,z)]) or any(abs(v[1]-x)<0.05 and abs(v[2]-y)<0.05 for v in vg[n])
    if exact: continue
    near=[o for o in g[(n,z)] if o[4]!=i and 0.05<=math.hypot(o[2]-x,o[3]-y)<w]+[v for v in vg[n] if 0.05<=math.hypot(v[1]-x,v[2]-y)<16]
    if near: bad.append((n,z,round(x,2),round(y,2),[(round(o[-4] if len(o)==6 else o[1],2),round(o[-3] if len(o)==6 else o[2],2)) for o in near][:2]))
print('near-miss ends',len(bad));[print(b) for b in bad[:60]]
