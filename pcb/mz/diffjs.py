# diffjs.py old.json new.json prefix
# Segment-level diff of two copper models (DSN coords). Writes:
#   prefix_del.js  : deletes lines/vias present in old but not in new (matched by net/layer/ends, tol 2 mil)
#   prefix_add.json: model with only the new segments/vias (feed to tojs2.py)
import json,sys
H=9850;LZ=[1,2,16]
old,new,pre=sys.argv[1:4]
def segs(M):
    S={};V={}
    for r in M:
        p=r['path'];n=r['net'];w=r.get('w',12)
        for a,b in zip(p,p[1:]):
            if a[0]!=b[0]: V[(n,round(a[1]),round(a[2]))]=(a[1],a[2])
            elif (a[1],a[2])!=(b[1],b[2]):
                e=sorted([(round(a[1]),round(a[2])),(round(b[1]),round(b[2]))])
                S[(n,a[0],e[0],e[1],round(w))]=(a,b,w)
        if r.get('endvia'): V[(n,round(p[-1][1]),round(p[-1][2]))]=(p[-1][1],p[-1][2])
    return S,V
So,Vo=segs(json.load(open(old)));Sn,Vn=segs(json.load(open(new)))
dS=[k for k in So if k not in Sn];aS=[k for k in Sn if k not in So]
dV=[k for k in Vo if k not in Vn];aV=[k for k in Vn if k not in Vo]
D=[[k[0],LZ[k[1]],So[k][0][1],So[k][0][2]-H,So[k][1][1],So[k][1][2]-H,So[k][2]] for k in dS]
DV=[[k[0],Vo[k][0],Vo[k][1]-H] for k in dV]
js=("(async()=>{const O={log:[],err:[]};const S=%s;const V=%s;"
"try{const m=(a,b)=>Math.abs(a[0]-b[0])<2&&Math.abs(a[1]-b[1])<2;const L=[];"
"for(const l of await eda.pcb_PrimitiveLine.getAll()){const n=l.getState_Net(),ly=l.getState_Layer();const s=[l.getState_StartX(),l.getState_StartY()],e=[l.getState_EndX(),l.getState_EndY()];"
"if(S.some(g=>g[0]===n&&g[1]===ly&&((m(s,[g[2],g[3]])&&m(e,[g[4],g[5]]))||(m(e,[g[2],g[3]])&&m(s,[g[4],g[5]])))))L.push(l.getState_PrimitiveId())}"
"for(let i=0;i<L.length;i+=500)await eda.pcb_PrimitiveLine.delete(L.slice(i,i+500));O.log.push('lines '+L.length+' of '+S.length);"
"const DV=[];for(const v of await eda.pcb_PrimitiveVia.getAll()){if(V.some(q=>q[0]===v.getState_Net()&&m([q[1],q[2]],[v.getState_X(),v.getState_Y()])))DV.push(v.getState_PrimitiveId())}"
"if(DV.length)await eda.pcb_PrimitiveVia.delete(DV);O.log.push('vias '+DV.length+' of '+V.length);"
"}catch(e){O.err.push(''+e)}"
"await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_del.json',{type:'application/json'}),'vrb_del.json');})();")%(json.dumps(D,separators=(',',':')),json.dumps(DV,separators=(',',':')))
open(pre+'_del.js','w').write(js)
A=[{'net':k[0],'w':Sn[k][2],'path':[list(Sn[k][0]),list(Sn[k][1])]} for k in aS]+[{'net':k[0],'w':12,'path':[[0,Vn[k][0],Vn[k][1]],[1,Vn[k][0],Vn[k][1]]],'via':True} for k in aV]
json.dump(A,open(pre+'_add.json','w'))
print('delete lines',len(D),'vias',len(DV),'| add lines',len(aS),'vias',len(aV))
