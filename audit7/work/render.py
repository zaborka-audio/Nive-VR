import fitz,sys,os
# usage: render.py book sec page dpi [x0 y0 x1 y1 fractions] [rot]
ROOT=r'C:\Users\theli\Documents\EasyEDA-Pro\projects\VR Channel Bench\audit6'
OUT=r'C:\Users\theli\Documents\EasyEDA-Pro\projects\VR Channel Bench\audit7\work\img'
B=sys.argv[1]; sec=sys.argv[2]; pg=int(sys.argv[3]); dpi=int(sys.argv[4])
d=fitz.open(os.path.join(ROOT,B,sec,sec+'.pdf')); p=d[pg-1]
clip=None; tag=''
if len(sys.argv)>=9:
    f=[float(x) for x in sys.argv[5:9]]; r=p.rect
    clip=fitz.Rect(r.x0+f[0]*r.width, r.y0+f[1]*r.height, r.x0+f[2]*r.width, r.y0+f[3]*r.height)
    tag='_'+'_'.join(sys.argv[5:9])
rot=int(sys.argv[9]) if len(sys.argv)>9 else 0
pm=p.get_pixmap(dpi=dpi,clip=clip)
out=os.path.join(OUT,f'{B}_{sec}_p{pg}_{dpi}{tag}{"_r"+str(rot) if rot else ""}.png')
os.makedirs(OUT,exist_ok=True)
pm.save(out)
if rot:
    from PIL import Image
    im=Image.open(out).rotate(rot,expand=True); im.save(out)
print(out,pm.width,pm.height,'rot',p.rotation,'rect',p.rect)
