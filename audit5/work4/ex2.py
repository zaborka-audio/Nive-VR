import sys; sys.path.insert(0,'work4')
from dsn import *
t=load()
lib=find(t,'library')[0]
img=find(lib,'image')[0]
pins=find(img,'pin')
print(len(pins), collections.Counter(len(p) for p in pins))
print([p for p in pins if len(p)!=5][:5])
ps=collections.Counter(p[1] for p in pins)
print(len(ps), ps.most_common(8))
print(collections.Counter(len(p[2]) for p in pins if p[1]!='pf07a228c575f71a'))
pst=find(lib,'padstack')
for p in pst:
    kinds=collections.Counter((s[1][0],s[1][1]) for s in find(p,'shape'))
    print(p[1], ps.get(p[1]), dict(kinds), [x for x in p[2:] if x[0]!='shape'])
net=find(t,'network')[0]
nets=find(net,'net'); print('nets',len(nets))
print([x[0] if isinstance(x,list) else x for x in net[1:]][-6:])
print(net[-1] if net[-1][0]!='net' else '')
w=find(t,'wiring')[0]
wires=find(w,'wire'); vias=find(w,'via')
print(len(wires),len(vias))
print(collections.Counter((x[1][0],x[1][1],x[1][2]) for x in wires))
print(collections.Counter(len(x[1]) for x in wires))
print(collections.Counter(tuple(y[0] for y in x[2:]) for x in wires))
print(collections.Counter(tuple(y[0] if isinstance(y,list) else 'n' for y in x[1:]) for x in vias))
print(collections.Counter(tuple(y[1] for y in x[2:] if y[0]=='type') for x in wires))
