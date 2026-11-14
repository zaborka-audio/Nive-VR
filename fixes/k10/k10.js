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


const V={P1:{R198:{m:'YAGEO',p:'MFR-25FBF52-47K',s:'n/a',v:'47k',n:'47k'},R199:{m:'YAGEO',p:'MFR-25FBF52-100K',s:'C1364475',v:'100k',n:'100k'},R200:{m:'YAGEO',p:'FMP100JR-52-100R',s:'C1740213',v:'100R 1W',n:'100R 1W'},R41:{m:'YAGEO',p:'MFR-25FBF52-40K2',s:'n/a',v:'40.2k 1%',n:'40.2k 1%'}},
 P13:{R195:{m:'YAGEO',p:'MFR-25FBF52-47K',s:'n/a',v:'47k',n:'47k'},R196:{m:'YAGEO',p:'MFR-25FBF52-47K',s:'n/a',v:'47k',n:'47k'},R197:{m:'YAGEO',p:'MFR-25FBF52-47K',s:'n/a',v:'47k',n:'47k'}}};
const PG={P1:'ce0c8e1395a8945d',P13:'9ccca2328f5cbe4a'};
for(const k of ['P1','P13']){try{await page(PG[k]);for(const d in V[k]){const id=await byDes(d);if(!id){O.err.push('no '+d);continue}await attr(id,V[k][d]);O.log.push(d)}}catch(e){O.err.push(k+' '+e)}}
const f=new File([JSON.stringify(O)],'vrb_k10.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_k10.json');})();
