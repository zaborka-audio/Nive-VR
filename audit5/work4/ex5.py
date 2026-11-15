import json,collections
j=json.load(open('pcb_pours4.json',encoding='utf8'))
print(str(j['keys'])[:500]); print(str(j['fills'])[:800])
for p,po in zip(j['poured'],j['pours']):
    c=collections.Counter(); st=collections.Counter()
    for f in p['PourFills']:
        st[(f['fill'],f['lineWidth'],len(f['path']['complexPolygon']))]+=1
        for sub in f['path']['complexPolygon']:
            assert not isinstance(sub[0],str), sub[:5]
            for x in sub:
                if isinstance(x,str): c[x]+=1
        extra=set(f)-{'lineWidth','fill','id','path'}; 
        if extra: print(extra)
        if set(f['path'])-{'complexPolygon'}: print(f['path'].keys())
    print(po['PourName'],po['Net'],dict(c),sorted(st.items(),key=lambda x:-x[1])[:6])
