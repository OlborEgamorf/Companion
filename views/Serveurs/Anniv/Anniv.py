from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, tableauMois)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect


@login_required(login_url="/login")
def viewAnniv(request,guild):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    pin=getPin(user,curseurGet,guild,"poll","ranks","")
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    connexionAnniv,curseurAnniv=connectSQL("OT","Guild","Guild",None,None)

    users=curseurGet.execute("SELECT * FROM users_{0}".format(guild)).fetchall()
    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "command":"calendrier","option":"anniv","plus":"",
    "travel":False,"selector":True,"obj":None,"pageanniv":True,
    "janvier":[],"février":[],"mars":[],"avril":[],"mai":[],"juin":[],"juillet":[],"aout":[],"septembre":[],"octobre":[],"novembre":[],"décembre":[]}

    for i in users:
        anniv=curseurAnniv.execute("SELECT * FROM anniversaires WHERE ID={0}".format(i["ID"])).fetchone()
        if anniv!=None:
            infos=getUserInfo(i["ID"],curseurGet,guild)
            ctx[anniv["Mois"]].append({"ID":i["ID"],"Avatar":infos["Avatar"],"Nom":infos["Nom"],"Jour":anniv["Jour"],"Color":infos["Color"]})
    
    for i in ("janvier","février","mars","avril","mai","juin","juillet","aout","septembre","octobre","novembre","décembre"):
        ctx[i].sort(key=lambda x:x["Jour"])

    ctx["you"]=curseurAnniv.execute("SELECT * FROM anniversaires WHERE ID={0}".format(user.id)).fetchone()
    return render(request, "companion/Anniv/AnnivAll.html", ctx)


def setAnniv(request,guild):
    user=request.user
    date=request.POST.get("dateanniv")
    mois,jour=tableauMois[date[5:7]].lower(),date[8:10]

    connexionAnniv,curseurAnniv=connectSQL("OT","Guild","Guild",None,None)

    anniv=curseurAnniv.execute("SELECT * FROM anniversaires WHERE ID={0}".format(user.id)).fetchone()

    if anniv==None:
        curseurAnniv.execute("INSERT INTO anniversaires VALUES({0},{1},'{2}',3)".format(user.id,jour,mois))
    else:
        if anniv["Nombre"]!=0:
            curseurAnniv.execute("UPDATE anniversaires SET Jour={0}, Mois='{1}', Nombre=Nombre-1 WHERE ID={2}".format(jour,mois,user.id))
    
    connexionAnniv.commit()
    return redirect("/companion/{0}/anniv".format(guild))
