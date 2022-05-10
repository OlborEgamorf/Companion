from math import inf

import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..Getteurs import getUserTable
from ..outils import (connectSQL, dictOptions, dictRefCommands,
                      dictRefOptions, getCommands,
                      getMoisAnnee, getPlus, getTableDay, getTimes,
                      listeOptions, tableauMois,dictRefPlus)


@login_required(login_url="/login")
def viewJours(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    listeMois,listeAnnee=getTimes(guild,option,"Stats")

    maxi=-inf

    ctx={"rank":None,"max":maxi,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"jours",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("jours",option),"dictPlus":dictRefPlus,"plus":"",
    "travel":True,"selector":True}
    
    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL",None)

    table=getTableDay(curseur,tableauMois[moisDB],anneeDB)

    ctx["max"]=max(list(map(lambda x:x["Count"],table)))
    ctx["rank"]=table
    
    return render(request,"companion/jours.html",ctx)


@login_required(login_url="/login")
def iFrameJour(request,guild,option):
    all=request.GET.get("data")
    jour,mois,annee=all.split("?")
    user=request.user
    
    connexion,curseur=connectSQL(guild,"Rapports","Stats","GL",None)
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    stats=[]
    maxi=-inf
    for i in curseur.execute("SELECT * FROM ranks WHERE Jour='{0}' AND Mois='{1}' AND Annee='{2}' AND Type='{3}' ORDER BY Rank ASC".format(jour,mois,annee,dictOptions[option])).fetchall():

        stats.append(getUserTable(i,curseurGet,guild))
        maxi=max(maxi,i["Count"])
    
    connexion.close()
    ctx={"rank":stats,"id":user.id,"max":maxi,"jour":jour, "mois":mois,"annee":annee,"option":option}
    return render(request, "companion/Ranks/iFrameRanks_ranks.html", ctx)
