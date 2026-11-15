import sys; sys.path.insert(0,'work4')
from geom import *
pins,pst,nets,wires,vias=load_pcb()
D=pickle.load(open('work4/conn.pkl','rb')); items=D['items'];roots=D['roots'];touch=D['touch'];thru=D['thru']
# via groups: via item -> group id; treat via as node spanning layers
grp={}
for g,ids in enumerate(thru):
    for i in ids: grp[i]=g
alive=set(range(len(items)))
def wire_sides(i):
    w=wires[items[i]['ref']]; a,b=Point(w['pts'][0]),Point(w['pts'][1])
    L=a.distance(b); r=w['w']/2
    sa=sb=mid=0
    for o in touch.get(i,()):
        if o not in alive: continue
        g=items[i]['geom'].intersection(items[o]['geom'])
        if g.is_empty: continue
        c=g.centroid
        da,db=c.distance(a),c.distance(b)
        # classify by where the contact region is along the wire
        ga,gb=g.distance(a),g.distance(b)
        if ga<=0.5 and gb<=0.5: sa+=1;sb+=1
        elif ga<=r*1.01+0.5 and ga<=gb: sa+=1
        elif gb<=r*1.01+0.5 and gb<ga: sb+=1
        else: mid+=1
    return sa,sb,mid
pruned=[]
changed=True
while changed:
    changed=False
    for i in list(alive):
        it=items[i]
        if it['kind']=='wire':
            sa,sb,mid=wire_sides(i)
            if (sa==0 or sb==0) and mid==0:
                alive.discard(i); pruned.append(i); changed=True
            elif (sa==0 or sb==0) and mid>0:
                pass
    # vias with single remaining connection
    for g,ids in enumerate(thru):
        if items[ids[0]]['kind']!='via' or ids[0] not in alive: continue
        con=[o for i in ids for o in touch.get(i,()) if o in alive]
        if len(con)<=1:
            for i in ids: alive.discard(i)
            pruned.append(ids[0]); changed=True
print('pruned antenna items:',len(pruned))
for i in pruned:
    it=items[i]
    if it['kind']=='wire':
        w=wires[it['ref']]; print('  wire',it['net'],'L'+it['layer'],'w',w['w'],[(round(a,1),round(b-YOFF,1)) for a,b in w['pts']],'len %.1f'%math.dist(*w['pts']))
    else:
        v=vias[it['ref']]; print('  via',it['net'],v['x'],v['y']-YOFF)
# wires with a free end but mid contact (overshoot stubs)
# group pruned items into chains
ps=set(pruned)
for g,ids in enumerate(thru):
    if ids[0] in ps: ps|=set(ids)
par={i:i for i in ps}
def f(a):
    while par[a]!=a: par[a]=par[par[a]];a=par[a]
    return a
for ids in thru:
    if ids[0] in ps:
        for x in ids[1:]: par[f(x)]=f(ids[0])
for i in ps:
    for o in touch.get(i,()):
        if o in ps: par[f(o)]=f(i)
ch=collections.defaultdict(list)
for i in ps: ch[f(i)].append(i)
print('chains',len(ch))
pinmap=pickle.load(open('work4/pinmap.pkl','rb'))
rows=[]
for r,ix in ch.items():
    ws=[i for i in ix if items[i]['kind']=='wire']
    L=sum(math.dist(*wires[items[i]['ref']]['pts']) for i in ws)
    nv=len({items[i]['ref'] for i in ix if items[i]['kind']=='via'})
    # free ends: wire endpoints not within any other item of whole board (alive or pruned) except own
    fe=[]
    for i in ws:
        w=wires[items[i]['ref']]
        for e in w['pts']:
            cap=Point(e).buffer(w['w']/2*0.6)
            if not any(items[o]['geom'].intersects(cap) for o in touch.get(i,())): fe.append((round(e[0],1),round(e[1]-YOFF,1)))
    # attach: non-pruned items touched
    att=set()
    for i in ix:
        for o in touch.get(i,()):
            if o not in ps:
                it=items[o]
                if it['kind']=='pad': att.add('pad '+pinmap.get(it['ref'],('HOLE',['']))[0]+'.'+'|'.join(pinmap.get(it['ref'],('',['']))[1][:2]))
                elif it['kind']=='via': att.add('via(%.0f,%.0f)'%(vias[it['ref']]['x'],vias[it['ref']]['y']-YOFF))
                else:
                    w=wires[it['ref']]; att.add('track L%s'%it['layer'])
    rows.append((L,items[ix[0]]['net'],sorted({items[i]['layer'] for i in ws}),nv,fe,sorted(att)))
rows.sort(reverse=True)
for r in rows: print('%.0f mil'%r[0],r[1],'layers',r[2],'vias',r[3],'free end',r[4],'attached to',r[5])
pickle.dump(rows,open('work4/antenna.pkl','wb'))
