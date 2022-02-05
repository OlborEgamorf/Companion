from math import inf
from random import choice

from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import render

from ..Getteurs import *
from ..outils import (avatarAnim, connectSQL, dictOptions, dictRefCommands,
                      dictRefOptions, dictRefPlus, getCommands, getGuild,
                      getGuilds, getPlus, getTimes, getUser, listeOptions)


@login_required(login_url="/login")
def viewFirstCompare(request,guild,option):
    annee1 = request.GET.get("annee1")
    annee2 = request.GET.get("annee2")
    listeAnnee=getTimes(guild,option)[1]
    listeAnnee.remove("Global")
    if annee1==None:
        annee1=choice(listeAnnee)
    anneeDB1=annee1[2:4]
    if annee2==None:
        annee2=choice(listeAnnee)
    anneeDB2=annee2[2:4]
    print(anneeDB1,anneeDB2)
    user=request.user

    guild_full=getGuild(guild)

    maxi=-inf
    maxiA=-inf
    stats1=[]
    stats2=[]

    if option!="freq":
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","TO","GL")

    for i in curseur.execute("SELECT * FROM firstM WHERE Annee={0} ORDER BY Mois ASC".format(anneeDB1)).fetchall()+curseur.execute("SELECT * FROM firstA WHERE Annee={0}".format(anneeDB1)).fetchall():

        i["Rank"]=0

        if option in ("messages","voice","mots"):
            ligne=getUserTable(i,curseurGet,guild)

        elif option in ("emotes","reactions"):
           ligne=getEmoteTable(i,curseurGet)

        elif option in ("salons","voicechan"):
            ligne=getChannels(i,curseurGet)

        elif option=="freq":
            ligne=getFreq(i)

        ligne["Mois"]=i["Mois"]
        ligne["Annee"]=i["Annee"]
        stats1.append(ligne)

        if i["Mois"]=="TO":
            maxiA=max(maxiA,i["Count"])
        else:
            maxi=max(maxi,i["Count"])

    for i in curseur.execute("SELECT * FROM firstM WHERE Annee={0} ORDER BY Mois ASC".format(anneeDB2)).fetchall()+curseur.execute("SELECT * FROM firstA WHERE Annee={0}".format(anneeDB2)).fetchall():
        
        i["Rank"]=0

        if option in ("messages","voice","mots"):
            ligne=getUserTable(i,curseurGet,guild)

        elif option in ("emotes","reactions"):
           ligne=getEmoteTable(i,curseurGet)

        elif option in ("salons","voicechan"):
            ligne=getChannels(i,curseurGet)

        elif option=="freq":
            ligne=getFreq(i)

        ligne["Mois"]=i["Mois"]
        ligne["Annee"]=i["Annee"]
        stats2.append(ligne)

        if i["Mois"]=="TO":
            maxiA=max(maxiA,i["Count"])
        else:
            maxi=max(maxi,i["Count"])

    connexion.close()


    for i in range(len(stats1)):
        period=list(filter(lambda x:x["Mois"]==stats1[i]["Mois"],stats2))
        print(period)
        if period!=[]:
            stats1[i]["Nom2"]=period[0]["Nom"]
            stats1[i]["Avatar2"]=period[0]["Avatar"]
            stats1[i]["Count2"]=period[0]["Count"]
            stats1[i]["Color2"]=period[0]["Color"]
            stats1[i]["ID2"]=period[0]["ID"]

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]
    full_guilds=getGuilds(user)

    ctx={"rank":stats1,"max":maxi,"maxA":maxiA,
    "avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":full_guilds,
    "mois1":"Total","annee1":annee1,"mois2":"Total","annee2":annee2,"listeMois":["Total"],"listeAnnee":listeAnnee,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"ranks",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("first"),"dictPlus":dictRefPlus,"plus":"compare",
    "travel":False,"selector":True,"obj":None}

    return render(request, "companion/Compare/firstCompare.html", ctx)
