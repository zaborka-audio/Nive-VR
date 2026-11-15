# collapse.py dsn in.json board.json out.json : merge track vertices closer than MINL (default 12) on segments not on board
import sys,os,json,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from geo import load,LAY
ps,pins,pinnet,_,_=load(sys.argv[1]);R=json.load(open(sys.argv[2]));BRD=json.load(open(sys.argv[3]))
MINL=float(os.environ.get('MINL','12'))
def key(n,z,a,b):
    e=sorted([(round(a[0]),round(a[1])),(round(b[0]),round(b[1]))]);return (n,z,e[0],e[1])
onb=set()
for r in BRD:
    p=r['path']
    for a,b in zip(p,p[1:]):
        if a[0]==b[0]: onb.add(key(r['net'],a[0],(a[1],a[2]),(b[1],b[2])))
# anchors: pad centres and via centres per net
anch={}
for pid,(pst,x,y) in pins.items():
    n=pinnet.get(pid)
    if n: anch.setdefault(n,[]).append((x,y))
for r in R:
    if r.get('via'): anch.setdefault(r['net'],[]).append((r['path'][0][1],r['path'][0][2]))
isanch=lambda n,x,y:any(abs(x-a)<0.6 and abs(y-b)<0.6 for a,b in anch.get(n,[]))
deg={}
for r in R:
    if r.get('via'): continue
    for e in r['path']: k=(r['net'],e[0],round(e[1],2),round(e[2],2));deg[k]=deg.get(k,0)+1
n_col=0
for it in range(50):
    ch=False
    for i,r in enumerate(R):
        if r.get('via') or r.get('_del'): continue
        a,b=r['path'];n=r['net'];z=a[0]
        L=math.hypot(b[1]-a[1],b[2]-a[2])
        if L>=MINL or key(n,z,(a[1],a[2]),(b[1],b[2])) in onb: continue
        # keep anchored vertex, else the one with higher degree
        ka=isanch(n,a[1],a[2]);kb=isanch(n,b[1],b[2])
        if ka and kb and L>0.01:
            continue
        if ka: tx,ty=a[1],a[2]
        elif kb: tx,ty=b[1],b[2]
        else: tx,ty=round((a[1]+b[1])/2,2),round((a[2]+b[2])/2,2)
        olds=[(a[1],a[2]),(b[1],b[2])]
        for rr in R:
            if rr['net']!=n or rr.get('via') or rr.get('_del'): continue
            for p in rr['path']:
                if p[0]==z and any(abs(p[1]-ox)<0.01 and abs(p[2]-oy)<0.01 for ox,oy in olds): p[1],p[2]=tx,ty
        r['_del']=1;n_col+=1;ch=True
    if not ch: break
out=[r for r in R if not r.get('_del') and (r.get('via') or (r['path'][0][1],r['path'][0][2])!=(r['path'][1][1],r['path'][1][2]))]
json.dump(out,open(sys.argv[4],'w'));print('collapsed',n_col)
left=[(r['net'],[tuple(round(v,1) for v in p) for p in r['path']]) for r in out if not r.get('via') and math.hypot(r['path'][1][1]-r['path'][0][1],r['path'][1][2]-r['path'][0][2])<MINL and key(r['net'],r['path'][0][0],(r['path'][0][1],r['path'][0][2]),(r['path'][1][1],r['path'][1][2])) not in onb]
print('short left',len(left),left[:10])
