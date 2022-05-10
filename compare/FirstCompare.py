from math import inf
from random import choice

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..Getteurs import *
from ..outils import (connectSQL, dictOptions, dictRefCommands, dictRefOptions,
                      dictRefPlus, getCommands, getPlus, getTimes,
                      listeOptions)


@login_required(login_url="/login")
def viewFirstCompare(request,guild,option):
    annee1 = request.GET.get("annee1")
    annee2 = request.GET.get("annee2")
    listeAnnee=getTimes(guild,option,"Stats")[1]
    listeAnnee.remove("Global")
    if annee1==None:
        annee1=choice(listeAnnee)
    anneeDB1=annee1[2:4]
    if annee2==None:
        annee2=choice(listeAnnee)
    anneeDB2=annee2[2:4]
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    maxi=-inf
    maxiA=-inf
    stats1=[]
    stats2=[]

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
            stats1[i]["ID2"]=period[0]["ID"]
            stats1[i]["Count2"]=period[0]["Count"]
            if option in ("messages","voice","mots"):
                stats1[i]["Avatar2"]=period[0]["Avatar"]
                stats1[i]["Color2"]=period[0]["Color"]

    ctx={"rank":stats1,"max":maxi,"maxA":maxiA,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "mois1":"Total","annee1":annee1,"mois2":"Total","annee2":annee2,"listeMois":["Total"],"listeAnnee":listeAnnee,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"first",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("first",option),"dictPlus":dictRefPlus,"plus":"compare",
    "travel":False,"selector":True,"obj":None}

    return render(request, "companion/Compare/firstCompare.html", ctx)
