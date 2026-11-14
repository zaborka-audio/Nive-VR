(async()=>{const O={err:[]};const W=ms=>new Promise(r=>setTimeout(r,ms));
const T=(p,ms,tag)=>Promise.race([p,new Promise((_,j)=>setTimeout(()=>j(new Error('TIMEOUT '+tag)),ms))]);
const st=o=>{const r={};for(const k of Object.getOwnPropertyNames(Object.getPrototypeOf(o))){if(k.startsWith('getState_')){try{const v=o[k]();r[k.slice(9)]=v}catch(e){}}}return r};
try{
 const pages=await eda.dmt_Schematic.getAllSchematicPagesInfo();O.pages=JSON.parse(JSON.stringify(pages));
 const flat=[];const walk=x=>{if(Array.isArray(x))x.forEach(walk);else if(x&&typeof x==='object'){if(x.uuid&&x.name)flat.push({uuid:x.uuid,name:x.name});for(const k in x)if(typeof x[k]==='object')walk(x[k])}};walk(pages);
 O.flat=flat;
 for(const pg of flat.filter(p=>/^P1 |^P13 |power input|channel power/i.test(p.name))){
  await eda.dmt_EditorControl.openDocument(pg.uuid);await W(4000);
  const P={comps:[],wires:[]};
  for(const id of await eda.sch_PrimitiveComponent.getAllPrimitiveId()){const c=await eda.sch_PrimitiveComponent.get(id);const s=st(c);
   const e={id,d:s.Designator,t:s.ComponentType,x:s.X,y:s.Y,r:s.Rotation,net:s.Net};
   if(['C41','C42','C43','C44','C45','C46','C38','R193','D19','R175','R25'].includes(s.Designator)){e.all=s;e.pins=(await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(id)).map(p=>({n:p.getState_PinNumber(),x:p.getState_X(),y:p.getState_Y(),r:p.getState_Rotation()}))}
   P.comps.push(e)}
  for(const id of await eda.sch_PrimitiveWire.getAllPrimitiveId()){const w=await eda.sch_PrimitiveWire.get(id);P.wires.push({id,l:w.getState_Line(),n:w.getState_Net()})}
  O[pg.name]=P}
 for(const q of ['1N5819','FG28X7R2A104','MFR-25FBF52-4K7']){try{const s=await T(eda.lib_Device.search(q),25000,q);O['s_'+q]=(s||[]).slice(0,6).map(x=>JSON.parse(JSON.stringify(x)))}catch(e){O.err.push(''+e)}}
}catch(e){O.err.push('ERR '+e)}
const f=new File([JSON.stringify(O)],'vrb_k5dump.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_k5dump.json');})();
