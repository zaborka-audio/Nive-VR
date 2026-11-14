(async()=>{const t=await (await eda.pcb_ManufactureData.getDsnFile()).text();await eda.sys_FileSystem.saveFile(new File([t],'vrb_v16.dsn',{type:'text/plain'}),'vrb_v16.dsn');})();
