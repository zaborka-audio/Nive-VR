(async()=>{const O={log:[],err:[],bad:[]};const W=ms=>new Promise(r=>setTimeout(r,ms));
const C=eda.sch_PrimitiveComponent,WR=eda.sch_PrimitiveWire,TX=eda.sch_PrimitiveText;
const T=(p,ms,t)=>Promise.race([p,new Promise((_,j)=>setTimeout(()=>j(new Error('TIMEOUT '+t)),ms))]);
const DIR={0:[1,0],180:[-1,0],90:[0,1],270:[0,-1]};
const L='0819f05c4eef4c71ace90d822a990e87';
const BAT={libraryUuid:L,uuid:'cbb463a8e2a90dbb'};
const re=async(id,line,net)=>{await WR.delete([id]);if(net)await WR.create(line,net);O.log.push('wire '+id+' -> '+net)};
const pick=async(q,rx,fp)=>{const r=await T(eda.lib_Device.search(q),30000,q);const d=(r||[]).find(x=>rx.test(x.name||'')&&(!fp||fp.test(x.footprintName||'')));O.log.push('search '+q+' -> '+(d?d.name+' '+d.supplierId:'NONE'));return d};
try{const P=await eda.dmt_Schematic.getAllSchematicPagesInfo();const pg=n=>P.find(p=>(p.name||'').startsWith(n));
 const R100=await pick('100K 1/4W',/^RN1\/4W100KFT/,/RES-TH_BD2\.4-L6\.3-P10\.30/);
 const R33=await pick('33K 1/4W',/^RN1\/4W33KFT/,/RES-TH_BD2\.4-L6\.3-P10\.30/);
 const C100=await pick('FG28X7R1H104KNT06',/FG28X7R1H104KNT06/,null);
 if(!R100||!R33||!C100)throw new Error('device missing');
 // ---- P9: free the analogue/overload lines from the 22k drivers
 await eda.dmt_EditorControl.openDocument(pg('P9 ').uuid);await W(4000);
 await WR.delete(['96c0eb4312e32820','9eb58b35a9fb949a','fcf210cf697dddc7']);O.log.push('P9 RN1.6 RN2.4 RN2.8 freed');
 // ---- P10: U36.5 / U36.14 to VL, new F4/F5 parts
 await eda.dmt_EditorControl.openDocument(pg('P10').uuid);await W(4000);
 await re('db7e2e647a6d061b',[165,835,85,835],'VL');
 await re('f1438e02eca38119',[265,855,235,855],'VL');
 const parts=[
  [R100,'R216','100k',{1:'G_EXPAND_CNTL',2:'EXP_ADC'}],[R33,'R217','33k',{1:'EXP_ADC',2:'+3V3'}],[C100,'C105','100n',{1:'EXP_ADC',2:'GND'}],
  [BAT,'D30','BAT85',{1:'+3V3',2:'EXP_ADC'}],[BAT,'D31','BAT85',{1:'EXP_ADC',2:'GND'}],
  [R100,'R218','100k',{1:'G_LC_CONTROL',2:'LC_ADC'}],[R33,'R219','33k',{1:'LC_ADC',2:'+3V3'}],[C100,'C106','100n',{1:'LC_ADC',2:'GND'}],
  [BAT,'D32','BAT85',{1:'+3V3',2:'LC_ADC'}],[BAT,'D33','BAT85',{1:'LC_ADC',2:'GND'}],
  [BAT,'D34','BAT85',{1:'GND',2:'G_OVERLOAD'}]];
 let x=100;
 for(const [dev,des,val,nets] of parts){
  try{const c=await T(C.create(dev,x,700,undefined,270,false,true,true),40000,'create '+des);const id=c.getState_PrimitiveId();await C.modify(id,{designator:des});
   const cc=await C.get(id);const op=Object.assign({},cc.getState_OtherProperty()||{},{Value:val});await C.modify(id,{otherProperty:op});
   for(const p of await C.getAllPinsByPrimitiveId(id)){const n=String(p.getState_PinNumber());const px=Math.round(p.getState_X()),py=Math.round(p.getState_Y());const r=((Math.round(p.getState_Rotation()||0)%360)+360)%360;const d=DIR[r]||[0,1];
    const net=nets[n];if(!net){O.bad.push(des+' pin '+n);continue}await WR.create([px,py,px+d[0]*20,py+d[1]*20],net);O.log.push(des+'.'+n+' '+net+' @'+px+','+py+' r'+r)}
  }catch(e){O.err.push(des+' '+e)}
  x+=50}
 await TX.create(60,645,'F4: EXPAND/LC CONTROL are analogue -> ADC PF7/PF8 (2.48 V + 0.248 x Vline)');
 await TX.create(60,630,'F5: D34 clamps OVERLOAD idle +14 V to 0 V. U36.5/14 unused (VL)');
 // ---- P13: K25 fed from CH_VL (F7)
 await eda.dmt_EditorControl.openDocument(pg('P13').uuid);await W(4000);
 await re('66d89d76ddb2cc43',[720,830,720,850],'CH_VL');
 await re('37fecac4d788a653',[720,950,720,930],'CH_VL');
 // ---- P3: Nucleo ADC pins
 await eda.dmt_EditorControl.openDocument(pg('P3 ').uuid);await W(4000);
 await WR.create([230,430,260,430],'EXP_ADC');await WR.create([230,440,260,440],'LC_ADC');O.log.push('CN9.26 EXP_ADC, CN9.24 LC_ADC');
 // ---- P2: U28 branch not fitted
 await eda.dmt_EditorControl.openDocument(pg('P2 ').uuid);await W(4000);
 for(const c of await C.getAll()){const d=c.getState_Designator();if(!/^(U28|R39|R40|C58|HS7)$/.test(d||''))continue;const id=c.getState_PrimitiveId();
  try{await C.modify(id,{addIntoBom:false})}catch(e){O.err.push('bom '+d+' '+e)}
  const r=await C.get(id);O.log.push(d+' addIntoBom='+(r.getState_AddIntoBom?r.getState_AddIntoBom():'?'))}
 for(const t of await TX.getAll()){if(/^U28\s+LM337/.test(t.getState_Content()||'')){await TX.modify(t.getState_PrimitiveId(),{content:'U28 LM337 -> VR: NOT FITTED (with R39, R40, C58, HS7). F7: CH_VR now comes from CH_VL via K25'});O.log.push('P2 note')}}
}catch(e){O.err.push(''+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_k16sch.json',{type:'application/json'}),'vrb_k16sch.json');})();
