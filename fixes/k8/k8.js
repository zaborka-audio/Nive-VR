(async()=>{const O={log:[],err:[],bad:[]};const W=ms=>new Promise(r=>setTimeout(r,ms));
const L='0819f05c4eef4c71ace90d822a990e87';
const DEV={"r220k": {"libraryUuid": "0819f05c4eef4c71ace90d822a990e87", "uuid": "f2dae84072034388bc7dae297ff18e7f"}, "r220": {"libraryUuid": "0819f05c4eef4c71ace90d822a990e87", "uuid": "7488ca4653f0408586b0fea0e8efa17a"}, "ptc005": {"libraryUuid": "0819f05c4eef4c71ace90d822a990e87", "uuid": "8af4893e52f04e4081b6b1b882beccac"}, "ptc020": {"libraryUuid": "0819f05c4eef4c71ace90d822a990e87", "uuid": "e0602a2667d44a1eb51b5fa11e78edfd"}, "d4148": {"libraryUuid": "0819f05c4eef4c71ace90d822a990e87", "uuid": "1cd391b03f36496c9af2eda9f38f1fc3"}, "rn223": {"libraryUuid": "0819f05c4eef4c71ace90d822a990e87", "uuid": "fbba9d40679647fc8a88ecb977f2483b"}, "rn102": {"libraryUuid": "0819f05c4eef4c71ace90d822a990e87", "uuid": "44d9e2c46d474a08810cf12115a7c24d"}};
const C=eda.sch_PrimitiveComponent,WR=eda.sch_PrimitiveWire;
const pinsOf=async id=>(await C.getAllPinsByPrimitiveId(id)).map(p=>({n:String(p.getState_PinNumber()),nm:String(p.getState_PinName()),x:Math.round(p.getState_X()),y:Math.round(p.getState_Y()),r:Math.round(p.getState_Rotation()||0)}));
const DIR={0:[1,0],180:[-1,0],90:[0,1],270:[0,-1]};
const stub=async(p,net,len)=>{len=len||20;const d=DIR[((p.r%360)+360)%360]||[0,-1];await WR.create([p.x,p.y,p.x+d[0]*len,p.y+d[1]*len],net)};
const T=(p,ms,tg)=>Promise.race([p,new Promise((_,j)=>setTimeout(()=>j(new Error('TIMEOUT '+tg)),ms))]);
const mk=async(dev,x,y,rot,des)=>{const c=await T(C.create(dev,x,y,undefined,rot,false,true,true),40000,'create '+(des||dev.uuid));const id=c.getState_PrimitiveId();if(des)await C.modify(id,{designator:des});return id};
const attr=async(id,a)=>{const c=await C.get(id);const op=Object.assign({},c.getState_OtherProperty()||{},{Value:a.v,'Supplier Part':a.s});const m={supplierId:a.s,otherProperty:op};if(a.m)m.manufacturer=a.m;if(a.p)m.manufacturerId=a.p;if(a.n)m.name=a.n;await C.modify(id,m);
 let r=await C.get(id);if(r.getState_SupplierId()!==a.s||(r.getState_OtherProperty()||{}).Value!==a.v){await C.modify(id,{supplierId:a.s,otherProperty:op});r=await C.get(id)}
 if(r.getState_SupplierId()!==a.s||(r.getState_OtherProperty()||{}).Value!==a.v||(a.p&&r.getState_ManufacturerId()!==a.p))O.bad.push(r.getState_Designator()+' '+r.getState_SupplierId()+' '+(r.getState_OtherProperty()||{}).Value+' '+r.getState_ManufacturerId())};
const role=nm=>/OUT|VO/i.test(nm)?'out':/GND|COM|ADJ/i.test(nm)?'gnd':/IN|VI/i.test(nm)?'in':nm;
const repl=async(oldId,dev,des,byRole,nets,fx,fy)=>{
 const oc=await C.get(oldId);const ox=oc.getState_X(),oy=oc.getState_Y(),orot=oc.getState_Rotation();const op=await pinsOf(oldId);
 const nid=await mk(dev,ox+3000,oy+3000,orot,null);const np=await pinsOf(nid);const nc=await C.get(nid);const nx=nc.getState_X(),ny=nc.getState_Y();
 const key=p=>byRole?role(p.nm):p.n;let match=op.length===np.length;
 for(const p of op){const q=np.find(z=>key(z)===key(p));if(!q||Math.abs((q.x-nx)-(p.x-ox))>0.5||Math.abs((q.y-ny)-(p.y-oy))>0.5)match=false}
 O.log.push(des+' old '+JSON.stringify(op)+' new '+JSON.stringify(np.map(p=>[p.n,p.nm,p.x-nx,p.y-ny]))+' match '+match);
 await C.delete([oldId]);
 if(match){await C.modify(nid,{x:ox,y:oy,designator:des})}
 else{await C.modify(nid,{x:fx,y:fy,designator:des});for(const p of await pinsOf(nid)){const net=nets[key(p)];if(net)await stub(p,net,20)}}
 return nid};
const page=async u=>{await eda.dmt_EditorControl.openDocument(u);await W(3500)};
const txt=async(id,f)=>{try{const t=await eda.sch_PrimitiveText.get(id);await eda.sch_PrimitiveText.modify(id,{content:f(t.getState_Content())})}catch(e){O.err.push('txt '+id+' '+e)}};
const byDes=async d=>{for(const id of await C.getAllPrimitiveId()){const c=await C.get(id);if(c.getState_Designator&&c.getState_Designator()===d)return id}return null};


const SP={"C103": [200, 540], "R198": [320, 440], "C104": [790, 880], "R199": [910, 780], "R200": [1600, 630], "F7": [1650, 550], "D26": [1090, 390], "D27": [990, 380], "D28": [1090, 270], "D29": [990, 260], "RN16": [50, 800], "RN17": [450, 1160], "RN18": [800, 1080], "F6": [630, 770]};
const two=async(dev,des,nets,a)=>{const [x,y]=SP[des];const id=await mk(dev,x,y,0,des);if(a)await attr(id,a);const p=await pinsOf(id);O.log.push(des+' '+JSON.stringify(p));
 for(const q of p){let n=nets[q.n];if(n===undefined)n=nets[q.nm];if(n)await stub(q,n,20)}return id};
const ren=async(id,net)=>{const w=await WR.get(id);const l=w.getState_Line();const f=Array.isArray(l[0])?[].concat(...l):l;await WR.delete([id]);await WR.create(f,net)};
/* P1 */
try{await page('ce0c8e1395a8945d');
 const cdev=(await C.get('71431082e3748b60')).getState_Component();
 await WR.delete(['cf33e5afdf7a8b9e']);await WR.create([200,320,200,400]);await WR.create([180,400,180,370],'ONOFF_U21');
 await WR.delete(['79add96ed7322a2a']);await WR.create([790,660,790,740]);await WR.create([770,740,770,710],'ONOFF_U22');
 const ca={m:'TDK',p:'FG28X7R2A104KNT06',s:'n/a',v:'100n 100V',n:'100n 100V'};
 await two(cdev,'C103',{'1':'VIN24','2':'ONOFF_U21'},ca);await two(DEV.r220k,'R198',{'1':'ONOFF_U21','2':'N17A'},{m:'YAGEO',p:'MFR-25FBF52-220K',s:'C1369876',v:'220k',n:'220k'});
 await two(cdev,'C104',{'1':'VIN24','2':'ONOFF_U22'},ca);await two(DEV.r220k,'R199',{'1':'ONOFF_U22','2':'N17L'},{m:'YAGEO',p:'MFR-25FBF52-470K',s:'n/a',v:'470k',n:'470k'});
 await two(DEV.r220,'R200',{'1':'PH48','2':'PH48_R'},{m:'YAGEO',p:'FMP100JR-52-220R',s:'C1742359',v:'220R 1W',n:'220R 1W'});
 await two(DEV.ptc005,'F7',{'1':'PH48_R','2':'PH48_F'},null);
 await attr('7e00befa54f16bf6',{m:'VISHAY',p:'P6KE30A-E3/73',s:'C1666288',v:'P6KE30A',n:'P6KE30A'});
 O.log.push('P1 ok')}catch(e){O.err.push('P1 '+e)}
/* P4 */
try{await page('85c9a1a6c384a1e5');
 await C.delete(['bd9cd9eff357c73c']);await WR.create([1400,620,1400,600],'PH48_F');
 for(const d of ['08813d8c8c624ed1','248abb9465fce520'])await attr(d,{m:'YAGEO',p:'MFR-25FBF52-22K1',s:'C1365570',v:'22.1k',n:'22.1k'});
 await two(DEV.d4148,'D26',{'A':'MICX_H','C':'+16V'},null);await two(DEV.d4148,'D27',{'A':'-16V','C':'MICX_H'},null);
 await two(DEV.d4148,'D28',{'A':'MICX_C','C':'+16V'},null);await two(DEV.d4148,'D29',{'A':'-16V','C':'MICX_C'},null);
 O.log.push('P4 ok')}catch(e){O.err.push('P4 '+e)}
/* P11 */
try{await page('2d391c71882bed56');
 const R=[['ec14d7bc72028b40','CH_A0_D'],['ede6b4314eedf5af','CH_A1_D'],['3cbe09cb4945eabf','CH_A2_D'],['e13e4b53219f042a','CH_A3_D'],['0748c81c8f0bfa5d','CH_A4_D'],['64ba2bf2670855e5','CH_A5_D'],['0081f22bcdb71100','CH_SEL_D']];
 for(const [id,n] of R)await ren(id,n);
 await two(DEV.rn223,'RN16',{'1':'+3V3','2':'L_A0','3':'L_A1','4':'L_A2','5':'L_A3','6':'L_A4','7':'L_A5'},null);
 await two(DEV.rn102,'RN17',{'1':'CH_A0_D','2':'CH_A0','3':'CH_A1_D','4':'CH_A1','5':'CH_A2_D','6':'CH_A2','7':'CH_A3_D','8':'CH_A3'},null);
 await two(DEV.rn102,'RN18',{'1':'CH_A4_D','2':'CH_A4','3':'CH_A5_D','4':'CH_A5','5':'CH_SEL_D','6':'CH_SEL'},null);
 O.log.push('P11 ok')}catch(e){O.err.push('P11 '+e)}
/* P13 */
try{await page('9ccca2328f5cbe4a');
 await ren('22e46033e1a1d4b8','VECAM_K');
 await two(DEV.ptc020,'F6',{'1':'VECAM_K','2':'VECAM'},null);
 await txt('de7ef4c8c1c689a5',s=>s+'  F6 MF-R020 (0.2 A) in VECAM.');
 O.log.push('P13 ok')}catch(e){O.err.push('P13 '+e)}
const f=new File([JSON.stringify(O)],'vrb_k8.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_k8.json');})();
