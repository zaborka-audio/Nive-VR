# ses2json.py in.ses out.json -> list of {'net','w','path':[(z,x,y)...]} (DSN coords, mil) + vias as 2-point layer change
import re,json,sys
t=open(sys.argv[1]).read()
LZ={'TopLayer':0,'BottomLayer':1,'Inner2':2,'Inner1':3}
out=[];bad=0
no=t[t.index('(network_out'):]
for m in re.finditer(r'\(net "?([^\s"]+)"?\n(.*?)\n      \)\n',no,re.S):
    n=m.group(1);body=m.group(2)
    for w in re.finditer(r'\(path (\S+) (\d+)\s+([-\d\s]+)\)',body):
        L=w.group(1);z=LZ[L]
        if z==3: bad+=1;continue
        c=[int(v)/1000 for v in w.group(3).split()]
        out.append({'net':n,'w':int(w.group(2))/1000,'path':[(z,c[i],c[i+1]) for i in range(0,len(c),2)]})
    for v in re.finditer(r'\(via \S+ (-?\d+) (-?\d+)',body):
        x,y=int(v.group(1))/1000,int(v.group(2))/1000
        out.append({'net':n,'w':12,'path':[(0,x,y),(1,x,y)],'via':True})
json.dump(out,open(sys.argv[2],'w'))
print('items',len(out),'vias',sum(1 for o in out if o.get('via')),'inner1 paths',bad)
