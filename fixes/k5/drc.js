(async()=>{const O={err:[],items:[]};
try{const r=await eda.pcb_Drc.check(false,false,true);
 const walk=(x,p)=>{if(Array.isArray(x))x.forEach(y=>walk(y,p));else if(x&&typeof x==='object'){if(x.errorType){O.items.push(JSON.parse(JSON.stringify(x)))}for(const k in x)if(typeof x[k]==='object'&&k!=='errorType')walk(x[k],p)}};walk(r);
 O.n=O.items.length;
}catch(e){O.err.push(''+e)}
const f=new File([JSON.stringify(O)],'vrb_drc9.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_drc9.json');})();
