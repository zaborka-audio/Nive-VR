(async()=>{const O={log:[],err:[]};
try{await eda.pcb_PrimitiveVia.delete(['a4a9e0dc13fb6e4e','7326e054514b10de']);O.log.push('del ok')}catch(e){O.err.push('del '+e)}
try{await eda.pcb_PrimitiveVia.create('GNDA',8030,-7795,15.7,31.5);O.log.push('via ok')}catch(e){O.err.push('via '+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_f29.json',{type:'application/json'}),'vrb_f29.json');})();
