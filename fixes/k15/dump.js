(async()=>{const O={err:[],pages:{}};const W=ms=>new Promise(r=>setTimeout(r,ms));
const C=eda.sch_PrimitiveComponent,WR=eda.sch_PrimitiveWire;
try{const P=await eda.dmt_Schematic.getAllSchematicPagesInfo();
for(const pg of P){const nm=pg.name||'';if(!/^P7|^P12/.test(nm))continue;
 await eda.dmt_EditorControl.openDocument(pg.uuid);await W(4500);const R={comps:[],wires:[]};
 for(const c of await C.getAll()){const d=c.getState_Designator();const e={d,id:c.getState_PrimitiveId(),x:c.getState_X(),y:c.getState_Y(),r:c.getState_Rotation(),v:(c.getState_OtherProperty()||{}).Value,s:c.getState_SupplierId()};
  if(/^(J1|J2|R16\d|R17\d|JP4|U45|U46|R1\d\d)$/.test(d||'')){e.pins=(await C.getAllPinsByPrimitiveId(e.id)).map(p=>[String(p.getState_PinNumber()),String(p.getState_PinName()),p.getState_X(),p.getState_Y(),p.getState_Rotation()])}
  R.comps.push(e)}
 for(const w of await WR.getAll()){R.wires.push([w.getState_PrimitiveId(),w.getState_Net(),w.getState_Line()])}
 O.pages[nm]=R}
}catch(e){O.err.push(''+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_k15dump.json',{type:'application/json'}),'vrb_k15dump.json');})();
