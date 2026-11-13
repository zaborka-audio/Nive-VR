import sys,os,numpy as np
sys.path.insert(0,'mz')
from geo import *
from PIL import Image,ImageDraw
ps,pins,pinnet,wires,vias=load(os.environ.get('DSN','ee14.dsn'))
net=sys.argv[1];x0,y0,x1,y1=map(float,sys.argv[2:6])  # EE coords mils
S=2.0 # px per... scale: 1px = 2.5mil
sc=0.4
def P(x,y): return ((x-x0)*sc,(y1-(y))*sc)  # y in EE (neg)
Wd,Hd=int((x1-x0)*sc),int((y1-y0)*sc)
img=Image.new('RGB',(Wd,Hd),(0,0,0));dr=ImageDraw.Draw(img,'RGBA')
col={'1':(255,0,0,150),'2':(0,0,255,150),'16':(0,200,0,150)}
for n,L,w,pts in wires:
    if L not in col: continue
    c=col[L] if n!=net else (255,255,0,255)
    dr.line([P(x,y-9850) for x,y in pts],fill=c,width=max(1,int(w*sc)))
for pid,(pst,x,y) in pins.items():
    sh=ps[pst].get('TopLayer')
    if not sh: continue
    r=(sh[1][0]/2 if sh[0]=='circle' else max(abs(v) for v in sh[1][1:]))*sc
    X,Yy=P(x,y-9850); c=(255,255,0,255) if pinnet.get(pid)==net else (160,160,160,200)
    dr.ellipse([X-r,Yy-r,X+r,Yy+r],outline=c,width=2)
for n,x,y in vias:
    X,Yy=P(x,y-9850);r=16*sc;dr.ellipse([X-r,Yy-r,X+r,Yy+r],fill=(200,200,200,255) if n!=net else (255,255,0,255))
img.save(sys.argv[6]);print(img.size)
