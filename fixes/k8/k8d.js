(async()=>{const O={log:[],err:[],bad:[]};const W=ms=>new Promise(r=>setTimeout(r,ms));
const L='0819f05c4eef4c71ace90d822a990e87';
const DEV={"r220k": {"libraryUuid": "0819f05c4eef4c71ace90d822a990e87", "uuid": "f2dae84072034388bc7dae297ff18e7f"}, "r220": {"libraryUuid": "0819f05c4eef4c71ace90d822a990e87", "uuid": "7488ca4653f0408586b0fea0e8efa17a"}, "ptc005": {"libraryUuid": "0819f05c4eef4c71ace90d822a990e87", "uuid": "8af4893e52f04e4081b6b1b882beccac"}, "ptc020": {"libraryUuid": "0819f05c4eef4c71ace90d822a990e87", "uuid": "e0602a2667d44a1eb51b5fa11e78edfd"}, "d4148": {"libraryUuid": "0819f05c4eef4c71ace90d822a990e87", "uuid": "1cd391b03f36496c9af2eda9f38f1fc3"}, "rn223": {"libraryUuid": "0819f05c4eef4c71ace90d822a990e87", "uuid": "fbba9d40679647fc8a88ecb977f2483b"}, "cap104":{"libraryUuid":"0819f05c4eef4c71ace90d822a990e87","uuid":"86d898f340ee4ce9a13303510059829f"},"rn224":{"libraryUuid":"0819f05c4eef4c71ace90d822a990e87","uuid":"ea5250f502484d68bdcf0794854f79be"},"rn223b":{"libraryUuid":"0819f05c4eef4c71ace90d822a990e87","uuid":"de463f006cb44efe865fbf18aa4b2928"},"r22k":{"libraryUuid":"0819f05c4eef4c71ace90d822a990e87","uuid":"b6d64a66b7624278b0bbe1eb88bf479a"},"r1k":{"libraryUuid":"0819f05c4eef4c71ace90d822a990e87","uuid":"bc411c54594f414b848db99ae40d2522"},"rn102": {"libraryUuid": "0819f05c4eef4c71ace90d822a990e87", "uuid": "44d9e2c46d474a08810cf12115a7c24d"}};
const C=eda.sch_PrimitiveComponent,WR=eda.sch_PrimitiveWire;
const pinsOf=async id=>(await C.getAllPinsByPrimitiveId(id)).map(p=>({n:String(p.getState_PinNumber()),nm:String(p.getState_PinName()),x:Math.round(p.getState_X()),y:Math.round(p.getState_Y()),r:Math.round(p.getState_Rotation()||0)}));
const DIR={0:[1,0],180:[-1,0],90:[0,1],270:[0,-1]};
const stub=async(p,net,len)=>{len=len||20;const d=DIR[((p.r%360)+360)%360]||[0,-1];await WR.create([p.x,p.y,p.x+d[0]*len,p.y+d[1]*len],net)};
const T=(p,ms,tg)=>Promise.race([p,new Promise((_,j)=>setTimeout(()=>j(new Error('TIMEOUT '+tg)),ms))]);
const mk=async(dev,x,y,rot,des)=>{const c=await T(C.create(dev,x,y,undefined,rot,false,true,true),120000,'create '+(des||dev.uuid));const id=c.getState_PrimitiveId();if(des)await C.modify(id,{designator:des});return id};
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
const two=async(dev,des,nets,a,sl)=>{const [x,y]=SP[des];const id=await mk(dev,x,y,0,des);if(a)await attr(id,a);const p=await pinsOf(id);O.log.push(des+' '+JSON.stringify(p));
 for(const q of p){let n=nets[q.n];if(n===undefined)n=nets[q.nm];if(n)await stub(q,n,sl||20)}return id};
const ren=async(id,net)=>{const w=await WR.get(id);const l=w.getState_Line();const f=Array.isArray(l[0])?[].concat(...l):l;await WR.delete([id]);await WR.create(f,net)};

Object.assign(SP,{"R201": [80, 960], "R202": [80, 825], "R203": [80, 690], "R204": [80, 555], "R205": [440, 960], "R206": [440, 825], "R207": [390, 1050], "R208": [360, 835], "R209": [390, 700], "R210": [390, 565], "R211": [750, 970], "R212": [750, 835], "R213": [750, 700]});
try{await page('2d391c71882bed56');
 const PU=[['R201','L_A0'],['R202','L_A1'],['R203','L_A2'],['R204','L_A3'],['R205','L_A4'],['R206','L_A5']];
 for(const [d,n] of PU)await two(DEV.r22k,d,{'1':'+3V3','2':n},{m:'YAGEO',p:'MFR-25FBF52-22K1',s:'C1365570',v:'22.1k',n:'22.1k'},10);
 const SR=[['R207','CH_A0'],['R208','CH_A1'],['R209','CH_A2'],['R210','CH_A3'],['R211','CH_A4'],['R212','CH_A5'],['R213','CH_SEL']];
 for(const [d,n] of SR)await two(DEV.r1k,d,{'1':n+'_D','2':n},{m:'YAGEO',p:'MFR-25FBF52-1K',s:'C1364484',v:'1k',n:'1k'},10);
 O.log.push('P11 ok')}catch(e){O.err.push('P11 '+e)}
const f=new File([JSON.stringify(O)],'vrb_k8d.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_k8d.json');})();
