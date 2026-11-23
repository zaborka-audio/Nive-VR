(async()=>{const O={log:[],err:[]};const W=ms=>new Promise(r=>setTimeout(r,ms));
const C=eda.sch_PrimitiveComponent,WR=eda.sch_PrimitiveWire;
const T=(p,ms,t)=>Promise.race([p,new Promise((_,j)=>setTimeout(()=>j(new Error('TIMEOUT '+t)),ms))]);
const DIR={0:[1,0],180:[-1,0],90:[0,1],270:[0,-1]};
const pinsOf=async id=>(await C.getAllPinsByPrimitiveId(id)).map(p=>({n:String(p.getState_PinNumber()),x:Math.round(p.getState_X()),y:Math.round(p.getState_Y()),r:Math.round(p.getState_Rotation()||0)}));
const re=async(id,line,net)=>{await WR.delete([id]);await WR.create(line,net);O.log.push('wire '+net+' '+line.join(','))};
try{const P=await eda.dmt_Schematic.getAllSchematicPagesInfo();const pg=n=>P.find(p=>(p.name||'').startsWith(n));
 // ---- P7: J1 26a/b/c -> GNDA (F2), J2 C3 -> GNDA (F1)
 await eda.dmt_EditorControl.openDocument(pg('P7').uuid);await W(4500);
 await re('a9678f09c1306ffd',[310,680,230,680],'GNDA');
 await re('c4a002b8303e18f2',[440,680,410,680],'GNDA');
 await re('c5ca7275c7a5b7bb',[440,550,410,550],'GNDA');
 await WR.create([940,545,970,545],'GNDA');O.log.push('J2.C3 GNDA');
 // ---- P12: CH_REF -> GND (logic 0 V), drop JP4, add 120k loads (F3)
 await eda.dmt_EditorControl.openDocument(pg('P12').uuid);await W(4500);
 await re('1038147db85f4896',[290,880,290,800],'GND');
 await re('b6ba586ce1e386a6',[240,690,160,690],'GND');
 await WR.delete(['2bcc0f60c7662282','43fa839be4a20a93']);
 const all=await C.getAll();
 const jp=all.find(c=>c.getState_Designator()==='JP4');if(jp){await C.delete([jp.getState_PrimitiveId()]);O.log.push('JP4 deleted')}
 const fl=all.filter(c=>!c.getState_Designator()&&Math.abs(c.getState_X()-1440)<25&&Math.abs(c.getState_Y()-375)<25);
 for(const f of fl){O.log.push('flag near JP4 '+f.getState_X()+','+f.getState_Y()+' '+JSON.stringify(f.getState_OtherProperty&&f.getState_OtherProperty()))}
 if(fl.length===1){await C.delete([fl[0].getState_PrimitiveId()]);O.log.push('JP4 GND flag deleted')}
 const res=await T(eda.lib_Device.search('MFR-25FBF52-120K'),30000,'search');
 O.cand=(res||[]).slice(0,6).map(x=>[x.name,x.supplierId,x.footprintName,x.manufacturer]);
 const dev=(res||[]).find(x=>/120K/i.test(x.name||'')&&/RES-TH_BD2\.4-L6\.3-P10\.30/.test(x.footprintName||''))||(res||[])[0];
 if(!dev)throw new Error('no 120k device');
 const mk=async(x,y,des,top,bot)=>{const c=await T(C.create(dev,x,y,undefined,270,false,true,true),40000,'create');const id=c.getState_PrimitiveId();await C.modify(id,{designator:des});
  const ps=await pinsOf(id);for(const [i,p] of ps.entries()){const d=DIR[((p.r%360)+360)%360]||[0,1];const net=i===0?top:bot;await WR.create([p.x,p.y,p.x+d[0]*20,p.y+d[1]*20],net);O.log.push(des+'.'+p.n+' '+net+' at '+p.x+','+p.y+' dir '+p.r)}};
 // pin pointing +y gets the first net (CH_DATA); the other pin the second net
 await mk(140,1040,'R214','CH_DATA','GND');
 await mk(200,1040,'R215','CH_DATA','CH_VL');
 const r=(await C.getAll()).filter(c=>/^R21[45]$/.test(c.getState_Designator()||''));
 O.made=r.map(c=>[c.getState_Designator(),c.getState_SupplierId(),(c.getState_OtherProperty()||{}).Value,c.getState_ManufacturerId&&c.getState_ManufacturerId()]);
}catch(e){O.err.push(''+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_k15sch.json',{type:'application/json'}),'vrb_k15sch.json');})();
