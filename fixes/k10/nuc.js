(async()=>{const O={c:{},free:[],err:[]};try{
for(const c of await eda.pcb_PrimitiveComponent.getAll()){const d=c.getState_Designator();if(!/^(CN7|CN8|CN9|CN10)$/.test(d))continue;const id=c.getState_PrimitiveId();
 O.c[d]={x:c.getState_X(),y:c.getState_Y(),r:c.getState_Rotation(),l:c.getState_Layer(),fp:(c.getState_Footprint()||{}).name,bb:await eda.pcb_Primitive.getPrimitivesBBox([id]),
 pins:(await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(id)).map(p=>[p.getState_PadNumber(),p.getState_X(),p.getState_Y(),p.getState_Pad(),p.getState_Hole(),p.getState_Net()])}}
for(const p of await eda.pcb_PrimitivePad.getAll()){try{O.free.push([p.getState_X(),p.getState_Y(),p.getState_Pad(),p.getState_Hole(),p.getState_PadNumber&&p.getState_PadNumber()])}catch(e){}}
}catch(e){O.err.push(''+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_nuc.json',{type:'application/json'}),'vrb_nuc.json');})();
