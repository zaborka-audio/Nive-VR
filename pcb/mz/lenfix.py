# lenfix.py in.json board.json out.json : replace too-short new segments A-B by A-X with X on the neighbour
# segment at B (or B-X with X on neighbour at A) so that every new segment is >= MINL long.
import sys,os,json,math
R=json.load(open(sys.argv[1]));BRD=json.load(open(sys.argv[2]))
MINL=float(os.environ.get('MINL','12.5'))
def key(n,z,a,b):
    e=sorted([(round(a[0]),round(a[1])),(round(b[0]),round(b[1]))]);return (n,z,e[0],e[1])
onb=set()
for r in BRD:
    p=r['path']
    for a,b in zip(p,p[1:]):
        if a[0]==b[0]: onb.add(key(r['net'],a[0],(a[1],a[2]),(b[1],b[2])))
segs=[r for r in R if not r.get('via')]
L=lambda a,b:math.hypot(b[1]-a[1],b[2]-a[2])
same=lambda p,q:abs(p[1]-q[1])<0.05 and abs(p[2]-q[2])<0.05
fixed=0;drop=0;left=[]
for r in segs:
    a,b=r['path']
    if L(a,b)>=MINL or key(r['net'],a[0],(a[1],a[2]),(b[1],b[2])) in onb: continue
    if L(a,b)<1.0:
        r['_del']=1;drop+=1;continue
    done=False
    for A,B in ((a,b),(b,a)):
        for q in segs:
            if q is r or q['net']!=r['net'] or q.get('_del') or q['path'][0][0]!=a[0]: continue
            q0,q1=q['path']
            if same(q0,B): far=q1
            elif same(q1,B): far=q0
            else: continue
            lq=L(B,far)
            if lq<1: continue
            # find t in (0,lq] with |A - (B + t*u)| >= MINL
            ux,uy=(far[1]-B[1])/lq,(far[2]-B[2])/lq
            t=None
            for k in range(1,int(lq)+1):
                X=(B[1]+ux*k,B[2]+uy*k)
                if math.hypot(X[0]-A[1],X[1]-A[2])>=MINL: t=k;break
            if t is None: continue
            X=[a[0],round(B[1]+ux*t,2),round(B[2]+uy*t,2)]
            r['path']=[list(A),X];fixed+=1;done=True;break
        if done: break
    if not done: left.append((r['net'],[tuple(round(v,1) for v in p) for p in r['path']]))
out=[r for r in R if not r.get('_del')]
json.dump(out,open(sys.argv[3],'w'));print('fixed',fixed,'dropped',drop,'left',len(left),left[:8])
