from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companion.Getteurs import *
from companion.outils import (connectSQL, dictOptions,
                      dictRefCommands, dictRefOptions, getCommands,
                      getPlus, getTablePerso, listeOptions, dictRefPlus)

@login_required(login_url="/login")
def viewPeriodsCompare(request,guild,option):
    user=request.user
    if option in ("messages","voice","mots"):
        obj1=user.id
        obj2 = request.GET.get("obj")
    else:
        obj1 = request.GET.get("obj")
        obj2 = request.GET.get("obj2")

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

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
    listeObj=list(filter(lambda x:x["Nom"]!="Ancien membre",listeObj))

    if len(listeObj)>150:
        listeObj=listeObj[:150]

    if obj1==None:
        obj1=listeObj[1]["ID"]
    if obj2==None:
        obj2=listeObj[0]["ID"]

    if option in ("messages","voice","mots"): 
        rankMois1=getTablePerso(guild,dictOptions[option],user.id,False,"M","countDesc")
        rankAnnee1=getTablePerso(guild,dictOptions[option],user.id,False,"A","countDesc")
        rankMois2=getTablePerso(guild,dictOptions[option],obj2,False,"M","countDesc")
        rankAnnee2=getTablePerso(guild,dictOptions[option],obj2,False,"A","countDesc")
    else:
        rankMois1=getTablePerso(guild,dictOptions[option],user.id,obj1,"M","countDesc")
        rankAnnee1=getTablePerso(guild,dictOptions[option],user.id,obj1,"A","countDesc")
        rankMois2=getTablePerso(guild,dictOptions[option],user.id,obj2,"M","countDesc")
        rankAnnee2=getTablePerso(guild,dictOptions[option],user.id,obj2,"A","countDesc")

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

    ctx={"rankMois":rankMois1,"rankAnnee":rankAnnee1,"maxM":maxiM,"maxA":maxiA,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"color":None,
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"periods",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("periods",option),"dictPlus":dictRefPlus,"plus":"compareperso",
    "travel":False,"selector":True,"listeObjs":listeObj,"obj":int(obj2),
    "user1ID":int(obj1),"user2ID":int(obj2),
    "pin":getPin(user,curseurGet,guild,option,"periods","compareperso")}

    if option in ("messages","voice","mots"):
        infos1=getUserInfo(obj1,curseurGet,guild)
        if infos1!=None:
            ctx["user1Color"]="#"+hex(infos1["Color"])[2:]
            ctx["user1Avatar"]=infos1["Avatar"]
            ctx["user1Nom"]=infos1["Nom"]
        else:
            ctx["user1Nom"]="Vous"
    
        infos2=getUserInfo(obj2,curseurGet,guild)
        if infos2!=None:
            ctx["user2Color"]="#"+hex(infos2["Color"])[2:]
            ctx["user2Avatar"]=infos2["Avatar"]
            ctx["user2Nom"]=infos2["Nom"]
        else:
            ctx["user2Nom"]="Ancien membre"
    else:
        ctx["user1Nom"]=getNom(obj1,option,curseurGet,False)
        ctx["user2Nom"]=getNom(obj2,option,curseurGet,False)
        color=getColor(user.id,guild,curseurGet)
        ctx["user1Color"]=color
        ctx["user2Color"]=color
        ctx["obj"]=None

    return render(request, "companion/Compare/periodsCompare.html", ctx)