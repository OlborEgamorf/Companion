from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..Getteurs import *
from ..outils import (avatarAnim, colorRoles, connectSQL, dictOptions,
                      dictRefCommands, dictRefOptions, getCommands, getGuild,
                      getGuilds, getMoisAnnee, getMoisAnneePerso, getTablePerso, getTimes, getUser,
                      listeOptions, tableauMois)


@login_required(login_url="/login")
def viewPerso(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnneePerso(mois,annee)
    moisGen,anneeGen,moisDBGen,anneeDBGen=getMoisAnnee(mois,annee)
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)

    full_guilds=getGuilds(user)
    listeMois,listeAnnee=getTimes(guild,option)

    stats=[]
    maxi=-inf
    
    ctx={"rank":stats,"max":None,
    "avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"color":None,
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":full_guilds,
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"perso",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "travel":True,"selector":True}

    user_full["roles"].sort(key=lambda x:roles_position[x], reverse=True)
    if len(user_full["roles"])!=0:
        ctx["color"]="#{0}".format(hex(roles_color[user_full["roles"][0]])[2:])

    if option in ("emotes","reactions"):
        full_emotes=getAllEmotes(full_guilds)

    print(moisDB,anneeDB)

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",moisDB,anneeDB)

    for i in curseur.execute("SELECT * FROM perso{0}{1}{2} ORDER BY Count DESC LIMIT 200".format(moisDB,anneeDB,user.id)).fetchall():


        if option in ("emotes","reactions"):
            ligne=getEmoteTable(i,full_emotes)

        elif option in ("salons","voicechan"):
            ligne=getChannels(i)

        elif option=="freq":
            ligne=getFreq(i)

        more=curseur.execute("SELECT * FROM {0}{1} WHERE ID={2}".format(moisDBGen,anneeDBGen,i["ID"])).fetchone()
        if more!=None:
            ligne["CountGen"]=more["Count"]
            ligne["RankGen"]=more["Rank"]
        stats.append(ligne)
        maxi=max(maxi,i["Count"])

    ctx["max"]=maxi
    if option in ("emotes","reactions"):
        return render(request, "companion/Perso/persoEmotes.html", ctx)
    else:
        return render(request, "companion/Perso/persoAutres.html", ctx)


@login_required(login_url="/login")
def iFramePerso(request,guild,option):
    obj=request.GET.get("data")
    user=request.user
    
    ctx={"rankMois":None,"rankAnnee":None,"maxM":None,"maxA":None,"color":None,"option":option}

    ctx["rankMois"]=getTablePerso(guild,dictOptions[option],user.id,obj,"M","countDesc")
    ctx["rankAnnee"]=getTablePerso(guild,dictOptions[option],user.id,obj,"A","countDesc")

    print(ctx["rankMois"])

    ctx["maxM"]=max(list(map(lambda x:x["Count"],ctx["rankMois"])))
    ctx["maxA"]=max(list(map(lambda x:x["Count"],ctx["rankAnnee"])))
    
    return render(request, "companion/Perso/iFramePerso.html", ctx)
