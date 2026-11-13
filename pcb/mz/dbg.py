import sys,os
src=open('mz/route.py').read().split('for n in targets:')[0]
sys.argv=['x','ee15.dsn','CH_A5','/dev/null']
exec(src)
n='CH_A5';nid=NID[n]
for name,(x,y) in [('J1_A19',(11350,9850-245)),('R149_1',(10875,9850-3803))]:
    cx,cy=int(round((x-OX)/G)),int(round((OY-y)/G))
    for z in range(3):
        ob=(lab[z]!=0)&(lab[z]!=nid)
        d=ndimage.distance_transform_edt(~ob)*G
        fr=(d>=TR)
        r=int(70/G)
        sub=fr[cy-r:cy+r,cx-r:cx+r]; own=(lab[z]==nid)[cy-r:cy+r,cx-r:cx+r]
        # free cells adjacent to own copper
        adj=ndimage.binary_dilation(own)&sub&~own
        print(name,z,'own',own.sum(),'free',sub.sum(),'adjfree',adj.sum(), 'maxd',round(float(d[cy-r:cy+r,cx-r:cx+r][~own].max()),1))
