import time

import aiofiles
import aiohttp
from companion.tools.outils import static, tableauMois
from PIL import Image, ImageDraw, ImageFont, ImageOps


def squaretoround(user):
    
    mask = Image.open(static+'/mask.png').convert('L')
    im = Image.open(static+'/Temp/{0}.png'.format(user)).convert("RGBA")

    output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)

    output.save(static+'/Temp/Round{0}.png'.format(user))

def fusion(back,user,text,couleur,taille,guild):
    
    img1 = Image.open(back)
    assert img1.size[0]>255 and img1.size[1]>255, "La taille de votre image doit être supérieure à 256 pixels, que ce soit en largeur ou en hauteur."
    
    img2 = Image.open(static+"/Temp/Round{0}.png".format(user["ID"]))
    
    img1.paste(img2, ((img1.size[0]-img2.size[0])//2,(img1.size[1]-img2.size[1])//2), mask = img2)

    if text not in (None,"None"):
        setText(img1,img2,couleur,user,text,taille,guild)

    temp=time.time()
    img1.save(static+"/Temp/BV{0}.png".format(temp))
    return temp

def fusionAdieu(back,user,text,couleur,taille,guild,filtre):
    
    img1 = Image.open(back)
    assert img1.size[0]>255 and img1.size[1]>255, "La taille de votre image doit être supérieure à 256 pixels, que ce soit en largeur ou en hauteur."
    
    img2 = Image.open(static+"/Temp/Round{0}.png".format(user["ID"]))
    img3 = Image.open(static+'/non.png').convert('RGBA')

    img1.paste(img2, ((img1.size[0]-img2.size[0])//2,(img1.size[1]-img2.size[1])//2), mask = img2)
    img1.paste(img3, ((img1.size[0]-img3.size[0])//2,(img1.size[1]-img3.size[1])//2), mask = img3)
    
    if text not in (None,"None"):
        setText(img1,img2,couleur,user,text,taille,guild)
    
    if filtre==True:
        img1=img1.convert('L')

    temp=time.time()
    img1.save(static+"/Temp/AD{0}.png".format(temp))
    return temp


def formatage(alerte:str,user,guild):

    alerte=alerte.replace("{user}","<@{0}>".format(user["ID"]))
    alerte=alerte.replace("{name}",user["Nom"])
    alerte=alerte.replace("{guild}",guild["Nom"])
    alerte=alerte.replace("{number}",str(guild["Count"]))
    alerte=alerte.replace("{date}","{0} {1}".format(time.strftime("%d"),tableauMois[time.strftime("%m")].lower()))

    return alerte


def setText(img1,img2,color,user,text,taille,guild):
    font = ImageFont.truetype(static+'/RobotoCondensed-Regular.ttf', taille)
    text=formatage(text,user,guild)
    textAlign=""
    maxi=img1.size[0]-img1.size[0]//10
    nb=0
    pix=taille*30/50
    for i in text.split(" "):
        if len(i)*pix>maxi:
            cut=0
            textAlign+=" "
            for j in i:
                if cut>maxi:
                    textAlign+="\n"
                    cut=0
                textAlign+=j
                cut+=pix
            textAlign+=" "
            nb=cut
            continue
        elif len(i)*pix+nb>maxi:
            textAlign+="\n"
            nb=0
        else:
            textAlign+=" "
        textAlign+=i
        nb+=len(i)*pix

    draw=ImageDraw.Draw(img1)
    draw.text((img1.size[0]//2,(img1.size[1]-img2.size[1])//2+img1.size[1]//2),textAlign[1:],color,font=font,anchor="mm",align="center")

def resize(path):
    img=Image.open(path)
    size=img.size
    if img.size[0]>1280:
        img=img.resize((1280,int(size[1]*1280/size[0])))
    if img.size[1]>720:
        img=img.resize((int(size[0]*720/size[1]),720))
    assert img.size[0]>256 and img.size[1]>256

    img.save(path)

async def getAvatar(user,avatar):
    """Récupère et enregistre l'avatar d'un utilisateur Discord."""
    async with aiohttp.ClientSession() as session:
        async with session.get("https://cdn.discordapp.com/avatars/{0}/{1}.png?size=128".format(user,avatar)) as resp:
            if resp.status == 200:
                f = await aiofiles.open(static+"/Temp/"+str(user)+".png", mode='wb')
                await f.write(await resp.read())
                await f.close()
