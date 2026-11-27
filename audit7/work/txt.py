import fitz,sys,os
ROOT=r'C:\Users\theli\Documents\EasyEDA-Pro\projects\VR Channel Bench\audit6'
B=sys.argv[1]; sec=sys.argv[2]
d=fitz.open(os.path.join(ROOT,B,sec,sec+'.pdf'))
print('pages',len(d))
for a in sys.argv[3:]:
    print(f'##### {sec} p{a}'); print(d[int(a)-1].get_text())
