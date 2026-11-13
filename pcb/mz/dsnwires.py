import re,json,sys
t=open(sys.argv[1]).read();wr=t[t.index('(wiring'):]
LZ={'1':0,'2':1,'16':2,'TopLayer':0,'BottomLayer':1,'Inner2':2}
out=[]
for m in re.finditer(r'\(wire\(path (\S+) ([\d.]+) ([^)]*)\)\s*\(net "?([^\s")]+)"?\)',wr):
    L,w,c,n=m.groups()
    if L not in LZ: continue
    c=[float(v) for v in c.split()]
    out.append({'net':n,'w':float(w),'path':[(LZ[L],c[i],c[i+1]) for i in range(0,len(c),2)]})
for m in re.finditer(r'\(via \S+ (-?[\d.]+) (-?[\d.]+)\s*\(net "?([^\s")]+)"?\)',wr):
    x,y=float(m.group(1)),float(m.group(2))
    out.append({'net':m.group(3),'w':12,'path':[(0,x,y),(1,x,y)],'via':True})
json.dump(out,open(sys.argv[2],'w'));print(len(out))
