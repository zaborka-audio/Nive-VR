import json,sys
src=sys.argv[1]; dst=sys.argv[2]
d=json.load(open(src,encoding='utf8')); old=json.load(open('full4.json'))
c=[]
for o in d['comps']:
    b=o.get('bbox') or {}
    pins=[[str(p['PadNumber']),round(p['X'],1),round(p['Y'],1),p.get('Net') or ''] for p in o.get('pads',[])]
    r=round(o['r'])%360
    c.append([o['des'],round(o['x']),round(o['y']),r,o['layer'],o['fp'],o['id'],pins,[round(b.get('minX',0)),round(b.get('minY',0)),round(b.get('maxX',0)),round(b.get('maxY',0))]])
json.dump({'c':c,'free':old['free']},open(dst,'w'))
print(len(c))
