(async()=>{const O={err:[]};const W=ms=>new Promise(r=>setTimeout(r,ms));
try{const pages=await eda.dmt_Schematic.getAllSchematicPagesInfo();const flat=[];const walk=x=>{if(Array.isArray(x))x.forEach(walk);else if(x&&typeof x==='object'){if(x.uuid&&x.name)flat.push({uuid:x.uuid,name:x.name});for(const k in x)if(typeof x[k]==='object')walk(x[k])}};walk(pages);
for(const pg of flat.filter(p=>/^P(1|2|5|7|8|11|13) /.test(p.name))){await eda.dmt_EditorControl.openDocument(pg.uuid);await W(3500);
 const P={uuid:pg.uuid,comps:[],wires:[],texts:[]};
 for(const id of await eda.sch_PrimitiveComponent.getAllPrimitiveId()){try{const c=await eda.sch_PrimitiveComponent.get(id);
  const e={id,d:c.getState_Designator(),t:c.getState_ComponentType(),x:c.getState_X(),y:c.getState_Y(),r:c.getState_Rotation(),net:c.getState_Net&&c.getState_Net(),nm:c.getState_Name(),dev:(c.getState_Component()||{}).name,mpn:c.getState_ManufacturerId()};
  if(e.t==='part'){e.pins=(await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(id)).map(p=>[String(p.getState_PinNumber()),p.getState_PinName(),Math.round(p.getState_X()),Math.round(p.getState_Y())])}
  P.comps.push(e)}catch(er){O.err.push(''+er)}}
 for(const id of await eda.sch_PrimitiveWire.getAllPrimitiveId()){const w=await eda.sch_PrimitiveWire.get(id);P.wires.push([id,w.getState_Line(),w.getState_Net()])}
 try{for(const t of await eda.sch_PrimitiveText.getAll()){P.texts.push([t.getState_PrimitiveId(),t.getState_X(),t.getState_Y(),t.getState_Content()])}}catch(er){O.err.push('txt '+er)}
 O[pg.name]=P}
}catch(e){O.err.push('ERR '+e)}
const f=new File([JSON.stringify(O)],'vrb_k6dump.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_k6dump.json');})();
