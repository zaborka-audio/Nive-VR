# mkfr2.py base_fr.dsn model.json out.dsn
# Rebuilds the wiring section of a FreeRouting DSN from a model json (DSN coords):
#  - drops the fake (type fix) Inner2 conduction polygons (pours were deleted on the board)
#  - signal wires/vias touching the Nucleo zone -> (type route) so FreeRouting may rip them
#  - everything else -> (type protect)
import re,json,sys
src,model,dst=sys.argv[1:4]
t=open(src).read()
M=json.load(open(model))
LN={0:'TopLayer',1:'BottomLayer',2:'Inner2',3:'Inner1'}
power=set('+16V -16V VL VR P12 HV50 PH48 +5V P16_S P16_F N16_S N16_F VL_S VL_F CH_VL CH_N16 CH_P16 IP_C IN_C IL_C P17 N17A N17L VIN_F SW1 SW2 SW3 SW4 VIN_RAW VIN24 NUC_VIN GND GNDA +3V3'.split())
# zone around CN7-CN10 (EasyEDA x 6425..8425, y -6180..-9350) + ~700 mil margin, DSN y = y_ee + 9850
ZX=(5700,9150);ZY=(9850-9850+0,9850-5450)
inz=lambda x,y:ZX[0]<=x<=ZX[1] and ZY[0]<=y<=ZY[1]
q=lambda n:'"%s"'%n if re.search(r'[^A-Za-z0-9_+\-]',n) else n
out=[];nr=0
for o in M:
    n=o['net'];P=o['path']
    free=n not in power and any(inz(p[1],p[2]) for p in P)
    ty='route' if free else 'protect'
    if free: nr+=1
    if o.get('via'):
        out.append('    (via via0 %g %g\n      (net %s)\n      (type %s)\n    )\n'%(P[0][1],P[0][2],q(n),ty))
    else:
        # split on layer change (shouldn't happen in model paths, but be safe)
        segs=[[P[0]]]
        for p in P[1:]:
            if p[0]!=segs[-1][-1][0]:
                out.append('    (via via0 %g %g\n      (net %s)\n      (type %s)\n    )\n'%(p[1],p[2],q(n),ty))
                segs.append([p]);continue
            segs[-1].append(p)
        for seg in segs:
            if len(seg)<2: continue
            c=' '.join('%g %g'%(p[1],p[2]) for p in seg)
            out.append('    (wire(path %s %g %s )\n      (net %s)\n      (type %s)\n    )\n'%(LN[seg[0][0]],o['w'],c,q(n),ty))
i=t.index('(wiring\n')+len('(wiring\n')
j=t.index('\n  )',i)
t=t[:i]+''.join(out)+t[j+1:]
open(dst,'w').write(t)
print('items',len(out),'route-type',nr)
