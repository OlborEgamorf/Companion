from math import inf

import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..Getteurs import getUserTable
from ..outils import (avatarAnim, connectSQL, dictOptions, dictRefCommands,
                      dictRefOptions, getCommands, getGuild, getGuilds,
                      getMoisAnnee, getTableDay, getTimes, getUser,
                      listeOptions, tableauMois)


@login_required(login_url="/login")
def viewJours(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]

    full_guilds=getGuilds(user)
    listeMois,listeAnnee=getTimes(guild,option)

    maxi=-inf

    ctx={"rank":None,"max":maxi,
    "avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":full_guilds,
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"jours",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
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
