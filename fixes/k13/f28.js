(async()=>{const O={log:[],err:[]};
try{await eda.pcb_PrimitiveLine.delete(['3987c6cf69caba61','48a448e027f8b3ab']);O.log.push('del ok')}catch(e){O.err.push('del '+e)}
try{await eda.pcb_PrimitiveLine.create('GNDA',1,7735,-7820,8030,-7795,20);O.log.push('add ok')}catch(e){O.err.push('add '+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_f28.json',{type:'application/json'}),'vrb_f28.json');})();
