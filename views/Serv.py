from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..Getteurs import *
from ..outils import (avatarAnim, connectSQL, dictOptions,
                      dictRefCommands, dictRefOptions, getCommands, getGuild,
                      getGuilds, getMoisAnnee, getPlus, getTablePerso, getUser,
                      listeOptions, tableauMois,dictRefPlus)


@login_required(login_url="/login")
def viewServ(request,guild,option):
    obj = request.GET.get("obj")
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]

    full_guilds=getGuilds(user)
    
    ctx={"rankMois":None,"rankAnnee":None,"maxM":None,"maxA":None,
    "avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"color":None,
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":full_guilds,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"serv",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("evol"),"dictPlus":dictRefPlus,"plus":"",
    "selector":True,"travel":False,}

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")

    if option!="freq":
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
        
    listeObj=curseur.execute("SELECT * FROM glob ORDER BY Count DESC").fetchall()
    if option in ("emotes","reactions"):
        listeObj=list(map(lambda x:getEmoteTable(x,curseurGet),listeObj))
    elif option in ("salons","voicechan"):
        listeObj=list(map(lambda x:getChannels(x,curseurGet),listeObj))
    elif option=="freq":
        listeObj=list(map(lambda x:getFreq(x),listeObj))

    if obj==None:
        obj=listeObj[0]["ID"]
    
    ctx["obj"]=int(obj)
    ctx["listeObjs"]=listeObj

    ctx["rankMois"]=getTablePerso(guild,dictOptions[option],obj,False,"M","countDesc")
    ctx["rankAnnee"]=getTablePerso(guild,dictOptions[option],obj,False,"A","countDesc")

    ctx["maxM"]=max(list(map(lambda x:x["Count"],ctx["rankMois"])))
    ctx["maxA"]=max(list(map(lambda x:x["Count"],ctx["rankAnnee"])))
    
    return render(request, "companion/periods.html", ctx)


@login_required(login_url="/login")
def iFrameServ(request,guild,option):
    all=request.GET.get("data")
    mois,annee,obj=all.split("?")
    if len(annee)==4:
        mois=tableauMois[mois.lower()]
        annee=annee[2:4]
    if annee not in ("GL","Global"):
        annee="20"+annee
    mois,annee,moisDB,anneeDB=getMoisAnnee(tableauMois[mois],annee)
    user=request.user
    
    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)

    if option!="freq":
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    rank=curseur.execute("SELECT Rank FROM {0}{1} WHERE ID={2}".format(moisDB.lower(),anneeDB,obj)).fetchone()["Rank"]

    rankPlus=rank-10
    rankMoins=rank+10

    if rankPlus<0:
        rankMoins-=rankPlus

    maxi=-inf
    stats=[]

    for i in curseur.execute("SELECT * FROM {0}{1} WHERE (Rank>={2} AND Rank<={3}) OR Rank=1 ORDER BY Rank ASC".format(moisDB.lower(),anneeDB,rankPlus,rankMoins)).fetchall():

        if option in ("emotes","reactions"):
            stats.append(getEmoteTable(i,curseurGet))
        elif option in ("salons","voicechan"):
            stats.append(getChannels(i,curseurGet))
        elif option=="freq":
            stats.append(getFreq(i))

        maxi=max(maxi,i["Count"])
    
    connexion.close()
    ctx={"rank":stats,"id":int(obj),"max":maxi,"mois":mois,"annee":annee,"option":option}
    return render(request, "companion/Serv/iFrameServ.html", ctx)