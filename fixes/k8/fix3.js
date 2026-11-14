(async()=>{const O={log:[]};try{
 const L=[];for(const l of await eda.pcb_PrimitiveLine.getAll()){if(['CH_A2','CH_A4'].includes(l.getState_Net()))L.push(l.getState_PrimitiveId())}
 L.push('b4bca62f7513b166','48fa61934aa7b805');await eda.pcb_PrimitiveLine.delete(L);
 const V=[];for(const v of await eda.pcb_PrimitiveVia.getAll()){if(['CH_A2','CH_A4'].includes(v.getState_Net()))V.push(v.getState_PrimitiveId())}
 if(V.length)await eda.pcb_PrimitiveVia.delete(V);O.log.push('del '+L.length+'/'+V.length);}catch(e){O.log.push('ERR '+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_fix3.json',{type:'application/json'}),'vrb_fix3.json');})();
