import sys; sys.path.insert(0,'work4')
from geom import *
pins,pst,nets,wires,vias=load_pcb()
pinmap=pickle.load(open('work4/pinmap.pkl','rb'))
D=pickle.load(open('work4/conn.pkl','rb')); items=D['items'];roots=D['roots'];touch=D['touch'];thru=D['thru']
def pname(pid):
    if pid in pinmap:
        d,c=pinmap[pid]; return d+'.'+('|'.join(c) if c else 'MNT')
    return 'HOLE@%d,%d'%(pins[pid]['x'],pins[pid]['y']-YOFF)
isl=collections.defaultdict(list)
for i,r in enumerate(roots): isl[r].append(i)
# shorts / label mismatches
nshort=0
netisl=collections.defaultdict(set)
for r,ix in isl.items():
    labels=collections.defaultdict(list)
    for i in ix: labels[items[i]['net']].append(i)
    for n in labels: netisl[n].add(r)
    if len(labels)>1:
        nshort+=1
        print('SHORT/LABEL island',r,{n:collections.Counter(items[i]['kind'] for i in v) for n,v in labels.items()})
print('islands with >1 net label:',nshort)
nopen=0
for n,rs in netisl.items():
    if len(rs)>1:
        nopen+=1
        print('OPEN net',n,'islands',len(rs))
        for r in rs:
            k=collections.Counter(items[i]['kind'] for i in isl[r] if items[i]['net']==n)
            pp=sorted({pname(items[i]['ref']) for i in isl[r] if items[i]['kind']=='pad'})
            print('    ',dict(k),pp[:12])
print('nets split into several islands:',nopen)
print('nets',len([n for n in netisl if not n.startswith('NC:')]),'NC pads',len([n for n in netisl if n.startswith('NC:')]))
# NC pads touching anything
for n,rs in netisl.items():
    if n.startswith('NC:'):
        for r in rs:
            if len(isl[r])!=4: print('NC pad island with extra copper',n,len(isl[r]))
# dangling wire ends
dang=[]
for i,it in enumerate(items):
    if it['kind']!='wire': continue
    w=wires[it['ref']]
    for e in w['pts']:
        pt=Point(e)
        ok=False
        for o in touch.get(i,()):
            if items[o]['geom'].distance(pt)<=max(0.5, 0.0): ok=True;break
        if not ok:
            # second chance: other item overlaps the end cap
            cap=pt.buffer(w['w']/2)
            near=[o for o in touch.get(i,()) if items[o]['geom'].intersects(cap)]
            dang.append((it['net'],it['layer'],e,w['w'],w['pts'],[(items[o]['kind'],round(items[o]['geom'].distance(pt),2)) for o in near]))
print('wire ends not landing on other copper:',len(dang))
for d in dang: print('  ',d[0],'L'+d[1],'end (%.1f,%.1f)'%(d[2][0],d[2][1]-YOFF),'w',d[3],'seg',[(round(a,1),round(b-YOFF,1)) for a,b in d[4]],d[5])
# vias
stub=[]
for ids in thru:
    if items[ids[0]]['kind']!='via': continue
    conn=collections.Counter()
    for i in ids:
        for o in touch.get(i,()):
            conn[(items[o]['layer'],items[o]['kind'])]+=1
    layers={l for l,k in conn}
    v=vias[items[ids[0]]['ref']]
    if len(layers)<2: stub.append((v['net'],v['x'],v['y']-YOFF,dict(conn)))
print('vias connecting <2 layers:',len(stub))
for s in stub: print('  ',s)
vc=collections.Counter(v['net'] for v in vias); print('vias by net',vc.most_common(12))
