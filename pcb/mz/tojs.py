import json,sys,itertools
d=json.load(open(sys.argv[1]));H=9850;LZ=[1,2,16]
lines=[];vias=[]
for r in d:
    p=r['path'];n=r['net']
    runs=[list(g) for k,g in itertools.groupby(p,key=lambda q:q[0])]
    for i,run in enumerate(runs):
        if i>0: vias.append([n,run[0][1],run[0][2]-H])
        pts=[(q[1],q[2]) for q in run]
        # compress collinear
        s=[pts[0]]
        for j in range(1,len(pts)-1):
            a,b,c=s[-1],pts[j],pts[j+1]
            d1=(b[0]-a[0],b[1]-a[1]);d2=(c[0]-b[0],c[1]-b[1])
            if d1[0]*d2[1]-d1[1]*d2[0]!=0: s.append(b)
        if len(pts)>1: s.append(pts[-1])
        for a,b in zip(s,s[1:]): lines.append([n,LZ[run[0][0]],a[0],a[1]-H,b[0],b[1]-H])
print(len(lines),len(vias))
js="(async()=>{try{const L=%s;const V=%s;let a=0,b=0;for(const l of L){await eda.pcb_PrimitiveLine.create(l[0],l[1],l[2],l[3],l[4],l[5],12);a++;}for(const v of V){await eda.pcb_PrimitiveVia.create(v[0],v[1],v[2],15.7,31.5);b++;}eda.sys_Dialog.showInputDialog('t','','R','text','lines '+a+' vias '+b);}catch(E){eda.sys_Dialog.showInputDialog('t','','R','text','FAIL '+E);}})();"%(json.dumps(lines),json.dumps(vias))
open(sys.argv[2],'w').write(js)
json.dump({'lines':lines,'vias':vias},open(sys.argv[1]+'.ee.json','w'))
