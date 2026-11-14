(async()=>{const O={r:[],err:[]};const W=ms=>new Promise(r=>setTimeout(r,ms));const B=["R168", "R170", "R175", "R176", "R177", "R178", "R179", "R181", "R182", "R184", "R185", "R190", "R192", "R46", "R41", "R45", "R51", "C43", "C46", "R33", "R34", "R35", "R36", "R37", "R39", "R3", "R4", "R5", "R6", "R11", "R12", "R13", "R14", "R15", "R16"];
try{const pages=await eda.dmt_Schematic.getAllSchematicPagesInfo();const flat=[];const walk=x=>{if(Array.isArray(x))x.forEach(walk);else if(x&&typeof x==='object'){if(x.uuid&&x.name)flat.push({uuid:x.uuid,name:x.name});for(const k in x)if(typeof x[k]==='object')walk(x[k])}};walk(pages);
for(const pg of flat.filter(p=>/^P\d+ /.test(p.name))){await eda.dmt_EditorControl.openDocument(pg.uuid);await W(3000);
 for(const id of await eda.sch_PrimitiveComponent.getAllPrimitiveId()){try{const c=await eda.sch_PrimitiveComponent.get(id);const d=c.getState_Designator&&c.getState_Designator();if(!B.includes(d))continue;
  await eda.sch_PrimitiveComponent.modify(id,{supplierId:'n/a'});let r=await eda.sch_PrimitiveComponent.get(id);let s=r.getState_SupplierId();
  if(s&&s.endsWith('.1')){await eda.sch_PrimitiveComponent.modify(id,{supplierId:' '});r=await eda.sch_PrimitiveComponent.get(id);s=r.getState_SupplierId()}
  O.r.push(d+'='+JSON.stringify(s))}catch(e){O.err.push(''+e)}}}
}catch(e){O.err.push('ERR '+e)}
const f=new File([JSON.stringify(O)],'vrb_k5sup.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_k5sup.json');})();