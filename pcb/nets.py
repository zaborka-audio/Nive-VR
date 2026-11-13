import sys,collections
sys.path.insert(0,'mz')
from geo import load
ps,pins,pinnet,wires,vias=load('v2.dsn')
cnt=collections.Counter(pinnet.values())
smd=collections.Counter()
for pid,(pst,x,y) in pins.items():
    n=pinnet.get(pid)
    if n and 'Inner1' not in ps[pst]: smd[n]+=1
print('nets',len(cnt),'pins',sum(cnt.values()))
print('multi-pin nets',sum(1 for v in cnt.values() if v>1))
for n,c in cnt.most_common(40): print(n,c,'smd',smd[n])
print('padstack layers sample',{k:list(v) for k,v in list(ps.items())[:3]})
print('smd total',sum(smd.values()), [n for n in smd if n in('GND','GNDA')], smd['GND'],smd['GNDA'])
