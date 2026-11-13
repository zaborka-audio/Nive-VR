import sys,json
exec(open('common4.py').read())
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.patches as pa
def render(pos,W,H,out,extra=None,title='',holes=()):
    cols={'p1':'#f4a','p2':'#f88','p3':'#8cf','p4':'#fc8','p5':'#fb6','p6':'#9d9','p7':'#bbb','p8':'#c9f','p9':'#dbf','p10':'#b8e','p11':'#a7d','p12':'#fd9','p13':'#ec9','?':'#eee'}
    fig,ax=plt.subplots(figsize=(14,12))
    ax.add_patch(pa.Rectangle((0,-H),W,H,fill=False,lw=2))
    for d,c in C.items():
        x,y=pos.get(d,(c['x'],c['y']))[:2]; dx=x-c['x']; dy=y-c['y']; b=c['bb']
        r=pos.get(d,(0,0,None))[2] if d in pos and len(pos[d])>2 else None
        x0,y0,x1,y1=b[0]+dx,b[1]+dy,b[2]+dx,b[3]+dy
        if r is not None and (r-c['r'])%180==90:
            cx,cy=(x0+x1)/2,(y0+y1)/2; w,h=x1-x0,y1-y0; x0,x1,y0,y1=cx-h/2,cx+h/2,cy-w/2,cy+w/2
        ax.add_patch(pa.Rectangle((x0,y0),x1-x0,y1-y0,fc=cols.get(pages.get(d,'?'),'#eee'),ec='k',lw=0.3))
        ax.text((x0+x1)/2,(y0+y1)/2,d,fontsize=4 if d[0] in 'RCD' else 6,ha='center',va='center')
    if extra:
        for (x0,y0,x1,y1,lab) in extra:
            ax.add_patch(pa.Rectangle((x0,y0),x1-x0,y1-y0,fill=False,ec='b',ls='--',lw=0.8)); ax.text(x0+30,y1-80,lab,fontsize=7,color='b')
    for hx,hy in holes: ax.add_patch(pa.Circle((hx,hy),126,fc='k'))
    ax.set_xlim(-300,W+300); ax.set_ylim(-H-1500,500); ax.set_aspect('equal'); ax.set_title(title)
    plt.savefig(out,dpi=110,bbox_inches='tight'); plt.close()
if __name__=='__main__':
    render({},13386,10827,'now4.png')
