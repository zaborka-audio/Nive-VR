(async()=>{const L=[];const W=ms=>new Promise(r=>setTimeout(r,ms));
const T=(p,ms,tag)=>Promise.race([p,new Promise((_,j)=>setTimeout(()=>j(new Error('TIMEOUT '+tag)),ms))]);
const pinsOf=async id=>(await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(id)).map(p=>({n:String(p.getState_PinNumber()),nm:p.getState_PinName(),x:Math.round(p.getState_X()),y:Math.round(p.getState_Y())}));
const inBox=(x,y)=>x>=1455&&x<=1645&&y>=895&&y<=985;
try{
 await eda.dmt_EditorControl.openDocument('2d391c71882bed56');await W(3500);
 const dc=[];for(const id of await eda.sch_PrimitiveComponent.getAllPrimitiveId()){const c=await eda.sch_PrimitiveComponent.get(id);const d=c.getState_Designator&&c.getState_Designator();const t=c.getState_ComponentType();if(d==='R194'||d==='D20'||(t==='netflag'&&inBox(c.getState_X(),c.getState_Y())))dc.push(id)}
 if(dc.length)await eda.sch_PrimitiveComponent.delete(dc);L.push('delc '+dc.length);
 const dw=[];for(const id of await eda.sch_PrimitiveWire.getAllPrimitiveId()){const w=await eda.sch_PrimitiveWire.get(id);const l=w.getState_Line();const f=Array.isArray(l[0])?[].concat(...l):l;let all=true;for(let i=0;i<f.length;i+=2)if(!inBox(f[i],f[i+1]))all=false;if(all)dw.push(id)}
 if(dw.length)await eda.sch_PrimitiveWire.delete(dw);L.push('delw '+dw.length);
 const rs=await T(eda.lib_Device.search('MFR-25FBF52-22K'),25000,'sR');L.push('rs '+(rs||[]).slice(0,8).map(x=>x.name).join('|'));
 const rd=(rs||[]).find(x=>String(x.name).toUpperCase()==='MFR-25FBF52-22K')||(rs||[]).find(x=>/^MFR-25FBF52-22K/i.test(x.name));
 const ds=await T(eda.lib_Device.search('BAT85,113'),25000,'sD');L.push('ds '+(ds||[]).slice(0,8).map(x=>x.name).join('|'));
 const dd=(ds||[]).find(x=>String(x.name).toUpperCase()==='BAT85,113');
 if(!rd||!dd)throw new Error('device missing r='+(rd&&rd.name)+' d='+(dd&&dd.name));
 L.push('use '+rd.name+' / '+dd.name);
 const r=await T(eda.sch_PrimitiveComponent.create(rd,1500,960,undefined,0,false,true,true),20000,'cR');const rid=r.getState_PrimitiveId();
 await eda.sch_PrimitiveComponent.modify(rid,{designator:'R194'});
 const val=/22K6/i.test(rd.name)?'22.6k':'22k';
 try{const c=await eda.sch_PrimitiveComponent.get(rid);await eda.sch_PrimitiveComponent.modify(rid,{otherProperty:Object.assign({},c.getState_OtherProperty()||{},{Value:val})})}catch(e){L.push('val '+e)}
 const rp=await pinsOf(rid);L.push('R194 '+JSON.stringify(rp));
 const d=await T(eda.sch_PrimitiveComponent.create(dd,1600,930,undefined,270,false,true,true),20000,'cD');const did=d.getState_PrimitiveId();
 await eda.sch_PrimitiveComponent.modify(did,{designator:'D20'});
 const dp=await pinsOf(did);L.push('D20 '+JSON.stringify(dp));
 if(dp.length!==2)throw new Error('diode pins '+dp.length);
 const k=dp.find(p=>/K/i.test(p.nm)||p.n==='1'),a=dp.find(p=>p!==k);
 if(!(k.x===a.x&&k.y>a.y))throw new Error('diode orientation '+JSON.stringify(dp));
 const p1=rp.find(p=>p.n==='1'),p2=rp.find(p=>p.n==='2');const left=p1.x<p2.x?p1:p2,right=p1.x<p2.x?p2:p1;
 await eda.sch_PrimitiveWire.create([left.x,left.y,left.x-20,left.y],'L_MISO_OC');
 await eda.sch_PrimitiveWire.create([right.x,right.y,k.x,right.y,k.x,k.y],'L_MISO');
 await eda.sch_PrimitiveWire.create([a.x,a.y,a.x,a.y-20],'');
 await eda.sch_PrimitiveComponent.createNetFlag('Ground','GND',a.x,a.y-20,0,false);
 L.push('ok');
}catch(e){L.push('ERR '+e)}
const f=new File([JSON.stringify(L)],'vrb_k2d.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_k2d.json');})();
