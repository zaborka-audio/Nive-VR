(async()=>{const O={};try{await eda.dmt_EditorControl.openDocument('e3a3dbfbefe06669');await new Promise(r=>setTimeout(r,3500));
await eda.sch_PrimitiveText.modify('7aa9e9d696d80ed2',{content:'J1, J2 are mounted on the TOP side of the Main board, front edge (as placed on the PCB); the Bus board (J3, J4) is stacked above.'});
O.t=(await eda.sch_PrimitiveText.get('7aa9e9d696d80ed2')).getState_Content();}catch(e){O.e=''+e}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_p7.json',{type:'application/json'}),'vrb_p7.json');})();
