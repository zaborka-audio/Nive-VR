(async()=>{const O={log:[],err:[],bad:[]};const W=ms=>new Promise(r=>setTimeout(r,ms));
const L='0819f05c4eef4c71ace90d822a990e87';
const DEV={d4148:{libraryUuid:L,uuid:'1cd391b03f36496c9af2eda9f38f1fc3'},u7812:{libraryUuid:L,uuid:'2fde5c33bdd7477d990047ea223c25d4'},mfr020:{libraryUuid:L,uuid:'e0602a2667d44a1eb51b5fa11e78edfd'},mfr300:{libraryUuid:L,uuid:'21f17f89d5fe42ae88ad672b82630c7d'},dc5a:{libraryUuid:L,uuid:'4d7cb0739a3f454f948049081267bc7c'},g2rl:{libraryUuid:L,uuid:'9e623110b99e41eea444d2aec93935d9'},r10k:{libraryUuid:L,uuid:'9b81c60c26fb4475a9110def3339918f'}};
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

/* P13: B1 base resistors + clamp diodes, B3 K25 + F5 */
try{await page('9ccca2328f5cbe4a');
 try{await WR.delete(['508c695993aae829','37d79fad54f08114','4b4016a6220e963f'])}catch(e){}
 const Q=[['R195','D23',250,200,220,280,'BP','BQ3','XP',true],['R196','D24',615,570,580,650,'BN','BQ4','XN',false],['R197','D25',975,930,940,1010,'BL','BQ5','XL',false]];
 for(const [rd,dd,cx,w0,out,b,nOut,nB,nE,pnp] of Q){
  const rid=await mk(DEV.r10k,cx,480,0,rd);const rp=(await pinsOf(rid)).sort((a,b)=>a.x-b.x);
  await WR.create([w0,480,out,480,rp[0].x,480],nOut);await WR.create([rp[1].x,480,b,480],nB);
  await attr(rid,{m:'YAGEO',p:'MFR-25FBF52-10K',s:'C1519255',v:'10k',n:'10k'});
  const did=await mk(DEV.d4148,cx,400,0,dd);const dp=await pinsOf(did);
  const k=dp.find(p=>/K|CATH/i.test(p.nm))||dp.find(p=>p.n==='1');const a=dp.find(p=>p!==k);
  await WR.create([a.x,a.y,a.x,a.y-20],pnp?nB:nE);await WR.create([k.x,k.y,k.x,k.y-20],pnp?nE:nB);
  O.log.push(rd+' '+JSON.stringify(rp)+' '+dd+' '+JSON.stringify(dp))}
 const kid=await mk(DEV.g2rl,700,890,0,'K25');const kp=await pinsOf(kid);O.log.push('K25 '+JSON.stringify(kp));
 const KN={'1':'VIN24','8':'DRV_PWR','3':'VR','6':'VR','4':'VR_SW','5':'VR_SW'};
 for(const p of kp){if(KN[p.n]){const up=p.y<890;await WR.create([p.x,p.y,p.x,p.y+(up?-20:20)],KN[p.n])}}
 const fid=await mk(DEV.mfr020,720,760,0,'F5');const fp=(await pinsOf(fid)).sort((a,b)=>a.x-b.x);O.log.push('F5 '+JSON.stringify(fp));
 await WR.create([fp[0].x,fp[0].y,fp[0].x-20,fp[0].y],'VR_SW');await WR.create([fp[1].x,fp[1].y,fp[1].x+20,fp[1].y],'CH_VR');
 await txt('de7ef4c8c1c689a5',s=>s+'  K25 (coil parallel to K23/K24) switches VR -> F5 MF-R020 0.2 A -> CH_VR.');
 await txt('7925d2585848e5bb',s=>s+'  Bases via 10k, 1N4148 across B-E (D23-D25).');
 O.log.push('P13 ok')}catch(e){O.err.push('P13 '+e)}

/* P7: J2 A23/C23 -> CH_VR */
try{await page('e3a3dbfbefe06669');
 await WR.delete(['78893a8ee8e2be98','d11c53d478f96103']);
 await WR.create([970,745,940,745],'CH_VR');await WR.create([780,745,860,745],'CH_VR');O.log.push('P7 ok')}catch(e){O.err.push('P7 '+e)}

/* P8: cascade via Q'S */
try{await page('72eee5cb92a38971');
 const M=[['c5b4c5b41f5bfe39',260,'QS4_1'],['d210b107ff3ca44d',560,'QS4_2'],['c634b502ad16caef',860,'QS4_3'],['111f25109b695bec',1160,'QS4_4']];
 await WR.delete(M.map(m=>m[0]));
 const nc=[];for(const id of await C.getAllPrimitiveId()){const c=await C.get(id);if(c.getState_ComponentType()!=='part'&&M.some(m=>Math.abs(c.getState_X()-m[1])<1&&Math.abs(c.getState_Y()-815)<1))nc.push(id)}
 if(nc.length){await C.delete(nc);O.log.push('P8 removed NC '+nc.length)}
 for(const [,x,n] of M)await WR.create([x,815,x+30,815],n);
 await txt('2f500c611d6df5df',s=>s.replace('QS -> next DATA',"Q'S (pin 10, changes on falling CLK) -> next DATA"));
 O.log.push('P8 ok')}catch(e){O.err.push('P8 '+e)}

/* P11: R153 2.2k */
try{await page('2d391c71882bed56');const id=await byDes('R153');await attr(id,{m:'YAGEO',p:'MFR-25FBF52-2K2',s:'C3454390',v:'2.2k',n:'2.2k'});O.log.push('P11 ok')}catch(e){O.err.push('P11 '+e)}

/* P5: R13/R16 2.49k */
try{await page('394d7b79a97ceaf5');for(const d of ['R13','R16']){const id=await byDes(d);await attr(id,{m:'YAGEO',p:'MFP-25BRD52-2K49',s:'n/a',v:'2.49k 0.1%',n:'2.49k 0.1%'})}O.log.push('P5 ok')}catch(e){O.err.push('P5 '+e)}

/* P1: D1 after Q1 (VIN24), P6KE27A; F1 MF-R300; J11 5 A jack */
try{await page('ce0c8e1395a8945d');
 await WR.delete(['1ee1eb322447cfee','d2fe8cb2ce85726e']);await C.delete(['5fb7b078364c0059']);
 await WR.create([220,1020,310,1020],'VIN_F');
 await C.modify('7e00befa54f16bf6',{x:560,y:920});const dp=await pinsOf('7e00befa54f16bf6');O.log.push('D1 '+JSON.stringify(dp));
 for(const p of dp){await stub(p,/K/i.test(p.nm)?'VIN24':'GND',20)}
 await attr('7e00befa54f16bf6',{m:'Taiwan Semiconductor',p:'P6KE27AHR0G',s:'C2446445',v:'P6KE27A',n:'P6KE27A'});
 await repl('c79d9d047130f947',DEV.mfr300,'F1',false,{'1':'VIN_RAW','2':'VIN_F'},600,1000);
 await repl('2f735fd772e57d3f',DEV.dc5a,'J11',false,{'1':'VIN_RAW','2':'GND','3':'GND'},-200,1000);
 await txt('4b6a57170b7a4fe2',s=>s+'  (PSU 24 V >= 4 A; F1 3 A hold; TVS D1 after Q1)');
 O.log.push('P1 ok')}catch(e){O.err.push('P1 '+e)}

/* P2: U29 -> L7812CV TO-220 */
try{await page('2deb12c50258dde1');
 await repl('77ad79fc4762c618',DEV.u7812,'U29',true,{'in':'P17','out':'P12','gnd':'GND'},560,740);
 await txt('5a522bd97cd551ec',s=>s.replace('78L12','L7812CV (TO-220)'));
 O.log.push('P2 ok')}catch(e){O.err.push('P2 '+e)}

const f=new File([JSON.stringify(O)],'vrb_k6b.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_k6b.json');})();
