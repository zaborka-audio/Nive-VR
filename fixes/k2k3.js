(async()=>{const L=[];const W=ms=>new Promise(r=>setTimeout(r,ms));
const pinsOf=async id=>(await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(id)).map(p=>({n:String(p.getState_PinNumber()),x:Math.round(p.getState_X()),y:Math.round(p.getState_Y())}));
try{
 // ---- K3 on P12
 await eda.dmt_EditorControl.openDocument('1176d61d645499a2');await W(4000);
 for(const id of ['abe27414a27e70fc','b38470881a25f4bb','9928e3a2df31dcce','e76852eb301d5d8b']){
  try{const c=await eda.sch_PrimitiveComponent.get(id);const x=c.getState_X(),y=c.getState_Y(),r=c.getState_Rotation();
   await eda.sch_PrimitiveComponent.delete([id]);await eda.sch_PrimitiveComponent.createNetFlag('Power','P12',x,y,r,false);L.push('flag P12 @'+x+','+y);}catch(e){L.push('flagERR '+id+' '+e)}}
 // ---- K2 on P11
 await eda.dmt_EditorControl.openDocument('2d391c71882bed56');await W(4000);
 await eda.sch_PrimitiveWire.delete(['820f011f4f6b0504']);
 await eda.sch_PrimitiveWire.create([1410,1010,1470,1010],'L_MISO');
 await eda.sch_PrimitiveWire.create([1380,1010,1395,1010],'L_MISO_OC');
 let rd=(await eda.lib_Device.search('MFR-25FBF52-22K')||[]).find(x=>String(x.name).toUpperCase()==='MFR-25FBF52-22K')||{libraryUuid:'0819f05c4eef4c71ace90d822a990e87',uuid:'2302d0cfeb6534d7'};
 L.push('Rdev '+rd.name+' '+rd.supplierId);
 const r=await eda.sch_PrimitiveComponent.create(rd,1500,960,undefined,0,false,true,true);const rid=r.getState_PrimitiveId();
 await eda.sch_PrimitiveComponent.modify(rid,{designator:'R194'});
 try{const c=await eda.sch_PrimitiveComponent.get(rid);await eda.sch_PrimitiveComponent.modify(rid,{otherProperty:Object.assign({},c.getState_OtherProperty()||{},{Value:'22k'})})}catch(e){L.push('val '+e)}
 let rp=await pinsOf(rid);L.push('R194 pins '+JSON.stringify(rp));
 const dd={libraryUuid:'0819f05c4eef4c71ace90d822a990e87',uuid:'cbb463a8e2a90dbb'};
 const dc=await eda.sch_PrimitiveComponent.create(dd,1600,930,undefined,270,false,true,true);const did=dc.getState_PrimitiveId();
 await eda.sch_PrimitiveComponent.modify(did,{designator:'D20'});
 let dp=await pinsOf(did);L.push('D20 pins '+JSON.stringify(dp));
 const p1=rp.find(p=>p.n==='1'),p2=rp.find(p=>p.n==='2');const k=dp.find(p=>p.n==='1'),a=dp.find(p=>p.n==='2');
 const left=p1.x<p2.x?p1:p2,right=p1.x<p2.x?p2:p1;
 // left pin -> L_MISO_OC label, right pin -> L_MISO node with diode K
 await eda.sch_PrimitiveWire.create([left.x,left.y,left.x-20,left.y],'L_MISO_OC');
 await eda.sch_PrimitiveWire.create([right.x,right.y,k.x,right.y,k.x,k.y],'L_MISO');
 await eda.sch_PrimitiveWire.create([a.x,a.y,a.x,a.y-15],'');
 await eda.sch_PrimitiveComponent.createNetFlag('Ground','GND',a.x,a.y-15,0,false);
 L.push('ok');
}catch(e){L.push('ERR '+e)}
const f=new File([JSON.stringify(L)],'vrb_k2k3.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_k2k3.json');})();
