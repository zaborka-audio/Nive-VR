import json,sys,re
t=open(sys.argv[1]).read().split('\n');out=[];n=0
for l in t:
    if '||' not in l: out.append(l);continue
    h,b=l.split('||',1)
    hj=json.loads(h)
    if hj['type'] in('PAD','POLY','FILL'):
        body,tail=b.rsplit('|',1) if b.endswith('|') else (b,None)
        d=json.loads(body)
        if hj['type']=='PAD':
            k=int(d['num']);d['num']=str(k+1 if k%2 else k-1);n+=1
        elif d.get('layerId') in (3,49) :
            def fy(p):
                if isinstance(p,list):
                    if p and p[0]=='CIRCLE': return [p[0],p[1],-p[2],p[3]]
                    r=[];i=0;nums=[]
                    # flip every second numeric
                    cnt=0
                    for v in p:
                        if isinstance(v,(int,float)):
                            r.append(-v if cnt%2==1 else v);cnt+=1
                        elif isinstance(v,list): r.append(fy(v))
                        else: r.append(v)
                    return r
                return p
            d['path']=fy(d['path'])
        b=json.dumps(d,separators=(',',':'),ensure_ascii=False)+('|' if tail is not None else '')
    out.append(h+'||'+b)
open(sys.argv[2],'w').write('\n'.join(out));print('pads',n)
