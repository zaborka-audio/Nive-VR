import json,collections
exec(open('common4.py').read())
src=open('pl9.py').read(); exec(src[:src.index('P=lambda')])
pos=json.load(open('plv2.json'))
W={}
for n in ['VIN_RAW','VIN_F']: W[n]=40
for n in ['VIN24','SW1','SW2','SW3','SW4']: W[n]=30
for n in ['N17A','N17L','P17','+16V','-16V','VL','XL','XN','XP','BL','BN','BP']: W[n]=25
for n in ['+5V','NUC_VIN']: W[n]=20
for n in ['+3V3','HV50','PH48','P12','VR']: W[n]=15
pinsof=collections.defaultdict(list)
for d in pos:
    for x,y,n in pins_at(d,*pos[d]):
        if n: pinsof[n].append((x,y,d))
order=[]
def add(n):
    if n and n not in order and n not in('GND','GNDA') and len(pinsof[n])>1: order.append(n)
# (a) Nucleo: outer columns first
outer=[];inner=[]
for d,cx,sgn in (('CN8',6425,-1),('CN9',6425,-1),('CN7',8425,1),('CN10',8425,1)):
    for x,y,n in pins_at(d,*pos[d]):
        (outer if (x-cx)*sgn>0 else inner).append((n,y))
for n,y in sorted(outer,key=lambda t:t[1]): 
    if n not in W: add(n)
for n,y in sorted(inner,key=lambda t:t[1]):
    if n not in W: add(n)
for n,_ in outer+inner: add(n)
na=len(order)
# J12 bus
for x,y,n in pins_at('J12',*pos['J12']): add(n)
nb=len(order)
# (b) drivers -> relays
for d in ('U1','U2','U3'):
    for x,y,n in pins_at(d,*pos[d]): add(n)
nc=len(order)
# (c) summing nodes and audio
for n in sorted(pinsof):
    if n.startswith('SUM'): add(n)
for d in ('J5','J6','J7','J8'):
    for x,y,n in pins_at(d,*pos[d]): add(n)
nd=len(order)
# (d) power, widest first
for n in sorted(W,key=lambda n:-W[n]): add(n)
ne=len(order)
# (e) rest by HPWL
def hp(n):
    xs=[p[0] for p in pinsof[n]];ys=[p[1] for p in pinsof[n]];return max(xs)-min(xs)+max(ys)-min(ys)
for n in sorted(pinsof,key=hp): add(n)
print('a',na,'J12',nb-na,'b',nc-nb,'c',nd-nc,'pwr',ne-nd,'rest',len(order)-ne,'total',len(order))
with open('order_v2.txt','w') as f:
    for n in order: f.write(n+(' %g'%W[n] if n in W else '')+'\n')
# GND / GNDA last (pins outside own pour)
with open('order_v2.txt','a') as f: f.write('GND\nGNDA\n')
