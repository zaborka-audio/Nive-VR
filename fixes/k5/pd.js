(async()=>{const O={c:{},t:[],v:[],err:[]};
try{
 O.rules=JSON.parse(JSON.stringify(await eda.pcb_Drc.getNetRules())).filter(r=>/N17|VIN24|P17/.test(JSON.stringify(r))).slice(0,10);
 for(const c of await eda.pcb_PrimitiveComponent.getAll()){const d=c.getState_Designator();const x=c.getState_X(),y=c.getState_Y();
  if(!(/^(D21|D22|C4[1-6]|C38|C39|U2[0-2]|D[45]|L[23]|R193|D19|R2[7-9]|R3[0-2]|C40)$/.test(d)||(x>900&&x<3800&&y<-6000&&y>-9500)))continue;
  const id=c.getState_PrimitiveId();let bb=null;try{bb=await eda.pcb_Primitive.getPrimitivesBBox([id])}catch(e){}
  const pins=(await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(id)).map(p=>[p.getState_PadNumber(),Math.round(p.getState_X()),Math.round(p.getState_Y()),p.getState_Net()]);
  O.c[d]={id,x,y,r:c.getState_Rotation(),l:c.getState_Layer(),bb,pins}}
 for(const l of await eda.pcb_PrimitiveLine.getAll()){const n=l.getState_Net();if(!/^(N17A|N17L|GND|CH_P16|\$17N104)$/.test(n))continue;
  O.t.push([l.getState_PrimitiveId(),n,l.getState_Layer(),l.getState_StartX(),l.getState_StartY(),l.getState_EndX(),l.getState_EndY(),l.getState_LineWidth()])}
 for(const v of await eda.pcb_PrimitiveVia.getAll()){const n=v.getState_Net();if(/^(N17A|N17L|GND|CH_P16)$/.test(n))O.v.push([v.getState_PrimitiveId(),n,v.getState_X(),v.getState_Y()])}
}catch(e){O.err.push(''+e)}
const f=new File([JSON.stringify(O)],'vrb_k5pcb.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_k5pcb.json');})();
