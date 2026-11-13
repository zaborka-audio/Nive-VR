import json,sys
src,rj,dst=sys.argv[1:4];H=9850
import subprocess
d=json.load(open(rj+'.ee.json'))
t=open(src).read()
add=''.join('    (wire(path %d 12 %s %s %s %s )\n      (net %s)\n      (type protect)\n    )\n'%(L,x1,y1+H,x2,y2+H,n) for n,L,x1,y1,x2,y2 in d['lines'])
add+=''.join('    (via via0 %s %s\n      (net %s)\n      (type protect)\n    )\n'%(x,y+H,n) for n,x,y in d['vias'])
i=t.index('(wiring')+len('(wiring\n');open(dst,'w').write(t[:i]+add+t[i:])
