import json,sys
O=json.load(open('../k8/vrb_k8dump.json',encoding='utf-8'))
def fl(l): return [v for s in l for v in s] if isinstance(l[0],list) else l
def near(P,pts,R=1):
  out=[]
  for w in P['wires']:
    f=fl(w[1]);ws=list(zip(f[::2],f[1::2]))
    if any(abs(a-x)<=R and abs(b-y)<=R for a,b in ws for x,y in pts): out.append((w[0],w[2],ws))
  return out
def flags(P,pts,R=1):
  return [(c['id'],c['t'],c.get('net'),c['x'],c['y'],c['r']) for c in P['comps'] if c['t']!='part' and any(abs(c['x']-x)<=R and abs(c['y']-y)<=R for x,y in pts)]
def show(page,des,pins=None):
  P=[v for k,v in O.items() if k.startswith(page+' ')][0]
  for c in P['comps']:
    if c.get('d') in des:
      ps=[p for p in c['pins'] if not pins or p[0] in pins]
      print(page,c['d'],c['dev'],c['x'],c['y'],c['r'],ps)
      W=near(P,[(p[2],p[3]) for p in ps])
      for w in W: print('    W',w)
      ends=[pt for w in W for pt in w[2]]
      for f in flags(P,ends): print('    F',f)
for a in sys.argv[1:]:
  pg,ds=a.split(':');d=ds.split(',');pins=None
  show(pg,[x.split('.')[0] for x in d],[x.split('.')[1] for x in d if '.' in x] or None)
