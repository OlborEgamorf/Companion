from math import inf

import requests
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import render

from ..Getteurs import *
from ..outils import (avatarAnim, collapseEvol, colorRoles, connectSQL,
                      dictOptions, dictRefCommands, dictRefOptions,
                      getCommands, getGuild, getGuilds, getMoisAnnee, getTimes,
                      getUser, listeOptions, tableauMois)


@login_required(login_url="/login")
def viewRank(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    print(mois,annee)
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)

    maxi=-inf
    stats=[]
    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
    flag=False

    full_guilds=getGuilds(user)
    listeMois,listeAnnee=getTimes(guild,option)

    ctx={"rank":stats,"max":maxi,
    "avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":full_guilds,
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"ranks",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "travel":True,"selector":True,"obj":None}

    if option in ("emotes","reactions"):
        full_emotes=getAllEmotes(full_guilds)

    for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT 100".format(moisDB,anneeDB)).fetchall():

        if option in ("messages","voice","mots"):
            stats.append(getUserTable(i,guild,roles_position,roles_color))

        elif option in ("emotes","reactions"):
            stats.append(getEmoteTable(i,full_emotes))

        elif option in ("salons","voicechan"):
            stats.append(getChannels(i))

        elif option=="freq":
            stats.append(getFreq(i))

        maxi=max(maxi,i["Count"])

    ctx["max"]=maxi
    connexion.close()

    if option in ("messages","voice","mots"):
        return render(request, "companion/Ranks/ranks.html", ctx)
    elif option in ("emotes","reactions"):
        return render(request, "companion/Ranks/ranksEmotes.html", ctx)
    else:
        return render(request, "companion/Ranks/ranksAutres.html", ctx)


@login_required(login_url="/login")
def iFrameRank(request,guild,option):
    all=request.GET.get("data")
    mois,annee,id=all.split("?")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user
    if id==None:
        id=user.id

    guild_full=getGuild(guild)

    user_full=getUser(guild,id)
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)
    
    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)

    table=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,id)).fetchall()
    table=collapseEvol(table)

    user_full["roles"].sort(key=lambda x:roles_position[x], reverse=True)
    if len(user_full["roles"])==0:
        color=None
    else:
        color="#{0}".format(hex(roles_color[user_full["roles"][0]])[2:])

    maxi=max(list(map(lambda x:x["Count"],table)))

    ctx={"rank":table,"id":user.id,"color":color,"max":maxi,"mois":mois,"annee":annee,"nom":user_full["user"]["username"],"option":option}
    connexion.close()
    return render(request,"companion/Ranks/iFrameRanks_evol.html",ctx)


@login_required(login_url="/login")
def iFrameRankObj(request,guild,option):
    all=request.GET.get("data")
    mois,annee,obj=all.split("?")
    mois,annee,moisDB,anneeDB=getMoisAnnee(tableauMois[mois],annee)
    user=request.user

    guild_full=getGuild(guild)
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)
    
    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)

    maxi=-inf
    stats=[]

    for i in curseur.execute("SELECT * FROM {0}{1}{2} ORDER BY Rank ASC".format(moisDB,anneeDB,obj)).fetchall():

        stats.append(getUserTable(i,guild,roles_position,roles_color))
        maxi=max(maxi,i["Count"])
    
    connexion.close()
    ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"option":option}
    return render(request, "companion/Ranks/iFrameRanks_ranks.html", ctx)
