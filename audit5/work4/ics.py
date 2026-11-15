import sys,csv; sys.path.insert(0,'work4')
from model import *
comps,j=load_sch_json()
val={}
for r in csv.DictReader(open('components.csv',encoding='utf8')): val[r['designator']]=(r['value'],r['mpn'])
def nk(s):
    m=re.match(r'([A-Za-z]*)(\d+)',s); return (m.group(1),int(m.group(2)))
for d in sorted(comps,key=nk):
    if re.match(r'(U|Q|K2[345]|D\d|RN1$|RN11|J11|J5|J7|F1$)',d):
        if d[0]=='D' and d not in('D1','D2','D3','D6','D10','D21','D23','D11'): continue
        if d[0]=='K' or d[0]=='U' or d[0]=='Q' or True:
            print(d,val.get(d),' '.join(f"{n}/{p['name']}={p['net'] or 'NC'}" for n,p in sorted(comps[d]['pins'].items(),key=lambda x:nk(x[0]))))
