import json,sys
O=json.load(open('vrb_k6dump.json',encoding='utf-8'))
def fl(l): return [v for s in l for v in s] if isinstance(l[0],list) else l
def occ(P):
  pts=[]
  for w in P['wires']:
    f=fl(w[1]);ws=list(zip(f[::2],f[1::2]))
    for (a,b),(c,d) in zip(ws,ws[1:]):
      n=int(max(abs(c-a),abs(d-b))/5)+1
      pts+=[(a+(c-a)*i/n,b+(d-b)*i/n) for i in range(n+1)]
  for c in P['comps']:
    pts.append((c['x'],c['y']))
    for p in c.get('pins') or []: pts.append((p[2],p[3]))
  for t in P['texts']: 
    for i in range(0,len(t[3])*7,10): pts.append((t[1]+i,t[2]))
  return pts
def find(page,x0,y0,x1,y1,w,h,step=10):
  P=[v for k,v in O.items() if k.startswith(page+' ')][0];pts=occ(P);res=[]
  for x in range(x0,x1+1,step):
    for y in range(y0,y1+1,step):
      if all(not(x-w/2-10<=a<=x+w/2+10 and y-h/2-10<=b<=y+h/2+10) for a,b in pts): res.append((x,y))
  return res
for a in sys.argv[1:]:
  pg,r=a.split(':');v=list(map(int,r.split(',')))
  res=find(pg,*v);print(a,len(res),res[:40])
