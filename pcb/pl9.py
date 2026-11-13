import json,math
exec(open('common4.py').read())
W,H=13850,9850
def rotv(dx,dy,r):
    r%=360
    return {0:(dx,dy),90:(-dy,dx),180:(-dx,-dy),270:(dy,-dx)}[r]
pos={}  # d -> [x,y,rot]
def relbb(d):
    c=C[d];b=c['bb'];return (b[0]-c['x'],b[1]-c['y'],b[2]-c['x'],b[3]-c['y'])
def bbox_at(d,x,y,r,m=0):
    c=C[d]; x0,y0,x1,y1=relbb(d); dr=(r-c['r'])%360
    pts=[rotv(a,b,dr) for a in (x0,x1) for b in (y0,y1)]
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    return (x+min(xs)-m,y+min(ys)-m,x+max(xs)+m,y+max(ys)+m)
def pins_at(d,x,y,r):
    c=C[d]; dr=(r-c['r'])%360; out=[]
    for p in c['pins']:
        a,b=rotv(p[1]-c['x'],p[2]-c['y'],dr); out.append((x+a,y+b,p[3]))
    return out
def rigid(ds,dx,dy):
    for d in ds: pos[d]=[C[d]['x']+dx,C[d]['y']+dy,C[d]['r']]
def rigid_rot(ds,cx_new,cy_new,ang=90):
    b=gbb(ds); cx=(b[0]+b[2])/2; cy=(b[1]+b[3])/2
    for d in ds:
        a,bb=rotv(C[d]['x']-cx,C[d]['y']-cy,ang); pos[d]=[cx_new+a,cy_new+bb,(C[d]['r']+ang)%360]
def gb(ds): 
    bs=[bbox_at(d,*pos[d]) for d in ds]; return (min(b[0] for b in bs),min(b[1] for b in bs),max(b[2] for b in bs),max(b[3] for b in bs))
def place_box(ds,x0,ytop):
    b=gbb(ds); rigid(ds,x0-b[0],ytop-b[3])
P=lambda k:[d for d in PG[k]]
# ---------- groups
REL=['K%d'%i for i in range(1,23)]+['R%d'%i for i in range(1,17)]+['J2','JP2']
LIN=[d for d in C if C[d]['x']<4900 and -9500<C[d]['y']<-7400 and pages.get(d) in('p2',)]
SW=[d for d in C if C[d]['x']>=5000 and C[d]['y']<=-6900 and pages.get(d) in('p1','p2')]
CP=[d for d in C if C[d]['x']<4800 and -7300<C[d]['y']<-5600 and pages.get(d)=='p13']
SUM=[d for d in PG['p6'] if d not in('C20','C21','C36','C37')]
ADC=[d for d in C if 8400<C[d]['x']<10600 and -9500<C[d]['y']<-5400 and pages.get(d) in('p12','p13')]
NUC=['CN7','CN8','CN9','CN10']
# relays + J2: relays left edge at 4600
b=gbb(['K%d'%i for i in range(1,23)]); rigid(REL,4600-b[0],0)
for d in ['K12','K21','K22','K17','R10','R12','R15','R16']: pos[d][1]-=700; pos[d][0]+=150
BX=4361
pos['J12']=[BX+2441,-3425,C['J12']['r']]
# J1 top aligned like J2
pos['J1']=[11100,C['J1']['y'],C['J1']['r']]
# left column
place_box(CP,150,-250)
place_box(LIN,150,-2600)
b=gbb(SW); rigid(SW,150-b[0],-H-6-b[1])
# middle: summing below relays
rb=gb(['K%d'%i for i in range(1,23)])
place_box(SUM,4650,rb[1]-180)
sb=gb(SUM)
# ADC rotated 90 in middle under summing
ab=gbb(ADC); w,h=ab[3]-ab[1],ab[2]-ab[0]
rigid_rot(ADC,4650+w/2,sb[1]-250-h/2,90)
# XLR rear
for i,j in enumerate(['J5','J6','J7','J8']):
    bb=relbb(j); x=4650+i*1110-bb[0]; y=-H-6-bb[1]-((C['J5']['bb'][1]-C[j]['bb'][1]) if 0 else 0)
    pos[j]=[x,C[j]['y']+(-H-114-C['J5']['bb'][1]) ,C[j]['r']]
# Nucleo: body x [W-100-2756, W-100], bottom at -H+50
NB=[10570,-10777]; dx=(W-100-2756)-NB[0]; dy=(-H+50)-NB[1]
rigid(NUC,dx,dy); NUCBOX=(W-100-2756,-H+50,W-100,-H+50+5250)
# logic columns
X0=9620; PIT=790
for k in range(5):
    x=X0+k*PIT
    pos['U%d'%(31+k)]=[x,-1750,90]
    pos['U%d'%(36+k)]=[x,-3800,90]
    s1,s2,pd=['RN%d'%(1+2*k),'RN%d'%(2+2*k),'RN%d'%(11+k)]
    pos[s1]=[x-200,-2780,90]; pos[s2]=[x,-2780,90]; pos[pd]=[x+200,-2780,90]
# drivers and LM339 left of Nucleo
for i,u in enumerate(['U1','U2','U3']): pos[u]=[8930,-5100-i*1150,90]
for i,u in enumerate(['U41','U42','U43','U44']): pos[u]=[9750,-5000-i*1030,90]
json.dump(pos,open('pl9_anchor.json','w'))
print(len(pos),'anchored; NUCBOX',NUCBOX)
