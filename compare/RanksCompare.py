from math import inf

from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import render

from ..Getteurs import *
from ..outils import (avatarAnim, connectSQL, dictOptions,
                      dictRefCommands, dictRefOptions, getCommands, getGuild,
                      getGuilds, getMoisAnnee, getPlus, getTimes, getUser, listeOptions,
                      tableauMois, dictRefPlus)

@login_required(login_url="/login")
def viewRankCompare(request,guild,option):
    mois1,annee1 = request.GET.get("mois1"),request.GET.get("annee1")
    mois2,annee2 = request.GET.get("mois2"),request.GET.get("annee2")
    mois1,annee1,moisDB1,anneeDB1=getMoisAnnee(mois1,annee1)
    mois2,annee2,moisDB2,anneeDB2=getMoisAnnee(mois2,annee2)
    user=request.user

    guild_full=getGuild(guild)

    maxi=-inf
    stats1=[]
    stats2=[]

    if option!="freq":
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB1],anneeDB1)

    for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT 150".format(moisDB1,anneeDB1)).fetchall():

        if option in ("messages","voice","mots"):
            stats1.append(getUserTable(i,curseurGet,guild))

        elif option in ("emotes","reactions"):
            stats1.append(getEmoteTable(i,curseurGet))

        elif option in ("salons","voicechan"):
            stats1.append(getChannels(i,curseurGet))

        elif option=="freq":
            stats1.append(getFreq(i))

        maxi=max(maxi,i["Count"])

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB2],anneeDB2)

    for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT 150".format(moisDB2,anneeDB2)).fetchall():

        if option in ("messages","voice","mots"):
            stats2.append(getUserTable(i,curseurGet,guild))

        elif option in ("emotes","reactions"):
            stats2.append(getEmoteTable(i,curseurGet))

        elif option in ("salons","voicechan"):
            stats2.append(getChannels(i,curseurGet))

        elif option=="freq":
            stats2.append(getFreq(i))

        maxi=max(maxi,i["Count"])

    connexion.close()

    for i in range(len(stats2)):
        if i<len(stats1):
            stats1[i]["Nom2"]=stats2[i]["Nom"]
            stats1[i]["Count2"]=stats2[i]["Count"]
            stats1[i]["ID2"]=stats2[i]["ID"]
            if option in ("messages","voice","mots"): 
                stats1[i]["Color2"]=stats2[i]["Color"]
                stats1[i]["Avatar2"]=stats2[i]["Avatar"]
            elif option in ("emotes","reactions"):
                 stats1[i]["Animated2"]=stats2[i]["Animated"]

            try:
                stats1[i]["Evol"]=list(filter(lambda x:stats2[i]["ID"]==x["ID"], stats1))[0]["Rank"]-stats2[i]["Rank"]
            except:
                stats1[i]["Evol"]=0
            stats1[i]["Rank"]=i+1
        else:
            try:
                evol=list(filter(lambda x:stats2[i]["ID"]==x["ID"], stats1))[0]["Rank"]-stats2[i]["Rank"]
            except:
                evol=0
                if option in ("messages","voice","mots"):
                    stats1.append({"Nom2":stats2[i]["Nom"],"Count2":stats2[i]["Count"],"Avatar2":stats2[i]["Avatar"],"Color2":stats2[i]["Color"],"ID2":stats2[i]["ID"],"Evol":evol,"Rank":i+1})
                elif option in ("emotes","reactions"):
                    stats1.append({"Nom2":stats2[i]["Nom"],"Count2":stats2[i]["Count"],"Animated2":stats2[i]["Animated"],"ID2":stats2[i]["ID"],"Evol":evol,"Rank":i+1})
                else:
                    stats1.append({"Nom2":stats2[i]["Nom"],"Count2":stats2[i]["Count"],"ID2":stats2[i]["ID"],"Evol":evol,"Rank":i+1}) 

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]
    full_guilds=getGuilds(user)
    listeMois,listeAnnee=getTimes(guild,option)

    ctx={"rank":stats1,"max":maxi,
    "avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":full_guilds,
    "mois1":mois1,"annee1":annee1,"mois2":mois2,"annee2":annee2,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"ranks",
    "lisPlus":getPlus("ranks"),"dictPlus":dictRefPlus,"plus":"compare",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "travel":False,"selector":True,"obj":None}

    return render(request, "companion/Compare/ranksCompare.html", ctx)