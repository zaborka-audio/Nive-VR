import re,sys,collections,math
dsn=open(sys.argv[1]).read()
pins={m.group(2):(float(m.group(3)),float(m.group(4))) for m in re.finditer(r'\(pin (\S+) (\S+) (-?[\d.]+) (-?[\d.]+)\)',dsn)}
net_pins={}
nw=dsn[dsn.index('(network'):dsn.index('(wiring')]
for m in re.finditer(r'\(net (\S+)\s*\(pins ([^)]*)\)',nw):
    net_pins[m.group(1).strip('"')]=[p.split('-',1)[1] for p in m.group(2).split()]
wr=dsn[dsn.index('(wiring'):]
segs=collections.defaultdict(list);vias=collections.defaultdict(list)
for m in re.finditer(r'\(wire\s*\(path (\S+) ([\d.]+)((?:\s+-?[\d.]+)+)\s*\)\s*\(net (\S+)\)',wr):
    c=[float(v) for v in m.group(3).split()];pts=[(c[i],c[i+1]) for i in range(0,len(c),2)]
    segs[m.group(4).strip('"')].append((m.group(1),pts))
for m in re.finditer(r'\(via \S+ (-?[\d.]+) (-?[\d.]+)\s*\(net (\S+)\)',wr):
    vias[m.group(3).strip('"')].append((float(m.group(1)),float(m.group(2))))
def dseg(p,a,b):
    ax,ay=a;bx,by=b;dx,dy=bx-ax,by-ay;L=dx*dx+dy*dy
    t=0 if L==0 else max(0,min(1,((p[0]-ax)*dx+(p[1]-ay)*dy)/L))
    return math.hypot(p[0]-ax-t*dx,p[1]-ay-t*dy)
total=0;out=[]
skip=set(sys.argv[2:])
for net,pl in net_pins.items():
    if len(pl)<2 or net in skip: continue
    nodes=[(None,[pins[p]]) for p in pl if p in pins];npin=len(nodes)
    for v in vias.get(net,[]): nodes.append((None,[v]))
    for lay,pp in segs.get(net,[]): nodes.append((lay,pp))
    par=list(range(len(nodes)))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]];a=par[a]
        return a
    for i in range(len(nodes)):
        li,pi=nodes[i]
        for j in range(len(nodes)):
            if i==j: continue
            lj,pj=nodes[j]
            if li is not None and lj is not None and li!=lj: continue
            # endpoints of i near any segment/point of j
            ends=[pi[0],pi[-1]] if li else pi
            ok=False
            for e in ends:
                if len(pj)==1: ok=math.hypot(e[0]-pj[0][0],e[1]-pj[0][1])<20
                else: ok=any(dseg(e,a,b)<12 for a,b in zip(pj,pj[1:]))
                if ok: break
            if ok: par[f(i)]=f(j)
    g=collections.defaultdict(list)
    for i in range(npin): g[f(i)].append(nodes[i][1][0])
    n=len(g)-1
    if n>0: total+=n;out.append((net,n,[v[0] for v in g.values()]))
print('unrouted',total)
for net,n,g in sorted(out,key=lambda x:-x[1]): print(net,n,[(round(x),round(y)) for x,y in g][:6])
