import sys; sys.path.insert(0,'work4')
from geom import *
pins,pst,nets,wires,vias=load_pcb()
pinmap=pickle.load(open('work4/pinmap.pkl','rb'))
D=pickle.load(open('work4/conn.pkl','rb')); items=D['items'];roots=D['roots'];touch=D['touch'];thru=D['thru']
def neck(a,b):
    g=items[a]['geom'].intersection(items[b]['geom'])
    if g.is_empty: return 0.0
    if g.geom_type not in('Polygon','MultiPolygon'): return 0.0
    r=g.minimum_rotated_rectangle
    if r.geom_type!='Polygon': return 0.0
    c=list(r.exterior.coords)
    s1=math.dist(c[0],c[1]);s2=math.dist(c[1],c[2])
    return max(s1,s2)
pairs={}
for a,s in touch.items():
    for b in s:
        if a<b: pairs[(a,b)]=neck(a,b)
pickle.dump(pairs,open('work4/pairs.pkl','wb'))
import numpy as np
v=np.array(list(pairs.values()))
print('touching pairs',len(v),'neck<2:',(v<2).sum(),'<4:',(v<4).sum(),'<6:',(v<6).sum(),'<8:',(v<8).sum(),'<10:',(v<10).sum())
def comps(th):
    parent=list(range(len(items)))
    def f(a):
        while parent[a]!=a: parent[a]=parent[parent[a]];a=parent[a]
        return a
    for ids in thru:
        for x in ids[1:]: parent[f(x)]=f(ids[0])
    for (a,b),n in pairs.items():
        if n>=th: parent[f(b)]=f(a)
    return [f(i) for i in range(len(items))]
def desc(i):
    it=items[i]
    if it['kind']=='wire':
        w=wires[it['ref']]; return 'wire L%s w%.0f (%.0f,%.0f)-(%.0f,%.0f)'%(it['layer'],w['w'],w['pts'][0][0],w['pts'][0][1]-YOFF,w['pts'][1][0],w['pts'][1][1]-YOFF)
    if it['kind']=='via': v_=vias[it['ref']]; return 'via (%.0f,%.0f)'%(v_['x'],v_['y']-YOFF)
    if it['kind']=='pad':
        p=pins[it['ref']]; d,c=pinmap.get(it['ref'],('HOLE',[])); return 'pad %s.%s (%.0f,%.0f)'%(d,'|'.join(c),p['x'],p['y']-YOFF)
    return it['kind']+str(it['ref'])
for th in (3,5,7,9):
    r=comps(th)
    # nets whose pads split
    netr=collections.defaultdict(set)
    for i,it in enumerate(items):
        if it['kind']=='pad' and not it['net'].startswith('NC:'): netr[it['net']].add(r[i])
    split=[n for n,s in netr.items() if len(s)>1]
    print('threshold',th,'mil: nets whose pads would split if joints narrower than this are ignored:',len(split),split)
print('--- joints with neck < 9 mil (sorted)')
for (a,b),n in sorted(pairs.items(),key=lambda x:x[1]):
    if n<9: print('%.2f'%n,items[a]['net'],'|',desc(a),'|',desc(b))
