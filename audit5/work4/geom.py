import sys,json,math,collections,pickle
sys.path.insert(0,'work4')
from model import *
from shapely.geometry import Point,Polygon,LineString,MultiPolygon
from shapely.ops import unary_union
from shapely import STRtree
import shapely
LAYMAP={'TopLayer':'1','BottomLayer':'2','Inner1':'15','Inner2':'16'}
LAYERS=['1','2','15','16']
YOFF=9850.0
def arc_pts(p0,ang,p1,sign=1,step=3.0):
    # arc from p0 to p1 sweeping 'ang' degrees
    x0,y0=p0;x1,y1=p1
    a=math.radians(ang)
    ch=math.hypot(x1-x0,y1-y0)
    if ch<1e-9 or abs(a)<1e-9: return [p1]
    r=ch/(2*math.sin(abs(a)/2))
    # center: midpoint + perpendicular * h
    mx,my=(x0+x1)/2,(y0+y1)/2
    h=r*math.cos(abs(a)/2)   # signed for >180
    ux,uy=(x1-x0)/ch,(y1-y0)/ch
    s=sign*(1 if a>0 else -1)
    cx,cy=mx - s*uy*h, my + s*ux*h   # center to the left for CCW (s>0)
    a0=math.atan2(y0-cy,x0-cx)
    n=max(2,int(abs(ang)/step)+1)
    pts=[]
    for i in range(1,n+1):
        t=a0+s*abs(a)*i/n
        pts.append((cx+r*math.cos(t),cy+r*math.sin(t)))
    pts[-1]=p1
    return pts,(cx,cy,r)
def path_pts(sub,sign=1,centers=None,scale=10.0):
    # returns list of points in DSN coords
    pts=[(sub[0],sub[1])]
    i=2;mode='L'
    while i<len(sub):
        t=sub[i]
        if isinstance(t,str): mode=t;i+=1;continue
        if mode=='L':
            pts.append((sub[i],sub[i+1]));i+=2
        elif mode=='ARC':
            ang=sub[i];p1=(sub[i+1],sub[i+2]);i+=3
            r=arc_pts(pts[-1],ang,p1,sign)
            if isinstance(r,tuple):
                ap,c=r
                if centers is not None: centers.append((c[0]*scale,c[1]*scale+YOFF,c[2]*scale,ang))
                pts+=ap
            else: pts+=r
        else: raise Exception(mode)
    return [(x*scale,y*scale+YOFF) for x,y in pts]
def pad_geom(shape,x,y):
    if shape[0]=='circle':
        d=float(shape[2]); ox=float(shape[3]) if len(shape)>3 else 0; oy=float(shape[4]) if len(shape)>4 else 0
        return Point(x+ox,y+oy).buffer(d/2,32)
    if shape[0]=='polygon':
        ap=float(shape[2]); c=[float(v) for v in shape[3:]]
        pts=[(x+c[i],y+c[i+1]) for i in range(0,len(c),2)]
        g=Polygon(pts)
        if not g.is_valid: g=g.buffer(0)
        return g
    raise Exception(shape[0])
