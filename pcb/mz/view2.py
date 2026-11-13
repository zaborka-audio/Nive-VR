import sys,os,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from geo import load
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
ps,pins,pinnet,wires,vias=load(sys.argv[1]);R=json.load(open(sys.argv[2]));out=sys.argv[3]
win=[float(v) for v in sys.argv[4].split(',')] if len(sys.argv)>4 else [0,0,13850,9850]
hl=set(sys.argv[5].split(',')) if len(sys.argv)>5 else set()
fig,ax=plt.subplots(figsize=(16,16*(win[3]-win[1])/(win[2]-win[0])))
for pid,(pst,x,y) in pins.items():
    if not(win[0]-100<x<win[2]+100 and win[1]-100<y<win[3]+100): continue
    sh=ps[pst].get('TopLayer');d=sh[1][0] if sh[0]=='circle' else 60
    n=pinnet.get(pid,'')
    ax.add_patch(plt.Circle((x,y),d/2,color='red' if n in hl else '#999'))
cols=['#d33','#33d','#3a3']
for r in R:
    p=r['path']
    for a,b in zip(p,p[1:]):
        if a[0]==b[0]: ax.plot([a[1],b[1]],[a[2],b[2]],color=cols[a[0]],lw=r.get('w',12)/12*0.8)
        else: ax.add_patch(plt.Circle((a[1],a[2]),16,color='k'))
ax.set_xlim(win[0],win[2]);ax.set_ylim(win[1],win[3]);ax.set_aspect('equal')
plt.savefig(out,dpi=90,bbox_inches='tight')
