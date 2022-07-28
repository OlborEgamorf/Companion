from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, tableauMois)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect


@login_required(login_url="/login")
def viewTimeline(request,guild):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    pin=getPin(user,curseurGet,guild,"poll","ranks","")
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)

    curseurGuild.execute("CREATE TABLE IF NOT EXISTS timeline (Titre TEXT, Description TEXT, Jour TEXT, Mois TEXT, Annee TEXT, DateID INT, User BIGINT, Membres TEXT)")
    elements=curseurGuild.execute("SELECT * FROM timeline ORDER BY DateID DESC").fetchall()
    connexionGuild.commit()

    for i in elements:
        infos=getUserInfo(i["User"],curseurGet,guild)
        i["Avatar"]=infos["Avatar"]
        i["Nom"]=infos["Nom"]
        i["Color"]=infos["Color"]

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "command":"timeline","option":"timeline","plus":"","elements":elements,
    "travel":False,"selector":True,"obj":None,"pagetimeline":True}
    
    return render(request, "companion/TL.html", ctx)


def addElementTL(request,guild):
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
