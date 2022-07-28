import asyncio
import os

from companion.tools.Getteurs import *
from companion.tools.outils import connectSQL, createPhrase, root
from companion.views.Serveurs.Outils.BienvenueOutils import (fusion, getAvatar,
                                                             resize,
                                                             squaretoround)
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from colorthief import ColorThief

@login_required(login_url="/login")
def viewGestionAnniv(request,guild):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    pin=getPin(user,curseurGet,guild,"poll","ranks","")
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)

    etatAnniv=curseurGuild.execute("SELECT * FROM etatModules WHERE Module='AnnivAuto'").fetchone()
    images=curseurGuild.execute("SELECT * FROM imagesAnniv").fetchall()
    guild_full["Count"]=curseurGet.execute("SELECT Count() AS Count FROM users_{0}".format(guild)).fetchone()["Count"]
    for i in images:
        asyncio.run(getAvatar(user.id,user_full["Avatar"]))
        squaretoround(user.id)
        temp=fusion(root+"/"+i["Path"],user_full,i["Message"],i["Couleur"],i["Taille"],guild_full)
        i["Path"]="/static/companion/Temp/BV"+str(temp)+".png"

    messages=curseurGuild.execute("SELECT * FROM messagesAnniv").fetchall()

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "command":"Annivad","option":"outils","plus":"","etatAnniv":etatAnniv,"images":images,"messages":messages,
    "travel":False,"selector":True,"obj":None,"pageoutils":True,"listeOutils":["Alertes Twitch","Alertes YouTube","Alertes Twitter","Messages de Bienvenue","Messages d'Adieu","Roles","Tableaux","Voice Ephem","Icones Dynamiques","Commandes Auto","Commandes Personnalisées","Anniversaires"],
    "pin":pin}
    
    return render(request, "companion/Outils/AnnivAuto.html", ctx) 

def simulateAnniv(request,guild,idimg):
    user=request.user
    mess,color,taille=request.GET.get("mess"),request.GET.get("color"),request.GET.get("taille")
    color="#"+color

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
    guild_full["Count"]=curseurGet.execute("SELECT Count() AS Count FROM users_{0}".format(guild)).fetchone()["Count"]

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    image=curseurGuild.execute("SELECT * FROM imagesAnniv WHERE Nombre={0}".format(idimg)).fetchone()

    asyncio.run(getAvatar(user.id,user_full["Avatar"]))
    squaretoround(user.id)
    temp=fusion(root+"/"+image["Path"],user_full,mess,color,int(taille),guild_full)

    return JsonResponse(data={"img":"/static/companion/Temp/BV"+str(temp)+".png"})


def toggleImgAnniv(request,guild,idimg):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    if request.GET.get("active")=="true":
        curseurGuild.execute("UPDATE imagesAnniv SET Active=True WHERE Nombre={0}".format(idimg))
    else:
        curseurGuild.execute("UPDATE imagesAnniv SET Active=False WHERE Nombre={0}".format(idimg))
    connexionGuild.commit()
    return JsonResponse(data={})

def toggleMessAnniv(request,guild,idmessage):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    if request.GET.get("active")=="true":
        curseurGuild.execute("UPDATE messagesAnniv SET Active=True WHERE Nombre={0}".format(idmessage))
    else:
        curseurGuild.execute("UPDATE messagesAnniv SET Active=False WHERE Nombre={0}".format(idmessage))
    connexionGuild.commit()
    return JsonResponse(data={})

def toggleAnniv(request,guild):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    if request.GET.get("active")=="true":
        curseurGuild.execute("UPDATE etatModules SET Active=True WHERE Module='AnnivAuto'")
    else:
        curseurGuild.execute("UPDATE etatModules SET Active=False WHERE Module='AnnivAuto'")
    connexionGuild.commit()
    return JsonResponse(data={})

def editMessAnniv(request,guild,idmessage):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    curseurGuild.execute("UPDATE messagesAnniv SET Message='{0}' WHERE Nombre={1}".format(createPhrase(request.GET.get("message")),idmessage))
    connexionGuild.commit()
    return JsonResponse(data={})

def editImgAnniv(request,guild,idimg):
    user=request.user
    mess,color,taille=createPhrase(request.GET.get("mess")),request.GET.get("color"),request.GET.get("taille")
    color="#"+color

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    curseurGuild.execute("UPDATE imagesAnniv SET Message='{0}', Couleur='{1}', Taille={2} WHERE Nombre={3}".format(mess,color,taille,idimg))
    connexionGuild.commit()

    return JsonResponse(data={})

def addMessAnniv(request,guild):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    count=curseurGuild.execute("SELECT Count FROM etatModules WHERE Module='AnnivAuto'").fetchone()["Count"]
    curseurGuild.execute("UPDATE etatModules SET Count=Count+1 WHERE Module='AnnivAuto'")
    curseurGuild.execute("INSERT INTO messagesAnniv VALUES ({0},'{1}',True)".format(count+1,"Joyeux anniversaire {user} !"))
    connexionGuild.commit()
    return JsonResponse(data={"count":count+1})

def addImgAnniv(request,guild):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    count=curseurGuild.execute("SELECT Count2 FROM etatModules WHERE Module='AnnivAuto'").fetchone()["Count2"]+1
    curseurGuild.execute("UPDATE etatModules SET Count2=Count2+1 WHERE Module='AnnivAuto'")

    message=request.POST.get("message")
    message=createPhrase(message)

    if len(request.FILES)!=0:
        image=request.FILES["image"]
        if not os.path.exists(root+"/Anniv/"+str(guild)):
            os.makedirs(root+"/Anniv/"+str(guild))
        filename="Anniv/{0}/{1}{2}".format(guild,count,image.name)
        with open(root+"/"+filename, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
    
    resize(root+"/"+filename)

    color=ColorThief(root+"/"+filename).get_color(quality=1)
    if color[0]*0.21+color[1]*0.72+color[2]*0.07<50:
        color="#FFFFFF"
    else:
        color="#000000"
    
    curseurGuild.execute("INSERT INTO imagesAnniv VALUES({0},'{1}','{2}','{3}',50,True)".format(count,filename,message,color))
    connexionGuild.commit()

    return redirect("/companion/{0}/annivauto".format(guild))


def delMessAnniv(request,guild,idmessage):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    curseurGuild.execute("DELETE FROM messagesAnniv WHERE Nombre={0}".format(idmessage))
    connexionGuild.commit()
    return JsonResponse(data={})

def delImgAnniv(request,guild,idimg):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    curseurGuild.execute("DELETE FROM imagesAnniv WHERE Nombre={0}".format(idimg))
    connexionGuild.commit()
    return JsonResponse(data={})

def chanAnniv(request,guild):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    salon=request.POST.get("salon")
    curseurGuild.execute("UPDATE etatModules SET Salon={0} WHERE Module='AnnivAuto'".format(salon))
    return redirect("/companion/{0}/outils/bienvenue".format(guild))