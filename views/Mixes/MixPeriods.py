from math import inf

from companion.Getteurs import *
from companion.outils import (connectSQL, dictOptions, dictRefCommands,
                              dictRefOptions, dictRefPlus, getCommands,
                              getMoisAnnee, getTablePerso, getTimesMix, listeOptions,
                              rankingClassic, tableauMois)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
def mixPeriods(request,mix,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    maxi=-inf
    stats=[]

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    
    mix_ids,infosMix,listeMixs=getInfoMix(user,mix,curseurGet)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    if option not in ("messages","voice","mots"):
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
            obj=listeObj[0]["ID"]

        if len(listeObj)>150:
            listeObj=listeObj[:150]
    
        obj=int(obj)
    else:
        obj,listeObj=False,None

    for guild in mix_ids:
        try:
            for i in getTablePerso(guild,dictOptions[option],user.id,obj,"M","countDesc"):
                it=0
                while it<len(stats) and it!=-1:
                    if stats[it]["Mois"]==i["Mois"] and stats[it]["Annee"]==i["Annee"]:
                        stats[it]["Count"]+=i["Count"]
                        it=-1
                    else:
                        it+=1
                if it!=-1:
                    stats.append(i)
        except:
            pass
    
    assert stats!=[]
    stats.sort(key=lambda x:x["Count"],reverse=True)
    if len(stats)>150:
        stats=stats[:150]
    rankingClassic(stats)

    if option in ("messages","voice","mots"):
        infos=getUserInfoMix(i["ID"],mix_ids,curseurGet)
        i["Nom"]=infos["Nom"]
        i["Avatar"]=infos["Avatar"]
    elif option in ("emotes","reactions"):
        infos=getEmoteTable(i,curseurGet)
        i["Nom"]=infos["Nom"]
    else:
        i["Nom"]=getNom(i["ID"],option,curseurGet,False)

    connexion.close()

    if maxi<=0:
        maxi=1

    listeMois,listeAnnee=getTimesMix(mix_ids,option)

    ctx={"rank":stats,"max":maxi,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,"guildname":infosMix["Nom"],"guildid":"mixes/{0}".format(infosMix["Nombre"]),
    "commands":["ranks","periods"],"dictCommands":dictRefCommands,"command":"ranks",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":[] if option in ("messages","voice","mots") else ["serv","perso"],"dictPlus":dictRefPlus,"plus":"" if option in ("messages","voice","mots") else "serv",
    "travel":True,"selector":True,"obj":None,"mix":True,"listeMix":listeMixs,"nbmix":infosMix["Nombre"],
    "pin":getPin(user,curseurGet,"mixes/{0}".format(infosMix["Nombre"]),option,"ranks","")}

    return render(request, "companion/Ranks/ranks.html", ctx)



@login_required(login_url="/login")
def iFrameMixRank(request,mix,option):
    all=request.GET.get("data")
    mois,annee,obj=all.split("?")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user
    if obj==None:
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
                for i in curseur.execute("SELECT * FROM {0}{1}{2} ORDER BY Rank ASC LIMIT 150".format(moisDB,anneeDB,obj)).fetchall():
                    ligne=getUserTable(i,curseurGet,guild["ID"])
                    stats.append(ligne)
                    maxi=max(maxi,i["Count"])
            except:
                pass
        stats.sort(key=lambda x:x["Count"],reverse=True)
        if maxi<0:
            maxi=1
        ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"nom":nom,"option":option,"obj":obj}
        return render(request,"companion/Ranks/iFrameRanks_ranks.html",ctx)
    else:
        for guild in listeMixs:
            connexion,curseur=connectSQL(guild["ID"],dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
            try:
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
        return render(request,"companion/EmotesWW/iFrameEmotesWW.html",ctx)