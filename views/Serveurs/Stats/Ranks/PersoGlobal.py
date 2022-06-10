from math import inf

from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, dictOptions, getMoisAnnee, getMoisAnneePerso,
                                    getTimes, listeOptions, listeOptionsJeux,
                                    tableauMois)
from companion.views.Serveurs.Stats.Recap import getPerso
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required(login_url="/login")
@CompanionStats
def viewPersoGlobal(request,guild):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    if guild=="OT":
        pin=getPin(user,curseurGet,"jeux","","ranks","")
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
        color=curseurGet.execute("SELECT * FROM couleurs WHERE ID={0}".format(user.id)).fetchone()
        if color!=None:
            color="#"+hex(int('%02x%02x%02x' % (color["R"], color["G"], color["B"]),base=16))[2:]
            liste=listeOptionsJeux
    else:
        pin=getPin(user,curseurGet,guild,"","ranks","")
        categ="Stats"
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
        color=curseurGet.execute("SELECT * FROM users JOIN users_{0} ON users.ID = users_{0}.ID WHERE users.ID={1}".format(guild,user.id)).fetchone()["Color"]
        color="#"+hex(color)[2:]
        liste=listeOptions

    allRanks={}
    for option in liste:
        if option in ("divers","messages","voice"):
            continue
        if True:
            connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)
            mois,annee,moisDB,anneeDB=getMoisAnneePerso(mois,annee)
            allRanks[option]=getPerso(request,guild,option,curseur=curseur,curseurGet=curseurGet,moisDB=moisDB,anneeDB=anneeDB,user=user,curseurGuild=curseurGuild)
        else:
            continue

    optionsStats=list(map(lambda x:x,allRanks))
    if categ=="Jeux":
        listeMois,listeAnnee=getTimes(guild,option,"Jeux")
        ctx={"ranks":allRanks,
        "avatar":user_full["Avatar"],"id":str(user.id),"nom":user_full["Nom"],"color":color,
        "guildname":"Olbor Track - Mondial","guildid":"ot/jeux",
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "command":"ranks","options":listeOptionsJeux,"option":option,"plus":"",
        "travel":True,"selector":True,"ot":True,"pagestats":True,"alloptions":optionsStats,
        "pin":pin}
        
        return render(request, "companion/Stats/Ranks/RanksGlobal.html", ctx)
    else:
        listeMois,listeAnnee=getTimes(guild,option,"Stats")

        ctx={"ranks":allRanks,
        "avatar":user_full["Avatar"],"id":str(user.id),"nom":user_full["Nom"],"color":color,
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "command":"ranks","options":listeOptions,"option":option,"plus":"",
        "travel":True,"selector":True,"pagestats":True,"alloptions":optionsStats,
        "pin":pin}

        return render(request, "companion/Stats/Perso/PersoGlobal.html", ctx)
