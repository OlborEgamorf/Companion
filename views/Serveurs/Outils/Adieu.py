import asyncio
import os

from colorthief import ColorThief
from companion.tools.Getteurs import *
from companion.tools.outils import connectSQL, createPhrase, root
from companion.views.Serveurs.Outils.BienvenueOutils import (fusionAdieu,
                                                             getAvatar, resize,
                                                             squaretoround)
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render


@login_required(login_url="/login")
def viewGestionAD(request,guild):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    pin=getPin(user,curseurGet,guild,"poll","ranks","")
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)

    etatAD=curseurGuild.execute("SELECT * FROM etatModules WHERE Module='AD'").fetchone()
    images=curseurGuild.execute("SELECT * FROM imagesAD").fetchall()
    guild_full["Count"]=curseurGet.execute("SELECT Count() AS Count FROM users_{0}".format(guild)).fetchone()["Count"]
    for i in images:
        asyncio.run(getAvatar(user.id,user_full["Avatar"]))
        squaretoround(user.id)
        temp=fusionAdieu(root+"/"+i["Path"],user_full,i["Message"],i["Couleur"],i["Taille"],guild_full,i["Filtre"])
        i["Path"]="/static/companion/Temp/AD"+str(temp)+".png"

    messages=curseurGuild.execute("SELECT * FROM messagesAD").fetchall()

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "command":"bvad","option":"outils","plus":"","etatAD":etatAD,"images":images,"messages":messages,
    "travel":False,"selector":True,"obj":None,"pageoutils":True,
    "pin":pin}
    
    return render(request, "companion/Outils/Adieu.html", ctx) 

def simulateAD(request,guild,idimg):
    user=request.user
    mess,color,taille,filtre=request.GET.get("mess"),request.GET.get("color"),request.GET.get("taille"),request.GET.get("filtre")
    color="#"+color
    if filtre=="true":
        filtre=True
    else:
        filtre=False

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
    guild_full["Count"]=curseurGet.execute("SELECT Count() AS Count FROM users_{0}".format(guild)).fetchone()["Count"]

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    image=curseurGuild.execute("SELECT * FROM imagesAD WHERE Nombre={0}".format(idimg)).fetchone()

    asyncio.run(getAvatar(user.id,user_full["Avatar"]))
    squaretoround(user.id)
    temp=fusionAdieu(root+"/"+image["Path"],user_full,mess,color,int(taille),guild_full,filtre)

    return JsonResponse(data={"img":"/static/companion/Temp/AD"+str(temp)+".png"})


def toggleImgAD(request,guild,idimg):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    if request.GET.get("active")=="true":
        curseurGuild.execute("UPDATE imagesAD SET Active=True WHERE Nombre={0}".format(idimg))
    else:
        curseurGuild.execute("UPDATE imagesAD SET Active=False WHERE Nombre={0}".format(idimg))
    connexionGuild.commit()
    return JsonResponse(data={})

def toggleMessAD(request,guild,idmessage):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    if request.GET.get("active")=="true":
        curseurGuild.execute("UPDATE messagesAD SET Active=True WHERE Nombre={0}".format(idmessage))
    else:
        curseurGuild.execute("UPDATE messagesAD SET Active=False WHERE Nombre={0}".format(idmessage))
    connexionGuild.commit()
    return JsonResponse(data={})

def toggleAD(request,guild):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    if request.GET.get("active")=="true":
        curseurGuild.execute("UPDATE etatModules SET Active=True WHERE Module='AD'")
    else:
        curseurGuild.execute("UPDATE etatModules SET Active=False WHERE Module='AD'")
    connexionGuild.commit()
    return JsonResponse(data={})

def editMessAD(request,guild,idmessage):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    curseurGuild.execute("UPDATE messagesAD SET Message='{0}' WHERE Nombre={1}".format(createPhrase(request.GET.get("message")),idmessage))
    connexionGuild.commit()
    return JsonResponse(data={})

def editImgAD(request,guild,idimg):
    user=request.user
    mess,color,taille,mode,filtre=createPhrase(request.GET.get("mess")),request.GET.get("color"),request.GET.get("taille"),request.GET.get("mode"),request.GET.get("filtre")
    color="#"+color
    if filtre=="true":
        filtre=True
    else:
        filtre=False

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    curseurGuild.execute("UPDATE imagesAD SET Message='{0}', Couleur='{1}', Taille={2}, Mode='{3}', Filtre={4} WHERE Nombre={5}".format(mess,color,taille,mode,filtre,idimg))
    connexionGuild.commit()

    return JsonResponse(data={})

def addMessAD(request,guild):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    count=curseurGuild.execute("SELECT Count FROM etatModules WHERE Module='AD'").fetchone()["Count"]
    curseurGuild.execute("UPDATE etatModules SET Count=Count+1 WHERE Module='AD'")
    curseurGuild.execute("INSERT INTO messagesAD VALUES ({0},'{1}',True)".format(count+1,"Adieu {name}..."))
    connexionGuild.commit()
    return JsonResponse(data={"count":count+1})

def addImgAD(request,guild):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    count=curseurGuild.execute("SELECT Count2 FROM etatModules WHERE Module='AD'").fetchone()["Count2"]+1
    curseurGuild.execute("UPDATE etatModules SET Count2=Count2+1 WHERE Module='AD'")

    message=request.POST.get("message")
    message=createPhrase(message)

    if len(request.FILES)!=0:
        image=request.FILES["image"]
        if not os.path.exists(root+"/BV/"+str(guild)):
            os.makedirs(root+"/BV/"+str(guild))
        filename="BV/{0}/{1}{2}".format(guild,count,image.name)
        with open(root+"/"+filename, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
    
    resize(root+"/"+filename)

    color=ColorThief(root+"/"+filename).get_color(quality=1)
    if color[0]*0.21+color[1]*0.72+color[2]*0.07<50:
        color="#FFFFFF"
    else:
        color="#000000"
    
    curseurGuild.execute("INSERT INTO imagesAD VALUES({0},'{1}','{2}','{3}',50,'all',True,True)".format(count,filename,message,color))
    connexionGuild.commit()

    return redirect("/companion/{0}/adieu".format(guild))


def delMessAD(request,guild,idmessage):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    curseurGuild.execute("DELETE FROM messagesAD WHERE Nombre={0}".format(idmessage))
    connexionGuild.commit()
    return JsonResponse(data={})

def delImgAD(request,guild,idimg):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    curseurGuild.execute("DELETE FROM imagesAD WHERE Nombre={0}".format(idimg))
    connexionGuild.commit()
    return JsonResponse(data={})

def chanAD(request,guild):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    salon=request.POST.get("salon")
    curseurGuild.execute("UPDATE etatModules SET Salon={0} WHERE Module='AD'".format(salon))
    return redirect("/companion/{0}/outils/adieu".format(guild))
