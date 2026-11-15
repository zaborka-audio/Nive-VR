(async()=>{const O={err:[],pl:[],ln:[]};
const st=o=>{const r={};for(const k of Object.getOwnPropertyNames(Object.getPrototypeOf(o))){if(k.startsWith('getState_')){try{r[k.slice(9)]=o[k]()}catch(e){}}}return r};
try{for(const p of await eda.pcb_PrimitivePolyline.getAll()){const s=st(p);if(s.Layer===3||s.Layer===13)O.pl.push(JSON.parse(JSON.stringify(s)))}}catch(e){O.err.push('pl '+e)}
try{for(const l of await eda.pcb_PrimitiveLine.getAll()){const s=st(l);if(s.Layer===3)O.ln.push([s.StartX,s.StartY,s.EndX,s.EndY,s.LineWidth])}}catch(e){O.err.push('ln '+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_silk.json',{type:'application/json'}),'vrb_silk.json');})();
