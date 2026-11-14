(async()=>{const O={log:[],err:[]};const W=ms=>new Promise(r=>setTimeout(r,ms));const C=eda.sch_PrimitiveComponent,WR=eda.sch_PrimitiveWire;
try{await eda.dmt_EditorControl.openDocument('ce0c8e1395a8945d');await W(3500);
 let jid=null;for(const id of await C.getAllPrimitiveId()){const c=await C.get(id);if(c.getState_Designator&&c.getState_Designator()==='J11')jid=id}
 const dw=[];for(const id of await WR.getAllPrimitiveId()){const w=await WR.get(id);const l=w.getState_Line();const f=Array.isArray(l[0])?[].concat(...l):l;let a=true;for(let i=0;i<f.length;i+=2)if(!(f[i]>-300&&f[i]<-100&&f[i+1]>950&&f[i+1]<1050))a=false;if(a)dw.push(id)}
 if(dw.length)await WR.delete(dw);O.log.push('delw '+dw.length);
 await C.modify(jid,{x:100,y:1010});
 O.log.push(JSON.stringify((await C.getAllPinsByPrimitiveId(jid)).map(p=>[p.getState_PinNumber(),p.getState_X(),p.getState_Y()])));
}catch(e){O.err.push(''+e)}
const f=new File([JSON.stringify(O)],'vrb_k6j.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_k6j.json');})();
