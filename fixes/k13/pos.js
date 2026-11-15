(async()=>{const O={err:[],L:{},V:{}};
const L=['0ded32d470a251ab','026719757d065057','11eaad9e7662fb76','3a7ec95be6ee3b64'];const V=['bd9ca1229f53b4ea','cb356e4d83e14244'];
for(const id of L){try{const l=await eda.pcb_PrimitiveLine.get(id);O.L[id]=[l.getState_Net(),l.getState_Layer(),l.getState_StartX(),l.getState_StartY(),l.getState_EndX(),l.getState_EndY(),l.getState_LineWidth?l.getState_LineWidth():null]}catch(e){O.err.push(id+' '+e)}}
for(const id of V){try{const v=await eda.pcb_PrimitiveVia.get(id);O.V[id]=[v.getState_Net(),v.getState_X(),v.getState_Y()]}catch(e){O.err.push(id+' '+e)}}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_pos.json',{type:'application/json'}),'vrb_pos.json');})();
