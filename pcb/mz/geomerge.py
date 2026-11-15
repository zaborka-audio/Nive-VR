# geomerge.py base.json routed.json out.json
# Geometric merge: keep base representation for unchanged copper.
#  removed = base segments not covered by routed copper of same net/layer
#  added   = routed segments not covered by base copper of same net/layer
#  vias compared with 1.5 mil tolerance
# Removals are only allowed for nets not in KEEP (power nets / GND), and vias of KEEP nets are kept.
import json,sys,os
from shapely.geometry import LineString,Point
from shapely.ops import unary_union
base,rt,dst=sys.argv[1:4]
KEEP=set(os.environ.get('KEEP','GND GNDA VIN24 VL G_SLB').split())
B=json.load(open(base));R=json.load(open(rt))
def split(M):
    S=[];V=[]
    for r in M:
        p=r['path']
        for a,b in zip(p,p[1:]):
            if a[0]!=b[0]: V.append((r['net'],a[1],a[2]))
            elif (a[1],a[2])!=(b[1],b[2]): S.append((r['net'],a[0],(a[1],a[2]),(b[1],b[2]),r.get('w',12)))
        if r.get('endvia'): V.append((r['net'],p[-1][1],p[-1][2]))
    return S,V
bS,bV=split(B);rS,rV=split(R)
def cover(S):
    d={}
    for n,z,a,b,w in S: d.setdefault((n,z),[]).append(LineString([a,b]))
    return {k:unary_union(v).buffer(0.8) for k,v in d.items()}
bc=cover(bS);rc=cover(rS)
inside=lambda c,n,z,a,b:(n,z) in c and c[(n,z)].contains(LineString([a,b]))
rem=[s for s in bS if s[0] not in KEEP and not inside(rc,s[0],s[1],s[2],s[3])]
ONLY=set(open(os.environ['ONLY']).read().split()) if os.environ.get('ONLY') else None
add=[s for s in rS if not inside(bc,s[0],s[1],s[2],s[3]) and (ONLY is None or s[0] in ONLY)]
near=lambda v,L:any(q[0]==v[0] and abs(q[1]-v[1])<1.5 and abs(q[2]-v[2])<1.5 for q in L)
remV=[v for v in bV if v[0] not in KEEP and not near(v,rV)]
addV=[v for v in rV if not near(v,bV) and (ONLY is None or v[0] in ONLY)]
remset=set((s[0],s[1],s[2],s[3]) for s in rem);remVs=set(remV)
out=[]
for s in bS:
    if (s[0],s[1],s[2],s[3]) in remset: continue
    out.append({'net':s[0],'w':s[4],'path':[[s[1],*s[2]],[s[1],*s[3]]]})
for s in add: out.append({'net':s[0],'w':s[4],'path':[[s[1],*s[2]],[s[1],*s[3]]]})
seen=set()
for v in bV+addV:
    if v in remVs: continue
    k=(v[0],round(v[1],1),round(v[2],1))
    if k in seen: continue
    seen.add(k);out.append({'net':v[0],'w':12,'path':[[0,v[1],v[2]],[1,v[1],v[2]]],'via':True})
json.dump(out,open(dst,'w'))
import collections
print('removed segs',len(rem),'vias',len(remV),'| added segs',len(add),'vias',len(addV))
print('removed by net',collections.Counter(s[0] for s in rem).most_common(12))
print('added by net',collections.Counter(s[0] for s in add).most_common(12))
