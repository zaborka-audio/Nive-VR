(async()=>{const O={err:[],items:[]};
try{const r=await eda.pcb_Drc.check(false,false,true);
 const walk=(x)=>{if(Array.isArray(x))x.forEach(walk);else if(x&&typeof x==='object'){if(x.errorType){O.items.push(JSON.parse(JSON.stringify(x)))}for(const k in x)if(typeof x[k]==='object'&&k!=='errorType')walk(x[k])}};walk(r);
 O.n=O.items.length;
 const t=await (await eda.pcb_ManufactureData.getDsnFile()).text();O.dsn=t;
}catch(e){O.err.push(''+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_drc29.json',{type:'application/json'}),'vrb_drc29.json');})();
