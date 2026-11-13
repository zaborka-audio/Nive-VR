import sys,json
sys.path.insert(0,'mz')
from geo import load
ps,pins,pinnet,wires,vias=load('v2.dsn')
def inpoly(x,y,P):
    pts=[(P[i],P[i+1]) for i in range(0,len(P)-1,2)]
    c=False
    for (x1,y1),(x2,y2) in zip(pts,pts[1:]+pts[:1]):
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
A=[4470,-15,9200,-15,9200,-4250,5980,-4250,5980,-6380,4470,-6380]
B1=[8880,-8500,10935,-8500,10935,-9835,8880,-9835]
B2=[11295,-8500,13560,-8500,13560,-9835,11295,-9835]
bad=[]
for pid,(pst,x,y) in pins.items():
    n=pinnet.get(pid);Y=y-9850
    ga=any(inpoly(x,Y,P) for P in (A,B1,B2))
    if n=='GND' and ga: bad.append((n,x,Y))
    if n=='GNDA' and not ga: bad.append((n,x,Y))
print(len(bad),bad)
