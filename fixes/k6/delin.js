(async()=>{const O={d:[]};for(const l of await eda.pcb_PrimitiveLine.getAll()){if(l.getState_Net()!=='IN_C')continue;const a=[l.getState_StartX(),l.getState_StartY(),l.getState_EndX(),l.getState_EndY()].map(Math.round);
 const m=(p,q)=>Math.abs(p[0]-q[0])<3&&Math.abs(p[1]-q[1])<3;const s=[a[0],a[1]],e=[a[2],a[3]],A=[2760,-1670],B=[3850,-3745];
 if((m(s,A)&&m(e,B))||(m(s,B)&&m(e,A))){await eda.pcb_PrimitiveLine.delete([l.getState_PrimitiveId()]);O.d.push(a)}}
 await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_k6del.json',{type:'application/json'}),'vrb_k6del.json');})();
