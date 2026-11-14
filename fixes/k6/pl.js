(async()=>{const O={log:[],err:[]};const P={"R195": [3225, -925, 180], "D23": [3050, -650, 0], "R196": [2800, -1775, 180], "D24": [2850, -1900, 0], "R197": [3675, -1325, 270], "D25": [3675, -1750, 270], "K25": [3175, -2275, 180], "F5": [4900, -1325, 0], "U29": [2450, -4700, 180], "F1": [2875, -9275, 180], "J11": [2052, -9417, 90]};const RIP=["BP", "BN", "BL", "QS4_1", "QS4_2", "QS4_3", "QS4_4", "VR", "VIN_F", "VIN_RAW"];
try{for(const c of await eda.pcb_PrimitiveComponent.getAll()){const d=c.getState_Designator();if(P[d]){const v=P[d];await eda.pcb_PrimitiveComponent.modify(c.getState_PrimitiveId(),{x:v[0],y:v[1],rotation:v[2]});O.log.push(d)}}
 const L=[];for(const l of await eda.pcb_PrimitiveLine.getAll()){if(RIP.includes(l.getState_Net()))L.push(l.getState_PrimitiveId())}
 for(let i=0;i<L.length;i+=500)await eda.pcb_PrimitiveLine.delete(L.slice(i,i+500));O.log.push('lines '+L.length);
 const V=[];for(const v of await eda.pcb_PrimitiveVia.getAll()){if(RIP.includes(v.getState_Net()))V.push(v.getState_PrimitiveId())}
 if(V.length)await eda.pcb_PrimitiveVia.delete(V);O.log.push('vias '+V.length);
 const t=await (await eda.pcb_ManufactureData.getDsnFile()).text();await eda.sys_FileSystem.saveFile(new File([t],'vrb_v11.dsn',{type:'text/plain'}),'vrb_v11.dsn');
}catch(e){O.err.push(''+e)}
await eda.sys_FileSystem.saveFile(new File([JSON.stringify(O)],'vrb_k6pl.json',{type:'application/json'}),'vrb_k6pl.json');})();