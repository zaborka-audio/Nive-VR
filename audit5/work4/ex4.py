import json,collections
j=json.load(open('pcb_pours4.json',encoding='utf8'))
print(j.keys(), j['err'])
for p in j['poured']:
    print({k:(v if k!='PourFills' else len(v)) for k,v in p.items()})
    for f in p['PourFills'][:400]:
        cp=f['path']['complexPolygon'] if 'complexPolygon' in f['path'] else f['path']
        d={k:v for k,v in f.items() if k!='path'}
        pp=f['path']
        info={k:(v if k!='complexPolygon' else None) for k,v in pp.items()} if isinstance(pp,dict) else type(pp)
        c=pp['complexPolygon']
        # c may be list of lists or flat
        kinds=collections.Counter(type(x).__name__ if not isinstance(x,str) else x for x in (c if not isinstance(c[0],list) else [y for x in c for y in x]))
        print('   ',d,info,'nested' if isinstance(c[0],list) else 'flat',len(c),dict(kinds), str(c)[:150])
