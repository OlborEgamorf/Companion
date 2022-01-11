from math import inf

import requests
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import render

from ..Getteurs import *
from ..outils import (avatarAnim, collapseEvol, connectSQL, dictOptions,
                      dictRefCommands, dictRefOptions, getCommands, getGuild,
                      getGuilds, getMoisAnnee, getTimes, getUser, listeOptions,
                      tableauMois)


@login_required(login_url="/login")
def viewRank(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    guild_full=getGuild(guild)

    maxi=-inf
    stats=[]

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)

    if option!="freq":
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT 150".format(moisDB,anneeDB)).fetchall():

        if option in ("messages","voice","mots"):
            stats.append(getUserTable(i,curseurGet,guild))

        elif option in ("emotes","reactions"):
            stats.append(getEmoteTable(i,curseurGet))

        elif option in ("salons","voicechan"):
            stats.append(getChannels(i,curseurGet))

        elif option=="freq":
            stats.append(getFreq(i))

        maxi=max(maxi,i["Count"])

    connexion.close()

    if "/mix/" in request.path:
        return {"rank":stats,"guildicon":guild_full["icon"],"guildname":guild_full["name"],"guildid":guild}
    else:
        user_full=getUser(guild,user.id)
        user_avatar=user_full["user"]["avatar"]
        full_guilds=getGuilds(user)
        listeMois,listeAnnee=getTimes(guild,option)

        ctx={"rank":stats,"max":maxi,
        "avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),
        "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":full_guilds,
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"ranks",
        "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
        "travel":True,"selector":True,"obj":None}

        return render(request, "companion/Ranks/ranks.html", ctx)


@login_required(login_url="/login")
def iFrameRank(request,guild,option):
    all=request.GET.get("data")
    mois,annee,obj=all.split("?")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user
    if obj==None:
        obj=user.id

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    if option in ("messages","mots","voice"):

        user_full=getUser(guild,obj)
        stats=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,obj)).fetchall()
        stats=collapseEvol(stats)
        stats.reverse()        
        color=getColor(obj,guild,curseurGet)
        maxi=max(list(map(lambda x:x["Count"],stats)))
        ctx={"rank":stats,"id":user.id,"color":color,"max":maxi,"mois":mois,"annee":annee,"nom":user_full["user"]["username"],"option":option}
        return render(request,"companion/Ranks/iFrameRanks_evol.html",ctx)

    else:

        maxi=-inf
        stats=[]
        for i in curseur.execute("SELECT * FROM {0}{1}{2} ORDER BY Rank ASC LIMIT 150".format(moisDB,anneeDB,obj)).fetchall():
            stats.append(getUserTable(i,curseurGet,guild))
            maxi=max(maxi,i["Count"])

        ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"option":option}
        return render(request, "companion/Ranks/iFrameRanks_ranks.html", ctx)