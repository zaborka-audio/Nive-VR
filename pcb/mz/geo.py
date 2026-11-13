import re,collections,math,numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
import os
G=float(os.environ.get('MZG','5'))
W,H=13850,9850
WIN=os.environ.get('MZWIN')  # x0,y0,x1,y1 in DSN coords
if WIN: OX,OY0,OX1,OY=map(float,WIN.split(','))
else: OX,OY0,OX1,OY=0,0,W,H
NX,NY=int((OX1-OX)/G)+1,int((OY-OY0)/G)+1
LAY=['TopLayer','BottomLayer','Inner2']; LNUM={'1':0,'2':1,'16':2}
def load(path):
    t=open(path).read()
    ps={}
    for m in re.finditer(r'\(padstack (\S+)((?:\s*\(shape\([^\n]*\)\))+)',t):
        sh={}
        for s in re.finditer(r'\(shape\((\w+) (\w+) ([^)]*)\)\)',m.group(2)):
            kind,lay,args=s.groups();a=[float(v) for v in args.split()]
            sh[lay]=(kind,a)
        ps[m.group(1)]=sh
    pins={m.group(2):(m.group(1),float(m.group(3)),float(m.group(4))) for m in re.finditer(r'\(pin (\S+) (\S+) (-?[\d.]+) (-?[\d.]+)\)',t)}
    nw=t[t.index('(network'):t.index('(wiring')]
    pinnet={}
    for m in re.finditer(r'\(net (\S+)\s*\(pins ([^)]*)\)',nw):
        for p in m.group(2).split(): pinnet[p.split('-',1)[1]]=m.group(1)
    wr=t[t.index('(wiring'):]
    wires=[];vias=[]
    for m in re.finditer(r'\(wire\(path (\S+) ([\d.]+) ([^)]*)\)\s*\(net (\S+)\)',wr):
        L,w,c,n=m.groups();c=[float(v) for v in c.split()]
        wires.append((n,L,float(w),[(c[i],c[i+1]) for i in range(0,len(c),2)]))
    for m in re.finditer(r'\(via (\S+) (-?[\d.]+) (-?[\d.]+)\s*\(net (\S+)\)',wr):
        vias.append((m.group(4),float(m.group(2)),float(m.group(3))))
    return ps,pins,pinnet,wires,vias
def c2g(x,y): return ((x-OX)/G, (OY-y)/G)  # image coords (row down)
def draw_pad(dr,sh,x,y):
    kind,a=sh
    if kind=='circle':
        r=a[0]/2/G;cx,cy=c2g(x+(a[1] if len(a)>1 else 0),y+(a[2] if len(a)>2 else 0))
        dr.ellipse([cx-r,cy-r,cx+r,cy+r],fill=1)
    else:
        a=a[1:];pts=[c2g(x+a[i],y+a[i+1]) for i in range(0,len(a)-1,2)]
        dr.polygon(pts,fill=1)
def draw_line(dr,p,q,w):
    a=c2g(*p);b=c2g(*q);r=w/2/G
    dr.line([a,b],fill=1,width=int(math.ceil(2*r))+1)
    dr.ellipse([a[0]-r,a[1]-r,a[0]+r,a[1]+r],fill=1);dr.ellipse([b[0]-r,b[1]-r,b[0]+r,b[1]+r],fill=1)
