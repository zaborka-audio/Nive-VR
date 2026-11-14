(async()=>{const O={c:{},err:[]};const W=['J1','J2','U23','U25','U27','U28','U47','K25','HS4','HS5','HS6','HS7','C41','C44','C47','C58','C38','R175','U48','U49','R200','R41','D1','Q1'];
const st=o=>{const r={};for(let k=o;k&&k!==Object.prototype;k=Object.getPrototypeOf(k))for(const m of Object.getOwnPropertyNames(k))if(m.startsWith('getState_')&&!(m.slice(9) in r)){try{const v=o[m]();if(typeof v!=='function'&&!(v&&v.then))r[m.slice(9)]=v}catch(e){}}return r};
try{for(const c of await eda.pcb_PrimitiveComponent.getAll()){const d=c.getState_Designator();if(!W.includes(d))continue;const id=c.getState_PrimitiveId();
 let bb=null;try{bb=await eda.pcb_Primitive.getPrimitivesBBox([id])}catch(e){}
 const pins=(await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(id)).map(p=>st(p));
 O.c[d]={x:c.getState_X(),y:c.getState_Y(),r:c.getState_Rotation(),l:c.getState_Layer(),fp:(c.getState_Footprint()||{}).name,bb,pins}}}catch(e){O.err.push(''+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_b8.json',{type:'application/json'}),'vrb_b8.json');})();
