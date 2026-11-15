import sys; sys.path.insert(0,'work4')
from model import *
import pickle
comps,j=load_sch_json()
pins,pst,nets,wires,vias=load_pcb()
pinmap=pickle.load(open('work4/pinmap.pkl','rb'))
for J,x0,rowy in (('J1',9550.0,{-245.0:'A',-345.0:'B',-445.0:'C'}),('J2',5252.0,{-245.0:'A',-445.0:'C'})):
    bad=0;n=0;seen=set()
    for pid,(d,c) in pinmap.items():
        if d!=J: continue
        p=pins[pid]; y=round(p['y']-9850,1)
        if y not in rowy: print('  non-row pad',p['x'],y,p['net'],c[:3]); continue
        name=rowy[y]+str(int(round((p['x']-x0)/100))+1)
        n+=1; seen.add(name)
        sn=comps[J]['pins'][name]['net'] if name in comps[J]['pins'] else 'MISSING'
        if sn!=(p['net'] or ''): bad+=1; print('  MISMATCH',J,name,'pcb',p['net'],'sch',sn)
        if c and name not in c: print('  geometry pin not in candidate set',name,c[:4])
    print(J,'pads checked by geometry',n,'mismatch',bad,'sch pins not found',set(comps[J]['pins'])-seen)
