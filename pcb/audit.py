import json,math,collections
exec(open('common4.py').read())
P=json.load(open('pl9.json'))
P['CN7']=[13372,-6690,270];P['CN10']=[13372,-8100,270];P['CN8']=[11372,-6850,270];P['CN9']=[11372,-8100,270]
def rot(dx,dy,r):
    a=math.radians(r);return dx*math.cos(a)-dy*math.sin(a),dx*math.sin(a)+dy*math.cos(a)
SENS={'C95','C96','C97','C98','C99','C100','D13','D14','D15','D16','D17','D18','R187','R188','R189','R190','R191'}
def grp(d):
    p=pages.get(d,'?')
    if d in('J5','J6','J7','J8'): return 'XLR'
    if d in('J1','J12'): return d
    if d.startswith('CN'): return 'NUC'
    if d in('U1','U2','U3','C1','C2','C3'): return 'DRV'
    if d in('J2','JP2') or p in('p4','p5'): return 'REL'
    if p=='p13': return 'SENS' if d in SENS else 'PWR'
    return {'p1':'PWR','p2':'PWR','p6':'SUM','p12':'ADC','p11':'LM','p8':'LOG','p9':'LOG','p10':'LOG'}.get(p,'PWR')
pins=[]  # (grp,des,net,x,y)
bb=collections.defaultdict(lambda:[1e9,1e9,-1e9,-1e9]);area=collections.Counter()
for d,c in C.items():
    if d not in P: continue
    x,y,r=P[d];g=grp(d);dr=r-c['r']
    b=c['bb'];w,h=b[2]-b[0],b[3]-b[1];area[g]+=w*h
    for n,px,py,net in c['pins']:
        dx,dy=rot(px-c['x'],py-c['y'],dr);X,Y=x+dx,y+dy
        pins.append((g,d,net,X,Y))
        B=bb[g];B[0]=min(B[0],X);B[1]=min(B[1],Y);B[2]=max(B[2],X);B[3]=max(B[3],Y)
if __name__=='__main__':
    for g in bb: print(g,[round(v) for v in bb[g]],'parts area cm2 %.0f'%(area[g]*6.4516e-6), 'bbox cm2 %.0f'%((bb[g][2]-bb[g][0])*(bb[g][3]-bb[g][1])*6.4516e-6))
