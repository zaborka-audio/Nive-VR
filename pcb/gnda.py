import json
exec(open('common4.py').read())
src=open('pl9.py').read(); exec(src[:src.index('P=lambda')])
pos=json.load(open('plv2.json'))
pts=[]
for d in pos:
    for x,y,n in pins_at(d,*pos[d]):
        if n=='GNDA': pts.append((round(x),round(y),d))
pts.sort()
from collections import defaultdict
g=defaultdict(list)
for x,y,d in pts: g[pages.get(d,'?')].append((d,x,y))
for k,v in g.items():
    xs=[a[1] for a in v]; ys=[a[2] for a in v]
    print(k,len(v),'x',min(xs),max(xs),'y',min(ys),max(ys),sorted(set(a[0] for a in v)))
