import sys,json,re,collections
sys.path.insert(0,'work4')
from dsn import *
VIAPS='pf07a228c575f71a'
def load_sch_json():
    j=json.load(open('sch_netlist_jlceda.json',encoding='utf8'))
    comps={}
    for k,c in j['components'].items():
        d=c['props']['Designator']
        comps.setdefault(d,{'fp':c['props'].get('Footprint'),'props':c['props'],'pins':{}})
        for pk,p in c['pinInfoMap'].items():
            if p['number'] in comps[d]['pins'] and comps[d]['pins'][p['number']]['net']!=p['net']:
                print('DUP PIN',d,p)
            comps[d]['pins'][p['number']]={'name':p['name'],'net':p['net']}
    return comps,j
def load_sch_pads():
    parts={};nets={}
    mode=None;cur=None
    for line in open('sch_netlist_pads.asc',encoding='utf8',errors='replace'):
        line=line.rstrip('\n')
        if line.startswith('*PART*'): mode='p';continue
        if line.startswith('*NET*'): mode='n';continue
        if line.startswith('*SIGNAL*'): cur=line.split()[1]; nets[cur]=[];continue
        if line.startswith('*'): mode=None if line.startswith('*END') else mode;continue
        if mode=='p' and line.strip():
            a=line.split(); parts[a[0]]=a[1] if len(a)>1 else ''
        if mode=='n' and line.strip():
            nets[cur]+=line.split()
    return parts,nets
def load_pcb():
    t=load()
    lib=find(t,'library')[0]
    img=find(lib,'image')[0]
    pins={}
    for p in find(img,'pin'):
        pins[p[2]]={'ps':p[1],'x':float(p[3]),'y':float(p[4]),'net':None,'id':p[2]}
    pst={}
    for p in find(lib,'padstack'):
        pst[p[1]]=[s[1] for s in find(p,'shape')]
    nets={}
    for n in find(find(t,'network')[0],'net'):
        name=n[1].strip('"\'')
        pl=[x.split('-',1)[1] for x in find(n,'pins')[0][1:]] if find(n,'pins') else []
        nets[name]=pl
        for x in pl:
            assert pins[x]['net'] is None,x
            pins[x]['net']=name
    w=find(t,'wiring')[0]
    wires=[]
    for x in find(w,'wire'):
        p=x[1]
        wires.append({'layer':p[1],'w':float(p[2]),'pts':[(float(p[i]),float(p[i+1])) for i in range(3,len(p),2)],'net':find(x,'net')[0][1].strip('"\'')})
    vias=[{'x':float(v[2]),'y':float(v[3]),'net':find(v,'net')[0][1].strip('"\'')} for v in find(w,'via')]
    return pins,pst,nets,wires,vias

_load_pcb_dsn=load_pcb
def load_pcb():
    pins,pst,nets,wires,vias=_load_pcb_dsn()
    j=json.load(open('pcb_lines_live4.json',encoding='utf8'))
    wires=[{'layer':str(l[2]),'w':float(l[7]),'pts':[(l[3],l[4]+9850.0),(l[5],l[6]+9850.0)],'net':l[1],'id':l[0]} for l in j['L']]
    vias=[{'x':v[2],'y':v[3]+9850.0,'net':v[1],'d':float(v[5])} for v in j['V']]
    return pins,pst,nets,wires,vias
