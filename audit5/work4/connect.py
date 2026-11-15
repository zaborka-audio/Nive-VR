import sys; sys.path.insert(0,'work4')
from geom import *
import numpy as np
pins,pst,nets,wires,vias=load_pcb()
pinmap=pickle.load(open('work4/pinmap.pkl','rb'))
def pname(pid):
    if pid in pinmap:
        d,c=pinmap[pid]
        return d+'.'+('|'.join(c) if c else 'MNT')
    return 'HOLE@%d,%d'%(pins[pid]['x'],pins[pid]['y']-YOFF)
items=[]  # dict kind, layer, geom, net, ref
def add(kind,layer,geom,net,ref): items.append({'kind':kind,'layer':layer,'geom':geom,'net':net,'ref':ref}); return len(items)-1
parent=[]
def find_(a):
    while parent[a]!=a:
        parent[a]=parent[parent[a]]; a=parent[a]
    return a
def union(a,b):
    a,b=find_(a),find_(b)
    if a!=b: parent[b]=a
thru=[] # groups to union across layers
for pid,p in pins.items():
    if p['ps']==VIAPS: continue
    ids=[]
    bylayer=collections.defaultdict(list)
    for s in pst[p['ps']]: bylayer[LAYMAP[s[1]]].append(pad_geom(s,p['x'],p['y']))
    assert set(bylayer)==set(LAYERS),p
    for l,gs in bylayer.items():
        ids.append(add('pad',l,unary_union(gs) if len(gs)>1 else gs[0],p['net'] or 'NC:'+pname(pid),pid))
    thru.append(ids)
for i,v in enumerate(vias):
    ids=[add('via',l,Point(v['x'],v['y']).buffer(v.get('d',31.5)/2,32),v['net'],i) for l in LAYERS]
    thru.append(ids)
for i,w in enumerate(wires):
    assert len(w['pts'])==2
    if w['pts'][0]==w['pts'][1]: g=Point(w['pts'][0]).buffer(w['w']/2,16)
    else: g=LineString(w['pts']).buffer(w['w']/2,16)
    add('wire',w['layer'],g,w['net'],i)
# pours
j=json.load(open('pcb_pours4.json',encoding='utf8'))
pourinfo=[]
for po,p in zip(j['pours'],j['poured']):
    assert po['PrimitiveId']==p.get('PourPrimitiveId',p['PrimitiveId']) and po['Layer']==15
    for f in p['PourFills']:
        cp=f['path']['complexPolygon']
        if f['fill']:
            rings=[]
            for sub in cp:
                pts=path_pts(sub)
                if len(pts)<3: continue
                g=Polygon(pts)
                if not g.is_valid: g=g.buffer(0)
                if g.area>0: rings.append(g)
            tree=STRtree(rings)
            depth=[]
            for ri,r in enumerate(rings):
                rp=Point(r.exterior.coords[0])
                cand=[c for c in tree.query(rp,predicate='within') if c!=ri]
                depth.append(len(cand))
            res=None
            for d in range(max(depth)+1):
                u=unary_union([r for r,dd in zip(rings,depth) if dd==d])
                res=u if res is None else (res.union(u) if d%2==0 else res.difference(u))
            parts=list(res.geoms) if res.geom_type=='MultiPolygon' else [res]
            pourinfo.append((po['PourName'],po['Net'],len(rings),collections.Counter(depth),len(parts),res.area))
            for k,g in enumerate(parts): add('pour','15',g,po['Net'],(po['PourName'],k))
        else:
            for sub in cp:
                pts=path_pts(sub)
                add('spoke','15',LineString(pts).buffer(f['lineWidth']*10/2,8),po['Net'],(po['PourName'],f['id']))
for x in pourinfo: print('pour',x)
parent=list(range(len(items)))
for ids in thru:
    for a in ids[1:]: union(ids[0],a)
bylayer=collections.defaultdict(list)
for i,it in enumerate(items): bylayer[it['layer']].append(i)
touch=collections.defaultdict(set)
for l,idx in bylayer.items():
    gs=[items[i]['geom'] for i in idx]
    tree=STRtree(gs)
    a,b=tree.query(gs,predicate='intersects')
    for x,y in zip(a,b):
        if x<y:
            union(idx[x],idx[y]); touch[idx[x]].add(idx[y]); touch[idx[y]].add(idx[x])
    print('layer',l,'items',len(idx),collections.Counter(items[i]['kind'] for i in idx))
roots=[find_(i) for i in range(len(items))]
pickle.dump({'items':items,'roots':roots,'touch':dict(touch),'thru':thru},open('work4/conn.pkl','wb'))
isl=collections.defaultdict(list)
for i,r in enumerate(roots): isl[r].append(i)
print('islands',len(isl))
