import json,math,numpy as np
src=open('pl9.py').read(); exec(src[:src.index('P=lambda')])
pos={d:list(v) for d,v in json.load(open('pl9.json')).items()}
pos.setdefault('U50',[C['U50']['x'],C['U50']['y'],C['U50']['r']])
SENS={'C95','C96','C97','C98','C99','C100','D13','D14','D15','D16','D17','D18','R187','R188','R189','R190','R191'}
def grp(d):
    p=pages.get(d,'?')
    if d=='U50': return 'VREG'
    if d in('J5','J6','J7','J8'): return 'XLR'
    if d.startswith('CN'): return 'NUC'
    if d in('U1','U2','U3','C1','C2','C3'): return 'DRV'
    if p=='p13' and d in SENS: return 'SENS'
    return {'p6':'SUM','p12':'ADC','p11':'LM'}.get(p)
MOV=[d for d in pos if grp(d)]
X0=6047
NUCBOX=(X0,-9800,X0+2756,-4550)
# anchors
pos['CN8']=[X0+378,-6850,270];pos['CN9']=[X0+378,-8100,270];pos['CN7']=[X0+2378,-6690,270];pos['CN10']=[X0+2378,-8100,270]
xl=[('J5',8850),('J6',9910),('J7',11320),('J8',12380)]
for d,x0 in xl:
    b=bbox_at(d,0,pos[d][1],pos[d][2]); pos[d][0]=x0-b[0]
for i,d in enumerate(['U1','U2','U3']): pos[d]=[9150,-5100-i*1150,90]
HOLES=[(157,-157),(4518,-157),(13219,-157),(4518,-3583),(13219,-3583),(157,-H+157),(4450,-H+157),(11115,-H+157),(W-157,-H+157)]
CELL=25;GX,GY=int(W/CELL)+2,int(H/CELL)+2
occ=np.zeros((GX,GY),dtype=np.int16)
def cells(b): return max(0,int(math.floor(b[0]/CELL))),min(GX,int(math.ceil(b[2]/CELL))),max(0,int(math.floor(-b[3]/CELL))),min(GY,int(math.ceil(-b[1]/CELL)))
def mark(b,v=1):
    i0,i1,j0,j1=cells(b);occ[i0:i1,j0:j1]+=v
def isfree(b,reg):
    if b[0]<reg[0] or b[2]>reg[2] or b[1]<reg[1] or b[3]>reg[3]: return False
    i0,i1,j0,j1=cells(b);return not occ[i0:i1,j0:j1].any()
M=20
fixed={d for d in pos if not grp(d)}|{'CN7','CN8','CN9','CN10','J5','J6','J7','J8','U1','U2','U3'}
for d in fixed: mark(bbox_at(d,*pos[d],M))
mark(NUCBOX)
mark((X0+2850,-4660,13750,-4250))  # audio corridor
for hx,hy in HOLES: mark((hx-210,hy-210,hx+210,hy+210))
REG={'VREG':(2600,-5650,4150,-4550),'SUM':(4480,-6350,5970,-4300),'SENS':(4480,-8050,5970,-6400),'ADC':(4480,-9800,5970,-8100),
     'DRV':(8880,-8250,9480,-4680),'LM':(9500,-8400,13780,-4680)}
POWER={'GND','GNDA','VIN24','+16V','-16V','VL','VR','+5V','+3V3','P17','N17A','N17L','P12',''}
netpins={}
def addpins(d):
    for x,y,n in pins_at(d,*pos[d]):
        if n not in POWER: netpins.setdefault(n,[]).append((x,y,d))
for d in fixed: addpins(d)
rest=[d for d in MOV if d not in fixed]
def score(d): return -sum(len(netpins.get(p[3],[])) for p in C[d]['pins'] if p[3] not in POWER)
fails=[]
for d in sorted(rest,key=score):
    reg=REG[grp(d)]
    pts=[(x,y) for p in C[d]['pins'] if p[3] not in POWER for (x,y,_) in netpins.get(p[3],[])]
    if pts: t=(sum(a for a,b in pts)/len(pts),sum(b for a,b in pts)/len(pts))
    else: t=((reg[0]+reg[2])/2,(reg[1]+reg[3])/2)
    t=(min(max(t[0],reg[0]),reg[2]),min(max(t[1],reg[1]),reg[3]))
    best=None
    for rr in range(0,8000,25):
        n=1 if rr==0 else max(8,int(2*math.pi*rr/25))
        cands=[]
        for k in range(n):
            x=round((t[0]+rr*math.cos(2*math.pi*k/n))/25)*25;y=round((t[1]+rr*math.sin(2*math.pi*k/n))/25)*25
            for r in (0,90,180,270):
                if isfree(bbox_at(d,x,y,r,M),reg): cands.append((x,y,r))
        if cands:
            def hp(c):
                s=0
                for (px,py,nn) in pins_at(d,*c):
                    ps=netpins.get(nn,[]) if nn not in POWER else []
                    if ps: s+=min(abs(px-a)+abs(py-b) for a,b,_ in ps)
                return s
            best=min(cands,key=hp);break
    if not best: fails.append(d);continue
    pos[d]=list(best);mark(bbox_at(d,*best,M));addpins(d)
print('moved',len(rest),'fails',fails)
bl=[(d,bbox_at(d,*pos[d],0)) for d in pos]
ov=[(bl[i][0],bl[j][0]) for i in range(len(bl)) for j in range(i+1,len(bl)) if bl[i][1][0]<bl[j][1][2]-1 and bl[j][1][0]<bl[i][1][2]-1 and bl[i][1][1]<bl[j][1][3]-1 and bl[j][1][1]<bl[i][1][3]-1]
print('overlaps',ov)
for hx,hy in HOLES:
    hit=[d for d,b in bl if b[0]<hx+197 and b[2]>hx-197 and b[1]<hy+197 and b[3]>hy-197]
    if hit: print('hole',hx,hy,hit)
json.dump(pos,open('plv2.json','w'));json.dump(HOLES,open('holesv2.json','w'))
HV2=HOLES
exec(open('rend4.py').read().split("if __name__")[0])
render({d:tuple(v) for d,v in pos.items()},W,H,'plv2.png',extra=[(NUCBOX[0],NUCBOX[1],NUCBOX[2],NUCBOX[3],'Nucleo-144'),(X0+2850,-4660,13750,-4250,'audio')],title='v2',holes=HV2)
