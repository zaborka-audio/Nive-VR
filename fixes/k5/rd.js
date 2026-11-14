(async()=>{const O={};const W=ms=>new Promise(r=>setTimeout(r,ms));
try{const pages=await eda.dmt_Schematic.getAllSchematicPagesInfo();const flat=[];const walk=x=>{if(Array.isArray(x))x.forEach(walk);else if(x&&typeof x==='object'){if(x.uuid&&x.name)flat.push({uuid:x.uuid,name:x.name});for(const k in x)if(typeof x[k]==='object')walk(x[k])}};walk(pages);
for(const pg of flat.filter(p=>/^P\d+ /.test(p.name))){await eda.dmt_EditorControl.openDocument(pg.uuid);await W(3000);
 for(const id of await eda.sch_PrimitiveComponent.getAllPrimitiveId()){try{const c=await eda.sch_PrimitiveComponent.get(id);const d=c.getState_Designator&&c.getState_Designator();if(!d)continue;
  O[d]=[c.getState_Name(),c.getState_Manufacturer(),c.getState_ManufacturerId(),c.getState_Supplier(),c.getState_SupplierId(),(c.getState_OtherProperty()||{}).Value,(c.getState_OtherProperty()||{})['Supplier Part']]}catch(e){}}}
}catch(e){O.ERR=''+e}
const f=new File([JSON.stringify(O)],'vrb_k5rd.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_k5rd.json');})();
