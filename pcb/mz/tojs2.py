# tojs2.py result.json out_prefix [chunk] -> out_prefix_N.js scripts for EasyEDA
import json,sys
H=9850;LZ=[1,2,16]
d=json.load(open(sys.argv[1]));pre=sys.argv[2];CH=int(sys.argv[3]) if len(sys.argv)>3 else 1500
lines=[];vias=set()
for r in d:
    p=r['path'];n=r['net'];w=r.get('w',12)
    for a,b in zip(p,p[1:]):
        if a[0]!=b[0]: vias.add((n,round(a[1],2),round(a[2]-H,2)))
        elif (a[1],a[2])!=(b[1],b[2]): lines.append([n,LZ[a[0]],round(a[1],2),round(a[2]-H,2),round(b[1],2),round(b[2]-H,2),w])
    if r.get('endvia'): vias.add((n,round(p[-1][1],2),round(p[-1][2]-H,2)))
vias=[list(v) for v in sorted(vias)]
items=[('L',l) for l in lines]+[('V',v) for v in vias]
k=0
for i in range(0,len(items),CH):
    part=items[i:i+CH];L=[x for t,x in part if t=='L'];V=[x for t,x in part if t=='V']
    js=("(async()=>{let a=0,b=0,e=[];const L=%s;const V=%s;for(const l of L){try{await eda.pcb_PrimitiveLine.create(l[0],l[1],l[2],l[3],l[4],l[5],l[6]);a++}catch(x){e.push(''+x)}}"
        "for(const v of V){try{await eda.pcb_PrimitiveVia.create(v[0],v[1],v[2],15.7,31.5);b++}catch(x){e.push(''+x)}}"
        "const f=new File([JSON.stringify({part:%d,lines:a,vias:b,err:e.slice(0,5)})],'vrb_ins%d.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_ins%d.json');})();")%(json.dumps(L,separators=(',',':')),json.dumps(V,separators=(',',':')),k,k,k)
    open('%s_%d.js'%(pre,k),'w').write(js);k+=1
print('lines',len(lines),'vias',len(vias),'scripts',k)
