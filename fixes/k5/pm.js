(async()=>{const O={log:[],err:[]};
try{
 for(const c of await eda.pcb_PrimitiveComponent.getAll()){const d=c.getState_Designator();const id=c.getState_PrimitiveId();
  if(d==='D21'){await eda.pcb_PrimitiveComponent.modify(id,{x:1925,y:-7475,rotation:180});}
  if(d==='D22'){await eda.pcb_PrimitiveComponent.modify(id,{x:2925,y:-6700,rotation:0});}
  if(d==='D21'||d==='D22'){const p=(await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(id)).map(p=>[p.getState_PadNumber(),Math.round(p.getState_X()),Math.round(p.getState_Y()),p.getState_Net()]);O.log.push(d+' '+JSON.stringify(p))}}
 await eda.pcb_PrimitiveLine.delete(['065bf47c493240ac','0eec8228489ae823','06b19219704cf36a','1cea8e37cc21574a','4dfb3c2070e2f215']);O.log.push('del5');
 const t=await (await eda.pcb_ManufactureData.getDsnFile()).text();O.dsnlen=t.length;
 const f2=new File([t],'vrb_v9.dsn',{type:'text/plain'});await eda.sys_FileSystem.saveFile(f2,'vrb_v9.dsn');
}catch(e){O.err.push(''+e)}
const f=new File([JSON.stringify(O)],'vrb_k5pm.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_k5pm.json');})();
