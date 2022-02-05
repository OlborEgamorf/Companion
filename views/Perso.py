from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..Getteurs import *
from ..outils import (avatarAnim, connectSQL, dictOptions, dictRefCommands,
                      dictRefOptions, dictRefPlus, getCommands, getGuild,
                      getGuilds, getMoisAnnee, getMoisAnneePerso, getPlus,
                      getTablePerso, getTimes, getUser, listeOptions)


@login_required(login_url="/login")
def viewPerso(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnneePerso(mois,annee)
    moisGen,anneeGen,moisDBGen,anneeDBGen=getMoisAnnee(mois,annee)
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]

    full_guilds=getGuilds(user)
    listeMois,listeAnnee=getTimes(guild,option)

    stats=[]
    maxi=-inf

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    
    ctx={"rank":stats,"max":None,
    "avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"color":getColor(user.id,guild,curseurGet),
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":full_guilds,
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"perso",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("perso"),"dictPlus":dictRefPlus,"plus":"",
    "travel":True,"selector":True}

    print(moisDB,anneeDB)

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",moisDB,anneeDB)

    for i in curseur.execute("SELECT * FROM perso{0}{1}{2} ORDER BY Count DESC LIMIT 200".format(moisDB,anneeDB,user.id)).fetchall():

        if option in ("emotes","reactions"):
            ligne=getEmoteTable(i,curseurGet)

        elif option in ("salons","voicechan"):
            ligne=getChannels(i,curseurGet)

        elif option=="freq":
            ligne=getFreq(i)

        more=curseur.execute("SELECT * FROM {0}{1} WHERE ID={2}".format(moisDBGen,anneeDBGen,i["ID"])).fetchone()
        if more!=None:
            ligne["CountGen"]=more["Count"]
            ligne["RankGen"]=more["Rank"]
        stats.append(ligne)
        maxi=max(maxi,i["Count"])

    ctx["max"]=maxi
    return render(request, "companion/Perso/perso.html", ctx)


@login_required(login_url="/login")
def iFramePerso(request,guild,option):
    obj=request.GET.get("data")
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    
    ctx={"rankMois":None,"rankAnnee":None,"maxM":None,"maxA":None,"color":None,"option":option,"color":getColor(user.id,guild,curseurGet)}

    ctx["rankMois"]=getTablePerso(guild,dictOptions[option],user.id,obj,"M","countDesc")
    ctx["rankAnnee"]=getTablePerso(guild,dictOptions[option],user.id,obj,"A","countDesc")

    ctx["maxM"]=max(list(map(lambda x:x["Count"],ctx["rankMois"])))
    ctx["maxA"]=max(list(map(lambda x:x["Count"],ctx["rankAnnee"])))
    
    return render(request, "companion/Perso/iFramePerso.html", ctx)
