import sys; sys.path.insert(0,'work4')
from geom import *
D=pickle.load(open('work4/conn.pkl','rb')); items=D['items'];touch=D['touch']
pours=[(i,it) for i,it in enumerate(items) if it['kind']=='pour']
main=[it for i,it in pours if it['ref'][0]=='GND_L15' and it['geom'].area>1e6][0]['geom']
for i,it in pours:
    g=it['geom']
    if g.area<5000:
        b=g.bounds; print('blob bounds',[round(b[0],1),round(b[1]-YOFF,1),round(b[2],1),round(b[3]-YOFF,1)],'dist to main GND pour %.3f'%g.distance(main),'npts',len(g.exterior.coords),'holes',len(g.interiors))
        print('   coords',[(round(x,1),round(y-YOFF,1)) for x,y in list(g.exterior.coords)[:12]])
for pt in ((6530,-7050),(8305,-6575)):
    P=Point(pt[0],pt[1]+YOFF)
    print(pt,'via centre to main pour dist %.2f'%main.distance(P), 'spokes near:',[ (round(items[i]['geom'].distance(P),1)) for i,it in enumerate(items) if it['kind']=='spoke' and items[i]['geom'].distance(P)<40])
j=json.load(open('pcb_pours4.json',encoding='utf8'))
for p in j['poured']:
    for f in p['PourFills']:
        if f.get('fill') and len(f['path']['complexPolygon'])==1: print({k:v for k,v in f.items() if k!='path'}, str(f['path']['complexPolygon'])[:300])
