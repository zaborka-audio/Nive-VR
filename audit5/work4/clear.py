import sys; sys.path.insert(0,'work4')
from geom import *
import numpy as np
from shapely.ops import nearest_points
pins,pst,nets,wires,vias=load_pcb()
pinmap=pickle.load(open('work4/pinmap.pkl','rb'))
D=pickle.load(open('work4/conn.pkl','rb')); items=D['items'];roots=D['roots'];touch=D['touch'];thru=D['thru']
def desc(i):
    it=items[i]
    if it['kind']=='wire':
        w=wires[it['ref']]; return 'wire w%.0f (%.1f,%.1f)-(%.1f,%.1f)'%(w['w'],w['pts'][0][0],w['pts'][0][1]-YOFF,w['pts'][1][0],w['pts'][1][1]-YOFF)
    if it['kind']=='via': v_=vias[it['ref']]; return 'via (%.1f,%.1f)'%(v_['x'],v_['y']-YOFF)
    if it['kind']=='pad':
        p=pins[it['ref']]; d,c=pinmap.get(it['ref'],('HOLE',[])); return 'pad %s.%s (%.1f,%.1f)'%(d,'|'.join(c) if len(c)<4 else 'NC',p['x'],p['y']-YOFF)
    return it['kind']+str(it['ref'])
bylayer=collections.defaultdict(list)
for i,it in enumerate(items): bylayer[it['layer']].append(i)
out=[]
mins={}
for l,idx in bylayer.items():
    gs=[items[i]['geom'] for i in idx]
    tree=STRtree(gs)
    a,b=tree.query(gs,predicate='dwithin',distance=12.0)
    m=1e9
    for x,y in zip(a,b):
        if x>=y: continue
        i,jx=idx[x],idx[y]
        if roots[i]==roots[jx]: continue
        d=gs[x].distance(gs[y])
        m=min(m,d)
        if d<9.84:
            p1,p2=nearest_points(gs[x],gs[y])
            out.append((d,l,items[i]['net'],items[jx]['net'],desc(i),desc(jx),(p1.x+p2.x)/2,(p1.y+p2.y)/2-YOFF,(items[i]['kind'],items[jx]['kind'])))
    mins[l]=m
print('min different-net spacing per layer (only pairs <12 mil examined):',{k:round(v,3) for k,v in mins.items()})
out.sort()
print('pairs < 9.84:',len(out),' < 9.5:',sum(o[0]<9.5 for o in out))
print(collections.Counter((o[1],o[8]) for o in out if o[0]<9.5))
for o in out:
    if o[0]<9.5: print('%.2f L%s %s / %s @(%.0f,%.0f) | %s | %s'%(o[0],o[1],o[2],o[3],o[6],o[7],o[4],o[5]))
pickle.dump(out,open('work4/clear.pkl','wb'))
