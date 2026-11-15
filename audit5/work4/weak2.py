import sys; sys.path.insert(0,'work4')
from geom import *
pins,pst,nets,wires,vias=load_pcb()
pinmap=pickle.load(open('work4/pinmap.pkl','rb'))
D=pickle.load(open('work4/conn.pkl','rb')); items=D['items'];roots=D['roots'];touch=D['touch'];thru=D['thru']
pairs=pickle.load(open('work4/pairs.pkl','rb'))
def width(i):
    it=items[i]
    if it['kind']=='wire': return wires[it['ref']]['w']
    if it['kind']=='spoke': return 15.75
    return 999
def desc(i):
    it=items[i]
    if it['kind']=='wire':
        w=wires[it['ref']]; return 'wire L%s w%.0f (%.1f,%.1f)-(%.1f,%.1f)'%(it['layer'],w['w'],w['pts'][0][0],w['pts'][0][1]-YOFF,w['pts'][1][0],w['pts'][1][1]-YOFF)
    if it['kind']=='via': v_=vias[it['ref']]; return 'via (%.1f,%.1f)'%(v_['x'],v_['y']-YOFF)
    if it['kind']=='pad':
        p=pins[it['ref']]; d,c=pinmap.get(it['ref'],('HOLE',[])); return 'pad %s.%s (%.1f,%.1f)'%(d,'|'.join(c),p['x'],p['y']-YOFF)
    return it['kind']+str(it['ref'])
def split_without(excl):
    parent=list(range(len(items)))
    def f(a):
        while parent[a]!=a: parent[a]=parent[parent[a]];a=parent[a]
        return a
    for ids in thru:
        for x in ids[1:]: parent[f(x)]=f(ids[0])
    for (a,b) in pairs:
        if (a,b) not in excl: parent[f(b)]=f(a)
    netr=collections.defaultdict(set)
    for i,it in enumerate(items):
        if it['kind']=='pad' and not it['net'].startswith('NC:'): netr[it['net']].add(f(i))
    return [n for n,s in netr.items() if len(s)>1]
weak=[(p,n) for p,n in pairs.items() if n<0.8*min(width(p[0]),width(p[1]),12.06) and not (items[p[0]]['kind']=='spoke' and items[p[1]]['kind']=='spoke')]
print('weak joints (neck < 0.8*min(track width,12)):',len(weak))
res=[]
for (a,b),n in sorted(weak,key=lambda x:x[1]):
    s=split_without({(a,b)})
    g=items[a]['geom'].intersection(items[b]['geom']); c=g.centroid
    res.append({'neck':n,'net':items[a]['net'],'a':desc(a),'b':desc(b),'bridge':bool(s),'x':c.x,'y':c.y-YOFF,'layer':items[a]['layer'],'kinds':(items[a]['kind'],items[b]['kind'])})
    print('%5.2f %-12s %s L%s (%.0f,%.0f) | %s | %s'%(n,items[a]['net'],'BRIDGE' if s else 'redund',items[a]['layer'],c.x,c.y-YOFF,desc(a),desc(b)))
pickle.dump(res,open('work4/weak.pkl','wb'))
print('bridging:',sum(r['bridge'] for r in res))
