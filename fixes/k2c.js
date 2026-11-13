(async()=>{const L=[];const W=ms=>new Promise(r=>setTimeout(r,ms));
const T=(p,ms,tag)=>Promise.race([p,new Promise((_,j)=>setTimeout(()=>j(new Error('TIMEOUT '+tag)),ms))]);
const pinsOf=async id=>(await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(id)).map(p=>({n:String(p.getState_PinNumber()),x:Math.round(p.getState_X()),y:Math.round(p.getState_Y())}));
try{
 await eda.dmt_EditorControl.openDocument('2d391c71882bed56');await W(3500);
 const ex=[];for(const id of await eda.sch_PrimitiveComponent.getAllPrimitiveId()){const c=await eda.sch_PrimitiveComponent.get(id);const d=c.getState_Designator&&c.getState_Designator();if(d==='R194'||d==='D20')ex.push(d)}L.push('existing '+ex.join(','));
 let rd=null,dd=null;
 try{rd=await T(eda.lib_Device.get('2302d0cfeb6534d7','0819f05c4eef4c71ace90d822a990e87'),15000,'getR');L.push('rd '+(rd&&rd.name))}catch(e){L.push(''+e)}
 try{dd=await T(eda.lib_Device.get('cbb463a8e2a90dbb','0819f05c4eef4c71ace90d822a990e87'),15000,'getD');L.push('dd '+(dd&&dd.name))}catch(e){L.push(''+e)}
 if(!rd){try{const s=await T(eda.lib_Device.search('MFR-25FBF52-22K'),20000,'searchR');rd=(s||[])[0];L.push('rs '+(rd&&rd.name+' '+rd.supplierId))}catch(e){L.push(''+e)}}
 if(!dd){try{const s=await T(eda.lib_Device.search('BAT85'),20000,'searchD');dd=(s||[]).find(x=>/BAT85/.test(x.name));L.push('ds '+(dd&&dd.name))}catch(e){L.push(''+e)}}
 if(rd&&dd&&!ex.length){
  const r=await T(eda.sch_PrimitiveComponent.create(rd,1500,960,undefined,0,false,true,true),20000,'createR');const rid=r.getState_PrimitiveId();
  await eda.sch_PrimitiveComponent.modify(rid,{designator:'R194'});
  try{const c=await eda.sch_PrimitiveComponent.get(rid);await eda.sch_PrimitiveComponent.modify(rid,{otherProperty:Object.assign({},c.getState_OtherProperty()||{},{Value:'22k'})})}catch(e){L.push('val '+e)}
  const rp=await pinsOf(rid);L.push('R194 '+JSON.stringify(rp));
  const dc=await T(eda.sch_PrimitiveComponent.create(dd,1600,930,undefined,270,false,true,true),20000,'createD');const did=dc.getState_PrimitiveId();
  await eda.sch_PrimitiveComponent.modify(did,{designator:'D20'});
  const dp=await pinsOf(did);L.push('D20 '+JSON.stringify(dp));
  const p1=rp.find(p=>p.n==='1'),p2=rp.find(p=>p.n==='2');const k=dp.find(p=>p.n==='1'),a=dp.find(p=>p.n==='2');
  const left=p1.x<p2.x?p1:p2,right=p1.x<p2.x?p2:p1;
  await eda.sch_PrimitiveWire.create([left.x,left.y,left.x-20,left.y],'L_MISO_OC');
  await eda.sch_PrimitiveWire.create([right.x,right.y,k.x,right.y,k.x,k.y],'L_MISO');
  await eda.sch_PrimitiveWire.create([a.x,a.y,a.x,a.y-15],'');
  await eda.sch_PrimitiveComponent.createNetFlag('Ground','GND',a.x,a.y-15,0,false);
  L.push('ok');}
}catch(e){L.push('ERR '+e)}
const f=new File([JSON.stringify(L)],'vrb_k2c.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_k2c.json');})();
