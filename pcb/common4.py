import json,re
D=json.load(open('full5.json'))
C={c[0]:dict(d=c[0],x=c[1],y=c[2],r=c[3],layer=c[4],fp=c[5],id=c[6],pins=c[7],bb=c[8]) for c in D['c']}
HOLES=D['free'][:9]
pages={}
for part in open('pages.txt').read().split('##'):
    m=re.match(r'\s*PAGE (\w+) ([^:]+): (.*)',part.strip())
    if m:
        for d in m.group(3).split(','): pages.setdefault(d.strip(),m.group(1))
for i in range(1,16): pages['RN%d'%i]='p9'
PG={}
for d in C: PG.setdefault(pages.get(d,'?'),[]).append(d)
def gbb(ds,pos=None):
    xs=[];ys=[]
    for d in ds:
        b=C[d]['bb']; 
        if pos: 
            dx=pos[d][0]-C[d]['x']; dy=pos[d][1]-C[d]['y']
        else: dx=dy=0
        xs+= [b[0]+dx,b[2]+dx]; ys+=[b[1]+dy,b[3]+dy]
    return min(xs),min(ys),max(xs),max(ys)
