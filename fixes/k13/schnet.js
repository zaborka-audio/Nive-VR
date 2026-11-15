(async()=>{const O={err:[],net:{},pages:null};const w=t=>new Promise(r=>setTimeout(r,t));
try{const P=await eda.dmt_Schematic.getAllSchematicPagesInfo();O.pages=P.map(p=>p.name||p.uuid);
const pg=P[0];await eda.dmt_EditorControl.openDocument(pg.uuid||pg.pageUuid);await w(5000);
for(const t of [undefined,'JLCEDA','EasyEDA','Allegro','PADS','Protel2','KiCad']){try{const f=await eda.sch_ManufactureData.getNetlistFile('vrb_net',t);O.net[String(t)]=f?await f.text():null}catch(e){O.err.push('sch '+t+' '+e)}}
}catch(e){O.err.push(''+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_schnet.json',{type:'application/json'}),'vrb_schnet.json');})();
