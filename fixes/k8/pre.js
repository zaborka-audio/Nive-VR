(async()=>{const O={log:[]};try{
for(const c of await eda.pcb_PrimitiveComponent.getAll()){if(c.getState_Designator()==='R212'){await eda.pcb_PrimitiveComponent.modify(c.getState_PrimitiveId(),{x:12500,y:-3800,rotation:90});O.log.push('R212 moved')}}
const L=[];for(const l of await eda.pcb_PrimitiveLine.getAll()){if(['CH_A2','CH_A4'].includes(l.getState_Net()))L.push(l.getState_PrimitiveId())}
if(L.length)await eda.pcb_PrimitiveLine.delete(L);
const V=[];for(const v of await eda.pcb_PrimitiveVia.getAll()){if(['CH_A2','CH_A4'].includes(v.getState_Net()))V.push(v.getState_PrimitiveId())}
if(V.length)await eda.pcb_PrimitiveVia.delete(V);O.log.push('del '+L.length+'/'+V.length);}catch(e){O.log.push('ERR '+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_k8pre.json',{type:'application/json'}),'vrb_k8pre.json');})();
