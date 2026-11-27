import sys,os,glob
from PIL import Image
src=r'C:\Users\theli\Pictures\Neve VR'
files=sorted(glob.glob(os.path.join(src,'*.jpeg')))
thumbs=[]
for f in files:
    im=Image.open(f); im.thumbnail((300,400)); thumbs.append((os.path.basename(f),im.copy()))
cols=7; rows=(len(thumbs)+cols-1)//cols
sheet=Image.new('RGB',(cols*310,rows*420),'white')
from PIL import ImageDraw
d=ImageDraw.Draw(sheet)
for i,(n,im) in enumerate(thumbs):
    x=(i%cols)*310; y=(i//cols)*420
    sheet.paste(im,(x,y)); d.text((x+2,y+402),n[15:],fill='black')
sheet.save(r'C:\Users\theli\Documents\EasyEDA-Pro\projects\VR Channel Bench\audit7\work\img\photos_contact.jpg',quality=85)
print(len(files),sheet.size)
