from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..Getteurs import *
from ..outils import (avatarAnim, colorRoles, connectSQL, dictOptions,
                      dictRefCommands, dictRefOptions, getCommands, getGuild,
                      getGuilds, getMoisAnnee, getTablePerso, getUser,
                      listeOptions, tableauMois)


@login_required(login_url="/login")
def viewPeriods(request,guild,option):
    obj = request.GET.get("obj")
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)

    full_guilds=getGuilds(user)
    
    ctx={"rankMois":None,"rankAnnee":None,"maxM":None,"maxA":None,
    "avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"color":None,
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":full_guilds,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"periods",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "travel":False,"selector":True}

    user_full["roles"].sort(key=lambda x:roles_position[x], reverse=True)
    if len(user_full["roles"])==0:
        ctx["color"]=None
    else:
        ctx["color"]="#{0}".format(hex(roles_color[user_full["roles"][0]])[2:])

    ctx["rankMois"]=getTablePerso(guild,dictOptions[option],user.id,False,"M","countDesc")
    ctx["rankAnnee"]=getTablePerso(guild,dictOptions[option],user.id,False,"A","countDesc")

    ctx["maxM"]=max(list(map(lambda x:x["Count"],ctx["rankMois"])))
    ctx["maxA"]=max(list(map(lambda x:x["Count"],ctx["rankAnnee"])))
    
    return render(request, "companion/periods.html", ctx)


@login_required(login_url="/login")
def iFramePeriods(request,guild,option):
    all=request.GET.get("data")
    mois,annee,obj=all.split("?")
    if len(annee)==4:
        mois=tableauMois[mois.lower()]
        annee=annee[2:4]
    if annee not in ("GL","Global"):
        annee="20"+annee
    mois,annee,moisDB,anneeDB=getMoisAnnee(tableauMois[mois],annee)
    print(mois,annee,moisDB,anneeDB)
    user=request.user

    guild_full=getGuild(guild)
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)

    if obj=="None":
        obj=""
    
    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
    rank=curseur.execute("SELECT Rank FROM {0}{1}{2} WHERE ID={3}".format(moisDB.lower(),anneeDB,obj,user.id)).fetchone()["Rank"]

    rankPlus=rank-10
    rankMoins=rank+10

    if rankPlus<0:
        rankMoins-=rankPlus

    maxi=-inf
    stats=[]

    for i in curseur.execute("SELECT * FROM {0}{1}{2} WHERE (Rank>={3} AND Rank<={4}) OR Rank=1 ORDER BY Rank ASC".format(moisDB.lower(),anneeDB,obj,rankPlus,rankMoins)).fetchall():

        stats.append(getUserTable(i,guild,roles_position,roles_color))
        maxi=max(maxi,i["Count"])
    
    connexion.close()
    ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"option":option}
    return render(request, "companion/Ranks/iFrameRanks_ranks.html", ctx)
