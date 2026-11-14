(async()=>{const O={del:[],err:[]};
try{const BOX=[[1350,-4450,1800,-3850],[2380,-9560,2920,-9290]];const inB=(x,y)=>BOX.some(b=>x>=b[0]&&x<=b[2]&&y>=b[1]&&y<=b[3]);
 const pads=[];for(const c of await eda.pcb_PrimitiveComponent.getAll()){for(const p of await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(c.getState_PrimitiveId()))pads.push([p.getState_X(),p.getState_Y()])}
 const vias=(await eda.pcb_PrimitiveVia.getAll()).map(v=>[v.getState_X(),v.getState_Y()]);
 for(let it=0;it<12;it++){
  const L=(await eda.pcb_PrimitiveLine.getAll()).filter(l=>[1,2,15,16].includes(l.getState_Layer())).map(l=>({id:l.getState_PrimitiveId(),n:l.getState_Net(),a:[l.getState_StartX(),l.getState_StartY()],b:[l.getState_EndX(),l.getState_EndY()]}));
  const near=(p,q,r)=>Math.hypot(p[0]-q[0],p[1]-q[1])<=r;
  const onSeg=(p,s)=>{const dx=s.b[0]-s.a[0],dy=s.b[1]-s.a[1],L2=dx*dx+dy*dy;if(!L2)return false;const t=((p[0]-s.a[0])*dx+(p[1]-s.a[1])*dy)/L2;if(t<-0.01||t>1.01)return false;return Math.hypot(s.a[0]+t*dx-p[0],s.a[1]+t*dy-p[1])<6};
  const dead=[];
  for(const s of L){for(const e of [s.a,s.b]){if(!inB(e[0],e[1]))continue;
   if(pads.some(p=>near(p,e,30))||vias.some(v=>near(v,e,8)))continue;
   if(L.some(o=>o!==s&&o.n===s.n&&onSeg(e,o)))continue;
   dead.push(s);break}}
  if(!dead.length)break;
  await eda.pcb_PrimitiveLine.delete(dead.map(s=>s.id));O.del.push(...dead.map(s=>[s.n,Math.round(s.a[0]),Math.round(s.a[1]),Math.round(s.b[0]),Math.round(s.b[1])]))}
}catch(e){O.err.push(''+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_dang.json',{type:'application/json'}),'vrb_dang.json');})();
