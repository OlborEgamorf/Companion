from math import inf

from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import render

from ..Getteurs import *
from ..outils import (avatarAnim, collapseEvol, connectSQL, dictOptions,
                      dictRefCommands, dictRefOptions, dictRefPlus,
                      getCommands, getGuild, getGuilds, getMoisAnnee, getPlus,
                      getTimes, getUser, listeOptions, tableauMois)


@login_required(login_url="/login")
def viewEvolCompare(request,guild,option):
    mois,annee,user2 = request.GET.get("mois"),request.GET.get("annee"),request.GET.get("obj")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]

    listeMois,listeAnnee=getTimes(guild,option,"Stats")

    full_guilds=getGuilds(user)

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

    infos2=getUserInfo(user2,curseurGet,guild)
    if infos2!=None:
        color2="#"+hex(infos2["Color"])[2:]
        avatar2=infos2["Avatar"]
        nom2=infos2["Nom"]
    else:
        color2,avatar2=None,None
        nom2="Ancien membre"

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
    
    table=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,user.id)).fetchall()
    table=collapseEvol(table)  
    table.reverse() 

    table2=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,user2)).fetchall()
    table2=collapseEvol(table2)  

    for i in range(len(table)):
        period=list(filter(lambda x:x["Mois"]==table[i]["Mois"] and x["Annee"]==table[i]["Annee"] and x["Jour"]==table[i]["Jour"],table2))
        if period!=[]:
            table[i]["Count2"]=period[0]["Count"]
            table[i]["Rank2"]=period[0]["Rank"]
            table[i]["Evol2"]=period[0]["Evol"]
            if not period[0]["Collapse"]:
                table[i]["Collapse"]=False

    maxi=max(max(list(map(lambda x:x["Count"],table))),max(list(map(lambda x:x["Count"],table2))))
    ctx={"rank":table,"max":maxi,
    "id":user.id,"color":None,"nom":user_full["user"]["username"],"avatar":user_avatar,"anim":avatarAnim(user_avatar),
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":full_guilds,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"evol",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("evol"),"dictPlus":dictRefPlus,"plus":"compare",
    "travel":True,"selector":True,"listeObjs":listeObj,"obj":int(user2),
    "user1ID":user.id,"user1Avatar":avatar1,"user1Nom":nom1,"user1Color":color1,"user2ID":user2,"user2Avatar":avatar2,"user2Nom":nom2,"user2Color":color2,}

    connexion.close()
    return render(request, "companion/Compare/evolCompare.html", ctx)
