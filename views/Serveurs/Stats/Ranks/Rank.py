from math import inf

from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import *
from companion.tools.outils import (collapseEvol, connectSQL, dictOptions,
                              getMoisAnnee, getTimes, listeOptions,
                              listeOptionsJeux, tableauMois)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def rankJeux(request,option):
    return viewRank(request,"OT",option)

def iFrameRankJeux(request,option):
    return iFrameRank(request,"OT",option)

@login_required(login_url="/login")
@CompanionStats
def viewRank(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    maxi=-inf
    stats=[]

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        pin=getPin(user,curseurGet,"ot/jeux",option,"ranks","")
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
    else:
        pin=getPin(user,curseurGet,guild,option,"ranks","")
        categ="Stats"
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)

    for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT 150".format(moisDB,anneeDB)).fetchall():

        stats.append(chooseGetteur(option,categ,i,guild,curseurGet,curseurGuild))

        maxi=max(maxi,i["Count"])

    connexion.close()

    if maxi<=0:
        maxi=1

    if categ=="Jeux":
        listeMois,listeAnnee=getTimes(guild,option,"Jeux")
        ctx={"rank":stats,"max":maxi,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":"Classements Jeux","guildid":"ot/jeux",
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "command":"ranks","options":listeOptionsJeux,"option":option,"plus":"","travel":True,"selector":True,"obj":None,"pin":pin,
        "pagestats":True,"ot":True}
        return render(request, "companion/Stats/Ranks/ranks.html", ctx)
    else:
        listeMois,listeAnnee=getTimes(guild,option,"Stats")

        ctx={"rank":stats,"max":maxi,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "command":"ranks","options":listeOptions,"option":option,"plus":"" if option in ("messages","voice","mots") else "serv",
        "travel":True,"selector":True,"obj":None,"pagestats":True,
        "pin":pin}

        if option=="divers":
            return render(request, "companion/Stats/Ranks/ranksDivers.html", ctx)
        else:
            return render(request, "companion/Stats/Ranks/ranks.html", ctx)

@login_required(login_url="/login")
@CompanionStats
def viewRankObj(request,guild,option):
    mois,annee,obj = request.GET.get("mois"),request.GET.get("annee"),request.GET.get("obj")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    maxi=-inf
    stats=[]

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    listeObj=objSelector(guild,option,"Stats",user,curseurGet,curseurGuild)
        
    if obj==None:
        obj=str(listeObj[0]["ID"])
    
    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)

    for i in curseur.execute("SELECT * FROM {0}{1}{2} ORDER BY Rank ASC LIMIT 150".format(moisDB,anneeDB,obj)).fetchall():

        ligne=getUserTable(i,curseurGet,curseurGuild,guild)
        if option=="divers" and obj=="11":
            ligne["Count"]=tempsVoice(i["Count"])

        stats.append(ligne)
        maxi=max(maxi,i["Count"])

    connexion.close()

    if maxi<=0:
        maxi=1

    listeMois,listeAnnee=getTimes(guild,option,"Stats")

    ctx={"rank":stats,"max":maxi,"pagestats":True,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "command":"ranks","options":listeOptions,"option":option,"plus":"obj",
    "travel":True,"selector":True,"obj":int(obj),"listeObjs":listeObj,
    "pin":getPin(user,curseurGet,guild,option,"ranks","obj"),"pagestats":True}

    return render(request, "companion/Stats/Ranks/ranks.html", ctx)


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
            color=infos["Color"]
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
        return render(request,"companion/Stats/Ranks/iFrameRanks_evol.html",ctx)

    else:
        connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
        nom=getNom(obj,option,curseurGet,False)
        try:
            maxi=-inf
            stats=[]
            for i in curseur.execute("SELECT * FROM {0}{1}{2} ORDER BY Rank ASC LIMIT 150".format(moisDB,anneeDB,obj)).fetchall():
                stats.append(getUserTable(i,curseurGet,curseurGuild,guild))
                maxi=max(maxi,i["Count"])
        except:
            pass

        ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"option":option,"obj":obj,"nom":nom}
        return render(request, "companion/Stats/Ranks/iFrameRanks_ranks.html", ctx)
