import json
exec(open('common4.py').read())
src=open('pl9.py').read(); exec(src[:src.index('P=lambda')])
pos=json.load(open('plv2.json'))
MV=[]
for d,(x,y,r) in pos.items():
    c=C[d]
    if (round(x),round(y),round(r)%360)!=(c['x'],c['y'],c['r']%360):
        MV.append([c['id'],round(x,1),round(y,1),round(r)%360])
HL=[['c64136646962e90a',11115,-9693]]
A=[4470,-15,'L',9200,-15,9200,-4250,5980,-4250,5980,-6380,4470,-6380,4470,-15]
B1=[8880,-8500,'L',10935,-8500,10935,-9835,8880,-9835,8880,-8500]
B2=[11295,-8500,'L',13560,-8500,13560,-9835,11295,-9835,11295,-8500]
G=[15,-15,'L',4470,-15,4470,-6380,5980,-6380,5980,-4250,9200,-4250,9200,-15,13835,-15,13835,-9835,13560,-9835,13560,-8500,11295,-8500,11295,-9835,10935,-9835,10935,-8500,8880,-8500,8880,-9835,15,-9835,15,-15]
PD=[['GNDA',A,'GNDA_L15',1],['GNDA',B1,'GNDA_XLR1_L15',1],['GNDA',B2,'GNDA_XLR2_L15',1],['GND',G,'GND_L15',3]]
NUC=[6047,-4550,'L',8803,-4550,8803,-9800,6047,-9800,6047,-4550]
js=("(async()=>{const o=[];try{"
"const LS=(await eda.pcb_PrimitiveLine.getAll()).filter(l=>[1,2,15,16].includes(+l.layer));for(let i=0;i<LS.length;i+=500)await eda.pcb_PrimitiveLine.delete(LS.slice(i,i+500).map(l=>l.primitiveId));o.push('lines-'+LS.length);"
"const VS=await eda.pcb_PrimitiveVia.getAll();for(let i=0;i<VS.length;i+=500)await eda.pcb_PrimitiveVia.delete(VS.slice(i,i+500).map(v=>v.primitiveId));o.push('vias-'+VS.length);"
"const PR=await eda.pcb_PrimitivePour.getAll();await eda.pcb_PrimitivePour.delete(PR.map(p=>p.primitiveId));o.push('pours-'+PR.length);"
"const MV=%s;let ok=0;for(const m of MV){try{await eda.pcb_PrimitiveComponent.modify(m[0],{x:m[1],y:m[2],rotation:m[3]});ok++;}catch(e){o.push('mvErr '+m[0])}}o.push('moved '+ok+'/'+MV.length);"
"const HL=%s;let hk=0;for(const h of HL){try{await eda.pcb_PrimitivePad.modify(h[0],{x:h[1],y:h[2]});hk++;}catch(e){o.push('hErr '+e)}}o.push('holes '+hk);"
"const PL=(await eda.pcb_PrimitivePolyline.getAll()).filter(p=>p.layer==3);await eda.pcb_PrimitivePolyline.delete(PL.map(p=>p.primitiveId));await eda.pcb_PrimitivePolyline.create('',3,eda.pcb_MathPolygon.createPolygon(%s),8,false);o.push('silk '+PL.length);"
"const PD=%s;for(const p of PD){try{await eda.pcb_PrimitivePour.create(p[0],15,eda.pcb_MathPolygon.createComplexPolygon(p[1]),'solid',false,p[2],p[3],0.2,false);o.push('pour '+p[2]);}catch(e){o.push('pourErr '+p[2]+' '+e)}}"
"}catch(e){o.push('ERR '+e)}"
"const f=new File([JSON.stringify(o)],'vrb_apply1.json',{type:'application/json'});await eda.sys_FileSystem.saveFile(f,'vrb_apply1.json');})();")%(json.dumps(MV),json.dumps(HL),json.dumps(NUC),json.dumps(PD))
open('apply_v2.js','w').write(js)
print(len(MV),len(js))
for d in ('R26',): print(d,pins_at(d,*pos[d]))
