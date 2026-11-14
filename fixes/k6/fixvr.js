(async()=>{const O={err:[]};try{await eda.pcb_PrimitiveLine.delete(['d5dd4e9fd0eb11cb']);
await eda.pcb_PrimitiveLine.create('VR',1,4055,-3030,4300,-2978,24);await eda.pcb_PrimitiveLine.create('VR',1,4300,-2978,4595,-2855,24);
const r=await eda.pcb_Drc.check(false,false,true);O.items=[];const walk=x=>{if(Array.isArray(x))x.forEach(walk);else if(x&&typeof x==='object'){if(x.errorType)O.items.push(JSON.parse(JSON.stringify(x)));for(const k in x)if(typeof x[k]==='object')walk(x[k])}};walk(r);O.n=O.items.length}catch(e){O.err.push(''+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_drc11.json',{type:'application/json'}),'vrb_drc11.json');})();
