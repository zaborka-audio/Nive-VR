import re,sys
src,dst=sys.argv[1:3]
t=open(src).read()
LN={'1':'TopLayer','2':'BottomLayer','15':'Inner1','16':'Inner2'}
t=re.sub(r"\(wire\(path (\d+) ",lambda m:"(wire(path %s "%LN[m.group(1)],t)
t=t.replace("(layer Inner1\n      (type signal)","(layer Inner1\n      (type power)")
H=9850
def pts(P): return ' '.join('%g %g'%(P[i],P[i+1]+H) for i in range(0,len(P),2))+' %g %g'%(P[0],P[1]+H)
A=[4470,-15,9200,-15,9200,-4250,5980,-4250,5980,-6380,4470,-6380]
B1=[8880,-8500,10935,-8500,10935,-9835,8880,-9835]
B2=[11295,-8500,13560,-8500,13560,-9835,11295,-9835]
G=[15,-15,4470,-15,4470,-6380,5980,-6380,5980,-4250,9200,-4250,9200,-15,13835,-15,13835,-9835,13560,-9835,13560,-8500,11295,-8500,11295,-9835,10935,-9835,10935,-8500,8880,-8500,8880,-9835,15,-9835]
planes=''.join('    (plane %s (polygon Inner1 0 %s))\n'%(n,pts(P)) for n,P in (('GND',G),('GNDA',A),('GNDA',B1),('GNDA',B2)))
i=t.index("  )\n\n  (placement");t=t[:i]+planes+t[i:]
VL=[9330,-1150,13050,-1150,13050,-7050,9450,-7050,9450,-4250,9330,-4250]
VIN=[4950,-600,8950,-600,8950,-3950,4950,-3950]
area=lambda n,P:'    (wire (polygon Inner2 0 %s)\n      (net %s)\n      (type fix)\n    )\n'%(pts(P),n)
i=t.index('(wiring\n')+len('(wiring\n');t=t[:i]+area('VL',VL)+area('VIN24',VIN)+t[i:]
power=['+16V','-16V','VL','VR','P12','HV50','PH48','+5V','P16_S','P16_F','N16_S','N16_F','VL_S','VL_F','CH_VL','CH_N16','CH_P16','IP_C','IN_C','IL_C']
phi=['P17','N17A','N17L','VIN_F','SW1','SW2','SW3','SW4','VIN_RAW']
W={**{n:24 for n in power},**{n:32 for n in phi},'VIN24':30,'NUC_VIN':20}
nets=set(re.findall(r"\n    \(net \"?([^\s\"]+)\"?\n",t))
i=t.index("    (class  ''");j=t.index("  )\n\n  (wiring")
cls=''.join("    (class w%d %s\n      (circuit\n        (use_via via0)\n      )\n      (rule\n        (width %d)\n        (clearance 10)\n      )\n    )\n"%(w,' '.join(n for n in W if W[n]==w and n in nets),w) for w in sorted(set(W.values())))
t=t[:i]+cls+t[j:]
t=t.replace('(clearance 9.84)','(clearance 10)').replace('(rule(clear 9.89','(rule(clear 10')
open(dst,'w').write(t)
print('ok',len(re.findall(r'\(wire\(path (TopLayer|BottomLayer|Inner2|Inner1) ',t)),'wires', len(re.findall(r'\(wire\(path \d+ ',t)),'numeric left')
