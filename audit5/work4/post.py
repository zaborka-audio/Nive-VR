import sys; sys.path.insert(0,'work4')
from geom import *
pins,pst,nets,wires,vias=load_pcb()
pinmap=pickle.load(open('work4/pinmap.pkl','rb'))
D=pickle.load(open('work4/conn.pkl','rb')); items=D['items'];roots=D['roots'];touch=D['touch'];thru=D['thru']
pairs=pickle.load(open('work4/pairs.pkl','rb'))
out=pickle.load(open('work4/clear.pkl','rb'))
print('CLEARANCE <9.84:'); [print('  %.2f L%s %s/%s @(%.0f,%.0f) | %s | %s'%(o[0],o[1],o[2],o[3],o[6],o[7],o[4],o[5])) for o in out]
def desc(i):
    it=items[i]
    if it['kind']=='wire':
        w=wires[it['ref']]; return 'wire %s L%s w%.0f (%.2f,%.2f)-(%.2f,%.2f)'%(it['net'],it['layer'],w['w'],w['pts'][0][0],w['pts'][0][1]-YOFF,w['pts'][1][0],w['pts'][1][1]-YOFF)
    if it['kind']=='via': v_=vias[it['ref']]; return 'via %s (%.2f,%.2f) d%s'%(it['net'],v_['x'],v_['y']-YOFF,v_.get('d'))
    if it['kind']=='pad':
        p=pins[it['ref']]; d,c=pinmap.get(it['ref'],('HOLE',[])); return 'pad %s.%s (%.1f,%.1f)'%(d,'|'.join(c)[:12],p['x'],p['y']-YOFF)
    return it['kind']+str(it['ref'])
print('GEN_H joints <9.6:',[('%.2f'%n,desc(a),desc(b)) for (a,b),n in pairs.items() if items[a]['net']=='GEN_H' and n<9.6])
print('TAILS (free end, dead length > 4 mil):')
for i,it in enumerate(items):
    if it['kind']!='wire': continue
    w=wires[it['ref']]; r=w['w']/2
    for k,e in enumerate(w['pts']):
        P=Point(e); cap=P.buffer(r*0.6)
        if any(items[o]['geom'].intersects(cap) for o in touch.get(i,())): continue
        ds=[items[i]['geom'].intersection(items[o]['geom']).distance(P) for o in touch.get(i,())]
        d=min(ds) if ds else 1e9
        if d>4: print('  %s L%s free end (%.1f,%.1f) dead length %.0f mil, other end (%.1f,%.1f)'%(it['net'],it['layer'],e[0],e[1]-YOFF,d,w['pts'][1-k][0],w['pts'][1-k][1]-YOFF))
def near(pt,rad,net=None,kinds=('wire','via')):
    P=Point(pt[0],pt[1]+YOFF); res=[]
    for i,it in enumerate(items):
        if it['kind'] in kinds and (net is None or it['net']==net) and it['geom'].distance(P)<rad:
            if it['kind'] in('via','pad') and it['layer']!='1': continue
            res.append(desc(i))
    return res
for name,pt,net,rad in (('new GND via',(6685,-7100),'GND',2),('CN8.11',(6575,-7000),'GND',1),('CN8.13',(6575,-7100),'GND',1),('CN7.8',(8275,-6540),'GND',1),('old via A',(6530,-7050),None,20),('old via B',(8305,-6575),None,20),
    ('ENB2 T',(7255,-3327.1),'ENB2',3),('ENB2 old end',(7376.5,-3327.1),'ENB2',30),('L_OE old via',(8602.91,-6547.71),None,8),('DRV_PAD_A old via',(7839.04,-3948.49),None,8),('GEN_H',(5395,-6415),'GEN_H',8),
    ('DRV_B_MTR T',(7739.7,-6275),'DRV_B_MTR',3),('DRV_B_MTR old end',(7739.7,-7000),'DRV_B_MTR',5),('AUX2',(8235.2,-2474.7),'AUX2',15),('G_SLB',(13058.5,-2420.8),'G_SLB',15),('DRV_PWR',(6908.3,-6785),'DRV_PWR',15),('J5',(9160,-9365),None,8)):
    print(name,pt); [print('    ',x) for x in near(pt,rad,net,('wire','via','pad'))]
pours=[(i,it) for i,it in enumerate(items) if it['kind']=='pour']
for i,it in pours: print('pour',it['ref'],it['net'],'area %.0f'%it['geom'].area)
main=[it for i,it in pours if it['ref'][0]=='GND_L15'][0]['geom']
P=Point(6685,-7100+YOFF); v=P.buffer(16)
print('new via: centre inside main GND pour:',main.contains(P),'| whole via disc inside:',main.contains(v),'| overlap area %.0f of %.0f'%(main.intersection(v).area,v.area),'| dist centre to pour edge %.1f'%main.boundary.distance(P))
vi=[ids for ids in thru if items[ids[0]]['kind']=='via' and abs(vias[items[ids[0]]['ref']]['x']-6685)<1 and abs(vias[items[ids[0]]['ref']]['y']-YOFF+7100)<1][0]
for i in vi: print('   via layer',items[i]['layer'],'touches',[desc(o) for o in touch.get(i,())])
# via diameters in live dump
print('via dia',collections.Counter(v_.get('d') for v_ in vias))
# CH_A4 via vs AUX5
V=[v_ for v_ in vias if v_['net']=='CH_A4' and abs(v_['x']-11257.5)<2][0]
print('CH_A4 via',V['x'],V['y']-YOFF,V['d'])
for i,it in enumerate(items):
    if it['kind']=='wire' and it['net']=='AUX5' and it['layer']=='16':
        d=LineString(wires[it['ref']]['pts']).distance(Point(V['x'],V['y']))
        if d<40: w=wires[it['ref']]; print('  AUX5 centreline dist %.3f, track w %.2f -> edge gap with d=32: %.3f ; with d=31.5: %.3f'%(d,w['w'],d-w['w']/2-16,d-w['w']/2-15.75),desc(i))
