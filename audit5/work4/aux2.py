import sys; sys.path.insert(0,'work4')
from geom import *
pins,pst,nets,wires,vias=load_pcb()
D=pickle.load(open('work4/conn.pkl','rb')); items=D['items'];touch=D['touch']
for i,it in enumerate(items):
    if it['kind']=='wire' and it['net']=='AUX2':
        w=wires[it['ref']]
        if min(math.dist(p,(8250,-2480+YOFF)) for p in w['pts'])<1:
            print('wire L'+it['layer'],[(round(a,1),round(b-YOFF,1)) for a,b in w['pts']])
            for o in touch[i]:
                g=items[i]['geom'].intersection(items[o]['geom']).centroid
                k=items[o]
                print('   contact at (%.0f,%.0f) with'%(g.x,g.y-YOFF),k['kind'],k['net'],'L'+k['layer'], [(round(a,1),round(b-YOFF,1)) for a,b in wires[k['ref']]['pts']] if k['kind']=='wire' else '')
for v in vias:
    if v['net']=='AUX2' and abs(v['x']-8250)<400 and abs(v['y']-YOFF+2480)<100: print('via',v['x'],v['y']-YOFF)
