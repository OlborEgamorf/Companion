from math import inf

from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import *
from companion.tools.outils import (collapseEvol, connectSQL, dictOptions,
                              getMoisAnnee, getTimes, listeOptions,
                              listeOptionsJeux, tableauMois)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
@CompanionStats
def viewTimeline(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    maxi=-inf
    stats=[]

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        pin=getPin(user,curseurGet,"ot/jeux",option,"ranks","")
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
    else:
        pin=getPin(user,curseurGet,guild,option,"ranks","")
        categ="Stats"
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    connexionRap,curseurRap=connectSQL(guild,"Guild","Guild",None,None)

    if moisDB=="glob":
        dates=curseurRap.execute("SELECT DISTINCT Jour,Mois,Annee,DateID FROM ranks WHERE Type='{0}' ORDER BY DateID ASC".format(option)).fetchall()
        archiveTemp=[]
        for jour in dates:
            archive=curseurRap.execute("SELECT * FROM archives WHERE DateID={0} AND Type='{1}' AND Period='Global' ORDER BY Rank ASC".format(jour["DateID"],option)).fetchall()
            if list(filter(lambda x:x["ID"]==user.id,archive))==[]:
                evolPerso=curseur.execute("SELECT * FROM evol{0}{1}{2} WHERE DateID='{3}'".format(moisDB,anneeDB,user.id,jour["DateID"])).fetchone()
            

    if categ=="Jeux":
        listeMois,listeAnnee=getTimes(guild,option,"Jeux")
        ctx={"rank":stats,"max":maxi,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":"Classements Jeux","guildid":"ot/jeux",
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "command":"ranks","options":listeOptionsJeux,"option":option,"plus":"","travel":True,"selector":True,"obj":None,"pin":pin,
        "pagestats":True,"ot":True}
        return render(request, "companion/Stats/Ranks/ranks.html", ctx)
    else:
        listeMois,listeAnnee=getTimes(guild,option,"Stats")

        ctx={"rank":stats,"max":maxi,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "command":"ranks","options":listeOptions,"option":option,"plus":"" if option in ("messages","voice","mots") else "serv",
        "travel":True,"selector":True,"obj":None,"pagestats":True,
        "pin":pin}

        if option=="divers":
            return render(request, "companion/Stats/Ranks/ranksDivers.html", ctx)
        else:
            return render(request, "companion/Stats/Ranks/ranks.html", ctx)