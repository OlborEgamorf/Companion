from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..Getteurs import *
from ..outils import (avatarAnim, colorRoles, connectSQL, dictOptions,
                      getGuild, getGuilds, getMoisAnnee, getTablePerso,
                      getUser, tableauMois)


@login_required(login_url="/login")
def viewPeriods(request,guild,option):
    obj = request.GET.get("obj")
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)

    full_guilds=getGuilds(user)

    listeCateg=["Classements","Périodes","Évolution","Rôles","Jours","Rapports"]
    listeSections=["Accueil","Messages","Salons","Emotes","Vocal","Réactions","Mots","Fréquences"]
    dictRef={"Classements":"rank","Périodes":"periods","Évolution":"evol","Rôles":"roles","Jours":"jours","Rapport":"rapport"}
    
    ctx={"rankMois":None,"rankAnnee":None,"avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"maxM":None,"maxA":None,"guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"color":None,"guilds":full_guilds,"type":"Périodes","categs":listeCateg,"hrefs":dictRef,"travel":False,"sections":listeSections,"section":dictOptions[option],"selector":True,"option":option,"command":"periods"}

    if option in ("messages","voice","mots"):
        user_full["roles"].sort(key=lambda x:roles_position[x], reverse=True)
        if len(user_full["roles"])==0:
            ctx["color"]=None
        else:
            ctx["color"]="#{0}".format(hex(roles_color[user_full["roles"][0]])[2:])
        obj=False
    else:
        if option in ("emotes","reactions"):
            full_emotes=getAllEmotes(full_guilds)
        connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")
        listeObj=curseur.execute("SELECT * FROM persoTOGL{0} ORDER BY Count DESC".format(user.id)).fetchall()
        if option in ("emotes","reactions"):
            listeObj=list(map(lambda x:getEmoteTable(x,full_emotes),listeObj))
        elif option in ("salons","voicechan"):
            listeObj=list(map(lambda x:getChannels(x),listeObj))
        elif option=="freq":
            listeObj=list(map(lambda x:getFreq(x),listeObj))

        if obj==None:
            obj=listeObj[0]["ID"]
        
        ctx["obj"]=int(obj)
        ctx["listeObjs"]=listeObj

    ctx["rankMois"]=getTablePerso(guild,dictOptions[option],user.id,obj,"M","countDesc")
    ctx["rankAnnee"]=getTablePerso(guild,dictOptions[option],user.id,obj,"A","countDesc")

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
    ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee}
    return render(request, "companion/Ranks/iFrameRanks_ranks.html", ctx)
