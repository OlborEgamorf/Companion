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
def viewFirst(request,guild,option):
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)

    maxiM,maxiA=-inf,-inf
    statsM,statsA=[],[]
    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")

    full_guilds=getGuilds(user)

    ctx={"rankMois":statsM,"rankAnnee":statsA,"maxM":maxiM,"maxA":maxiA,
    "avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":full_guilds,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"first",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "travel":False,"selector":True}

    if option in ("emotes","reactions"):
        full_emotes=getAllEmotes(full_guilds)

    for i in curseur.execute("SELECT * FROM firstM ORDER BY Count DESC").fetchall():
        i["Rank"]=0

        if option in ("messages","voice","mots"):
            ligne=getUserTable(i,guild,roles_position,roles_color)

        elif option in ("emotes","reactions"):
           ligne=getEmoteTable(i,full_emotes)

        elif option in ("salons","voicechan"):
            ligne=getChannels(i)

        elif option=="freq":
            ligne=getFreq(i)

        ligne["Mois"]=i["Mois"]
        ligne["Annee"]=i["Annee"]
        statsM.append(ligne)

        maxiM=max(maxiM,i["Count"])

    for i in curseur.execute("SELECT * FROM firstA ORDER BY Count DESC").fetchall():
        i["Rank"]=0

        if option in ("messages","voice","mots"):
            ligne=getUserTable(i,guild,roles_position,roles_color)

        elif option in ("emotes","reactions"):
           ligne=getEmoteTable(i,full_emotes)

        elif option in ("salons","voicechan"):
            ligne=getChannels(i)

        elif option=="freq":
            ligne=getFreq(i)

        ligne["Mois"]=i["Mois"]
        ligne["Annee"]=i["Annee"]
        statsA.append(ligne)

        maxiA=max(maxiA,i["Count"])

    ctx["maxM"]=maxiM
    ctx["maxA"]=maxiA
    connexion.close()

    if option in ("messages","voice","mots"):
        return render(request, "companion/First/first.html", ctx)
    elif option in ("emotes","reactions"):
        return render(request, "companion/First/firstEmotes.html", ctx)
    else:
        return render(request, "companion/First/firstAutres.html", ctx)


@login_required(login_url="/login")
def iFrameFirst(request,guild,option):
    all=request.GET.get("data")
    mois,annee,id=all.split("?")
    mois=tableauMois[mois]
    annee="20"+annee
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    print(mois,annee,moisDB,anneeDB)
    user=request.user
    if id==None:
        id=user.id

    guild_full=getGuild(guild)

    roles_position,roles_color,roles_name=colorRoles(guild_full)
    
    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)

    table=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,id)).fetchall()
    table=collapseEvol(table)

    ctx={"rank":table,"id":user.id,"color":None,"max":None,"mois":mois,"annee":annee,"nom":None,"option":option}

    if option in ("messages","voice","mots"):
        user_full=getUser(guild,id)
        user_full["roles"].sort(key=lambda x:roles_position[x], reverse=True)
        if len(user_full["roles"])==0:
            ctx["color"]=None
        else:
            ctx["color"]="#{0}".format(hex(roles_color[user_full["roles"][0]])[2:])
        ctx["nom"]=user_full["user"]["username"]

    ctx["max"]=max(list(map(lambda x:x["Count"],table)))

    
    connexion.close()
    return render(request,"companion/Ranks/iFrameRanks_evol.html",ctx)
