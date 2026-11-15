# gcmp.py a.json b.json : geometric differences (segments of a not covered by b and vice versa), vias
import json,sys,collections
from shapely.geometry import LineString
from shapely.ops import unary_union
def split(M):
    S=[];V=set()
    for r in M:
        p=r['path']
        for a,b in zip(p,p[1:]):
            if a[0]!=b[0]: V.add((r['net'],round(a[1]),round(a[2])))
            elif (a[1],a[2])!=(b[1],b[2]): S.append((r['net'],a[0],(a[1],a[2]),(b[1],b[2]),r.get('w',12)))
        if r.get('endvia'): V.add((r['net'],round(p[-1][1]),round(p[-1][2])))
    return S,V
def cover(S):
    d={}
    for n,z,a,b,w in S: d.setdefault((n,z),[]).append(LineString([a,b]))
    return {k:unary_union(v).buffer(1.0) for k,v in d.items()}
A,AV=split(json.load(open(sys.argv[1])));B,BV=split(json.load(open(sys.argv[2])))
ca,cb=cover(A),cover(B)
mA=[s for s in A if not ((s[0],s[1]) in cb and cb[(s[0],s[1])].contains(LineString([s[2],s[3]])))]
mB=[s for s in B if not ((s[0],s[1]) in ca and ca[(s[0],s[1])].contains(LineString([s[2],s[3]])))]
near=lambda v,L:any(q[0]==v[0] and abs(q[1]-v[1])<=2 and abs(q[2]-v[2])<=2 for q in L)
vA=[v for v in AV if not near(v,BV)];vB=[v for v in BV if not near(v,AV)]
print('segs',len(A),len(B),'| only in A',len(mA),collections.Counter(s[0] for s in mA).most_common(10))
print('only in B',len(mB),collections.Counter(s[0] for s in mB).most_common(10))
print('vias',len(AV),len(BV),'only A',len(vA),vA[:6],'only B',len(vB),vB[:6])
