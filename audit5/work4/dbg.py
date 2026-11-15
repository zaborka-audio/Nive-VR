import sys; sys.path.insert(0,'work4')
from geom import *
pins,pst,nets,wires,vias=load_pcb()
D=pickle.load(open('work4/conn.pkl','rb')); items=D['items'];roots=D['roots'];touch=D['touch'];thru=D['thru']
def show(pt,rad=40,net=None):
    pt=(pt[0],pt[1]+YOFF)
    for i,it in enumerate(items):
        if it['layer'] not in('1','2','16'): continue
        if net and it['net']!=net: continue
        if it['geom'].distance(Point(pt))<rad:
            if it['kind']=='wire':
                w=wires[it['ref']]; print('  wire',i,it['net'],'L'+it['layer'],w['w'],[(round(a,1),round(b-YOFF,1)) for a,b in w['pts']],'touch',sorted(touch.get(i,())))
            elif it['kind']=='via' and it['layer']=='1': v=vias[it['ref']];print('  via',i,it['net'],v['x'],v['y']-YOFF)
            elif it['kind']=='pad' and it['layer']=='1': p=pins[it['ref']];print('  pad',i,it['net'],p['x'],p['y']-YOFF)
for pt,net in (((8736.4,-7307.0),'DRV_PWR'),((8836.8,-6303.8),'L_OE'),((7769.0,-4457.0),'ENB2'),((11347.9,-568.7),'G_CSCB')):
    print(pt,net); show(pt,30,net)
print('=====')
pinmap=pickle.load(open('work4/pinmap.pkl','rb'))
def show2(pt,rad=45):
    P=Point(pt[0],pt[1]+YOFF)
    seen=set()
    for i,it in enumerate(items):
        d=it['geom'].distance(P)
        if d<rad and it['kind'] in('wire','via','pad'):
            if it['kind']=='wire':
                w=wires[it['ref']]; print('   %.1f wire %s L%s w%.0f %s'%(d,it['net'],it['layer'],w['w'],[(round(a,1),round(b-YOFF,1)) for a,b in w['pts']]))
            elif (it['kind'],it['ref']) not in seen:
                seen.add((it['kind'],it['ref']))
                if it['kind']=='via': v=vias[it['ref']];print('   %.1f via %s (%.1f,%.1f)'%(d,it['net'],v['x'],v['y']-YOFF))
                else: p=pins[it['ref']];print('   %.1f pad %s %s (%.1f,%.1f)'%(d,it['net'],pinmap.get(it['ref'],('HOLE',))[0],p['x'],p['y']-YOFF))
for pt in ((8736.4,-7307.0),(8836.8,-6303.8),(7769.0,-4457.0),(8833.8,-6986.9),(7746.7,-7354.8),(7870.2,-4474.0),(8841.1,-7417.1),(8859.1,-6260.2),(9618.0,-7573.8),(11347.9,-568.7),(8072.0,-8039.2),(8208.3,-8130.2),(9513.0,-6480.1)):
    print(pt); show2(pt)
