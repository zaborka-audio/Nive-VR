(async()=>{const O={c:{},err:[],log:[]};const RIP=['CH_A0','CH_A1','CH_A2','CH_A3','CH_A4','CH_A5','CH_SEL','PH48','VECAM'];
try{const L=[];for(const l of await eda.pcb_PrimitiveLine.getAll()){if(RIP.includes(l.getState_Net()))L.push(l.getState_PrimitiveId())}
 for(let i=0;i<L.length;i+=500)await eda.pcb_PrimitiveLine.delete(L.slice(i,i+500));O.log.push('lines '+L.length);
 const V=[];for(const v of await eda.pcb_PrimitiveVia.getAll()){if(RIP.includes(v.getState_Net()))V.push(v.getState_PrimitiveId())}
 if(V.length)await eda.pcb_PrimitiveVia.delete(V);O.log.push('vias '+V.length);
 for(const c of await eda.pcb_PrimitiveComponent.getAll()){const d=c.getState_Designator();const id=c.getState_PrimitiveId();let bb=null;try{bb=await eda.pcb_Primitive.getPrimitivesBBox([id])}catch(e){}
 const pins=(await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(id)).map(p=>[p.getState_PadNumber(),Math.round(p.getState_X()),Math.round(p.getState_Y()),p.getState_Net()]);
 O.c[d]={id,x:c.getState_X(),y:c.getState_Y(),r:c.getState_Rotation(),l:c.getState_Layer(),bb,pins}}
 const t=await (await eda.pcb_ManufactureData.getDsnFile()).text();await eda.sys_FileSystem.saveFile(new File([t],'vrb_v13.dsn',{type:'text/plain'}),'vrb_v13.dsn');
}catch(e){O.err.push(''+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_k8pcb.json',{type:'application/json'}),'vrb_k8pcb.json');})();
