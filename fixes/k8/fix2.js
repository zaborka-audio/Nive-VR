(async()=>{const O={log:[],err:[]};try{
 await eda.pcb_PrimitiveLine.delete(['2881b0c5677eaace','57c000f473675fa2','c4772d52f7154d80','3f01eb5943738802']);O.log.push('del4');
 let k=0;for(const l of await eda.pcb_PrimitiveLine.getAll()){if(l.getState_Net()==='VECAM'&&Math.abs(l.getState_LineWidth()-16)<0.5){await eda.pcb_PrimitiveLine.modify(l.getState_PrimitiveId(),{lineWidth:12});k++}}O.log.push('vecam w '+k);
}catch(e){O.err.push(''+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_fix2.json',{type:'application/json'}),'vrb_fix2.json');})();
