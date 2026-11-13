import json
exec(open('common4.py').read())
src=open('pl9.py').read(); exec(src[:src.index('P=lambda')])
pos=json.load(open('plv2.json'))
for d in ['J1','J2','J5','J6','J7','J8','J11']:
    print(d,pos[d],[round(v) for v in bbox_at(d,*pos[d],0)], C[d]['fp'], 'orig',C[d]['x'],C[d]['y'],C[d]['r'])
print('W,H',W,H)
