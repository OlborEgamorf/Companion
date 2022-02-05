from math import inf

from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import render

from ..Getteurs import *
from ..outils import (avatarAnim, connectSQL, dictOptions,
                      dictRefCommands, dictRefOptions, getCommands, getGuild,
                      getGuilds, getPlus, getTablePerso, getUser, listeOptions, dictRefPlus)

@login_required(login_url="/login")
def viewPeriodsCompare(request,guild,option):
    user2 = request.GET.get("obj")
    user=request.user

    guild_full=getGuild(guild)

    maxi=-inf

    if option!="freq":
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")
    listeObj=curseur.execute("SELECT * FROM glob ORDER BY Count DESC").fetchall()
    if option in ("emotes","reactions"):
        listeObj=list(map(lambda x:getEmoteTable(x,curseurGet),listeObj))
    elif option in ("salons","voicechan"):
        listeObj=list(map(lambda x:getChannels(x,curseurGet),listeObj))
    elif option=="freq":
        listeObj=list(map(lambda x:getFreq(x),listeObj))
    elif option in ("messages","voice","mots"):
        listeObj=list(map(lambda x:getUserTable(x,curseurGet,guild),listeObj))

    listeObj=list(filter(lambda x:x["ID"]!=user.id,listeObj))

    if user2==None:
        user2=listeObj[0]["ID"]

    infos1=getUserInfo(user.id,curseurGet,guild)
    if infos1!=None:
        color1="#"+hex(infos1["Color"])[2:]
        avatar1=infos1["Avatar"]
        nom1=infos1["Nom"]
    else:
        color1,avatar1=None,None
        nom1="Vous"
    rankMois1=getTablePerso(guild,dictOptions[option],user.id,False,"M","countDesc")
    rankAnnee1=getTablePerso(guild,dictOptions[option],user.id,False,"A","countDesc")

    infos2=getUserInfo(user2,curseurGet,guild)
    if infos2!=None:
        color2="#"+hex(infos2["Color"])[2:]
        avatar2=infos2["Avatar"]
        nom2=infos2["Nom"]
    else:
        color2,avatar2=None,None
        nom2="Ancien membre"
    rankMois2=getTablePerso(guild,dictOptions[option],user2,False,"M","countDesc")
    rankAnnee2=getTablePerso(guild,dictOptions[option],user2,False,"A","countDesc")

    maxiM=max(list(map(lambda x:x["Count"],rankMois1))+list(map(lambda x:x["Count"],rankMois2)))
    maxiA=max(list(map(lambda x:x["Count"],rankAnnee1))+list(map(lambda x:x["Count"],rankAnnee2)))

    for i in range(len(rankMois1)):
        period=list(filter(lambda x:x["Mois"]==rankMois1[i]["Mois"] and x["Annee"]==rankMois1[i]["Annee"],rankMois2))
        if period!=[]:
            rankMois1[i]["Count2"]=period[0]["Count"]
            rankMois1[i]["Rank2"]=period[0]["Rank"]
    for i in range(len(rankAnnee1)):
        period=list(filter(lambda x:x["Annee"]==rankAnnee1[i]["Annee"],rankAnnee2))
        if period!=[]:
            rankAnnee1[i]["Count2"]=period[0]["Count"]
            rankAnnee1[i]["Rank2"]=period[0]["Rank"]
        
    full_guilds=getGuilds(user)

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]

    ctx={"rankMois":rankMois1,"rankAnnee":rankAnnee1,"maxM":maxiM,"maxA":maxiA,
    "avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"color":None,
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":full_guilds,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"periods",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("periods"),"dictPlus":dictRefPlus,"plus":"compare",
    "travel":False,"selector":True,"listeObjs":listeObj,"obj":int(user2),
    "user1ID":user.id,"user1Avatar":avatar1,"user1Nom":nom1,"user1Color":color1,"user2ID":user2,"user2Avatar":avatar2,"user2Nom":nom2,"user2Color":color2}

    return render(request, "companion/Compare/periodsCompare.html", ctx)