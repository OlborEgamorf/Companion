from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companion.Getteurs import *
from companion.outils import (collapseEvol, connectSQL, dictOptions, dictRefCommands,
                      dictRefOptions, dictRefOptionsJeux, dictRefPlus,
                      getCommands, getMoisAnnee, getPlus,
                      getTimes, listeOptions, listeOptionsJeux,
                      tableauMois)


def rankJeux(request,option):
    return viewRank(request,"OT",option)

def iFrameRankJeux(request,option):
    return iFrameRank(request,"OT",option)

@login_required(login_url="/login")
def viewRank(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    maxi=-inf
    stats=[]

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
    else:
        categ="Stats"
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)

    for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT 150".format(moisDB,anneeDB)).fetchall():

        if option in ("messages","voice","mots"):
            stats.append(getUserTable(i,curseurGet,guild))

        elif option in ("emotes","reactions"):
            stats.append(getEmoteTable(i,curseurGet))

        elif option in ("salons","voicechan"):
            stats.append(getChannels(i,curseurGet))

        elif option=="freq":
            stats.append(getFreq(i))

        elif option=="divers":
            stats.append(getDivers(i))
        
        elif categ=="Jeux":
            stats.append(getUserJeux(i,curseurGet,option))

        maxi=max(maxi,i["Count"])

    connexion.close()

    if maxi<=0:
        maxi=1

    if "/mix/" in request.path:
        return {"rank":stats,"guildicon":guild_full["icon"],"guildname":guild_full["name"],"guildid":guild}
    elif categ=="Jeux":
        listeMois,listeAnnee=getTimes(guild,option,"Jeux")
        ctx={"rank":stats,"max":maxi,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":"Olbor Track - Mondial","guildid":"jeux",
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "commands":["ranks","periods","evol","first","badges"],"dictCommands":dictRefCommands,"command":"ranks",
        "options":listeOptionsJeux,"dictOptions":dictRefOptionsJeux,"option":option,
        "lisPlus":getPlus("ranks",option),"dictPlus":dictRefPlus,"plus":"",
        "travel":True,"selector":True,"obj":None}
        return render(request, "companion/Ranks/ranks.html", ctx)
    else:
        listeMois,listeAnnee=getTimes(guild,option,"Stats")

        ctx={"rank":stats,"max":maxi,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"ranks",
        "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
        "lisPlus":getPlus("ranks",option),"dictPlus":dictRefPlus,"plus":"" if option in ("messages","voice","mots") else "serv",
        "travel":True,"selector":True,"obj":None}

        if option=="divers":
            return render(request, "companion/Ranks/ranksDivers.html", ctx)
        else:
            return render(request, "companion/Ranks/ranks.html", ctx)

@login_required(login_url="/login")
def viewRankObj(request,guild,option):
    mois,annee,obj = request.GET.get("mois"),request.GET.get("annee"),request.GET.get("obj")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    maxi=-inf
    stats=[]

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
    elif option=="divers":
        listeObj=list(map(lambda x:getDivers(x),listeObj))
        
    if obj==None:
        obj=str(listeObj[0]["ID"])

    if len(listeObj)>150:
        listeObj=listeObj[:150]
    
    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)

    for i in curseur.execute("SELECT * FROM {0}{1}{2} ORDER BY Rank ASC LIMIT 150".format(moisDB,anneeDB,obj)).fetchall():

        ligne=getUserTable(i,curseurGet,guild)
        if option=="divers" and obj=="11":
            ligne["Count"]=tempsVoice(i["Count"])

        stats.append(ligne)
        maxi=max(maxi,i["Count"])

    connexion.close()

    if maxi<=0:
        maxi=1

    listeMois,listeAnnee=getTimes(guild,option,"Stats")

    ctx={"rank":stats,"max":maxi,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"ranks",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("ranks",option),"dictPlus":dictRefPlus,"plus":"obj",
    "travel":True,"selector":True,"obj":int(obj),"listeObjs":listeObj}

    return render(request, "companion/Ranks/ranks.html", ctx)


@login_required(login_url="/login")
def iFrameRank(request,guild,option):
    all=request.GET.get("data")
    mois,annee,obj=all.split("?")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user
    if obj==None:
        obj=user.id
    
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
    else:
        categ="Stats"
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)
    
    if option in ("messages","mots","voice") or categ=="Jeux":
        
        if categ=="Jeux":
            connexionUser,curseurUser=connectSQL("OT",obj,"Titres",None,None)
            infos=getAllInfos(curseurGet,curseurUser,connexionUser,obj)
            nom=infos["Full"]
            color=infos["Couleur"]
        else:
            user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(obj)).fetchone()
            color=getColor(obj,guild,curseurGet)
            nom=user_full["Nom"]

        stats=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,obj)).fetchall()
        stats=collapseEvol(stats)
        stats.reverse()   
        stats=list(filter(lambda x:not x["Collapse"], stats))     
        maxi=max(list(map(lambda x:x["Count"],stats)))
        if maxi<0:
            maxi=1
        ctx={"rank":stats,"id":user.id,"color":color,"max":maxi,"mois":mois,"annee":annee,"nom":nom,"option":option}
        return render(request,"companion/Ranks/iFrameRanks_evol.html",ctx)

    else:

        maxi=-inf
        stats=[]
        for i in curseur.execute("SELECT * FROM {0}{1}{2} ORDER BY Rank ASC LIMIT 150".format(moisDB,anneeDB,obj)).fetchall():
            stats.append(getUserTable(i,curseurGet,guild))
            maxi=max(maxi,i["Count"])

        ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"option":option}
        return render(request, "companion/Ranks/iFrameRanks_ranks.html", ctx)
