import json,re,collections
j=json.load(open('sch_netlist_jlceda.json',encoding='utf8'))
print(j.keys())
c=j['components']; print(len(c))
k=list(c)[0]; print({a:(b if a!='props' else '...') for a,b in c[k].items()})
print(json.dumps(c[k],ensure_ascii=False)[:200])
print(json.dumps({a:b for a,b in c[k].items() if a!='props'},ensure_ascii=False)[:1500])
for kk in j:
    if kk!='components': print(kk, str(j[kk])[:500])
