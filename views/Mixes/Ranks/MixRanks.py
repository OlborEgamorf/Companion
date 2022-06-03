from math import inf

from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, dictOptions, getMoisAnnee,
                              getTimesMix, listeOptions, rankingClassic,
                              tableauMois)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
def mixRank(request,mix,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    maxi=-inf
    dictStats={}

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    
    mix_ids,infosMix,listeMixs=getInfoMix(user,mix,curseurGet)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    for guild in mix_ids:
        try:
            connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
            for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT 1000".format(moisDB,anneeDB)).fetchall():
                if i["ID"] not in dictStats:
                    dictStats[i["ID"]]=i["Count"]
                else:
                    dictStats[i["ID"]]+=i["Count"]
        except:
            pass
    
    stats=list(map(lambda x:{"ID":x,"Count":dictStats[x]},dictStats))
    assert stats!=[]
    stats.sort(key=lambda x:x["Count"],reverse=True)
    if len(stats)>150:
        stats=stats[:150]
    rankingClassic(stats)

    for i in stats:
        if option in ("messages","voice","mots"):
            infos=getUserInfoMix(i["ID"],mix_ids,curseurGet)
            i["Nom"]=infos["Nom"]
            i["Avatar"]=infos["Avatar"]
        elif option in ("emotes","reactions"):
            infos=getEmoteTable(i,curseurGet)
            i["Nom"]=infos["Nom"]
        else:
            i["Nom"]=getNom(i["ID"],option,curseurGet,False)

        maxi=max(maxi,i["Count"])

    connexion.close()

    if maxi<=0:
        maxi=1

    listeMois,listeAnnee=getTimesMix(mix_ids,option)

    ctx={"rank":stats,"max":maxi,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,"guildname":infosMix["Nom"],"guildid":"mixes/{0}".format(infosMix["Nombre"]),
    "command":"ranks","options":listeOptions,"option":option,"plus":"" if option in ("messages","voice","mots") else "serv",
    "travel":True,"selector":True,"obj":None,"mix":True,"listeMix":listeMixs,"nbmix":infosMix["Nombre"],
    "pin":getPin(user,curseurGet,"mixes/{0}".format(infosMix["Nombre"]),option,"ranks","")}

    return render(request, "companion/Stats/Ranks/ranks.html", ctx)



@login_required(login_url="/login")
def iFrameMixRank(request,mix,option):
    all=request.GET.get("data")
    mois,annee,obj=all.split("?")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user
    if obj=="None" or obj==None:
        obj=user.id
    
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    mix_ids,infosMix,listeMixs=getInfoMix(user,mix,curseurGet)

    stats=[]
    maxi=-inf
    nom=getNom(obj,option,curseurGet,False)
    if option in ("salons","voicechan"):
        for guild in listeMixs:
            connexion,curseur=connectSQL(guild["ID"],dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
            try:
                connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
                for i in curseur.execute("SELECT * FROM {0}{1}{2} ORDER BY Rank ASC LIMIT 150".format(moisDB,anneeDB,obj)).fetchall():
                    ligne=getUserTable(i,curseurGet,curseurGuild,guild["ID"])
                    stats.append(ligne)
                    maxi=max(maxi,i["Count"])
            except:
                pass
        stats.sort(key=lambda x:x["Count"],reverse=True)
        if maxi<0:
            maxi=1
        ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"nom":nom,"option":option,"obj":obj}
        return render(request,"companion/Stats/Ranks/iFrameRanks_ranks.html",ctx)
    else:
        for guild in listeMixs:
            try:
                connexion,curseur=connectSQL(guild["ID"],dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
                ligne=curseur.execute("SELECT * FROM {0}{1} WHERE ID={2}".format(moisDB,anneeDB,obj)).fetchone()
                ligne["Nom"]=guild["Nom"]
                ligne["ID"]=guild["ID"]
                ligne["Icon"]=guild["Icon"]
                maxi=max(maxi,ligne["Count"])
                stats.append(ligne)
            except:
                pass
        stats.sort(key=lambda x:x["Count"],reverse=True)
        if maxi<0:
            maxi=1
        ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"nom":nom,"option":option}
        return render(request, "companion/Stats/Periods/periods.html", ctx)
