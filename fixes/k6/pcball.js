(async()=>{const O={c:{},err:[]};
try{for(const c of await eda.pcb_PrimitiveComponent.getAll()){const d=c.getState_Designator();const id=c.getState_PrimitiveId();let bb=null;try{bb=await eda.pcb_Primitive.getPrimitivesBBox([id])}catch(e){}
 const pins=(await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(id)).map(p=>[p.getState_PadNumber(),Math.round(p.getState_X()),Math.round(p.getState_Y()),p.getState_Net()]);
 O.c[d]={id,x:c.getState_X(),y:c.getState_Y(),r:c.getState_Rotation(),l:c.getState_Layer(),bb,pins}}
 const t=await (await eda.pcb_ManufactureData.getDsnFile()).text();const f2=new File([t],'vrb_v10.dsn',{type:'text/plain'});await eda.sys_FileSystem.saveFile(f2,'vrb_v10.dsn');
}catch(e){O.err.push(''+e)}
const f=new File([JSON.stringify(O)],'vrb_k6pcb.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_k6pcb.json');})();
