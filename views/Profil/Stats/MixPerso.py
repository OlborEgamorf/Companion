from math import inf

from companion.Getteurs import *
from companion.outils import (connectSQL, dictOptions, dictRefCommands,
                              dictRefOptions, dictRefPlus, getCommands, getMoisAnnee,
                              getMoisAnneePerso, getPlus, getTablePerso, getTimesMix,
                              listeOptions, rankingClassic,tableauMois)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
def mixPerso(request,mix,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnneePerso(mois,annee)
    user=request.user

    maxi=-inf
    dictStats={}

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    
    mix_ids,infosMix,listeMixs=getInfoMix(user,mix,curseurGet)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    for guild in mix_ids:
        try:
            connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",moisDB,anneeDB)
            for i in curseur.execute("SELECT * FROM perso{0}{1}{2} ORDER BY Count DESC LIMIT 200".format(moisDB,anneeDB,user.id)).fetchall():
                if i["ID"] not in dictStats:
                    dictStats[i["ID"]]=i["Count"]
                else:
                    dictStats[i["ID"]]+=i["Count"]
        except:
            continue
    
    stats=list(map(lambda x:{"ID":x,"Count":dictStats[x]},dictStats))
    assert stats!=None
    stats.sort(key=lambda x:x["Count"],reverse=True)
    if len(stats)>150:
        stats=stats[:150]
    rankingClassic(stats)

    for i in stats:
        if option in ("emotes","reactions"):
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
    "commands":["ranks","periods"],"dictCommands":dictRefCommands,"command":"ranks",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":["serv","perso"],"dictPlus":dictRefPlus,"plus":"perso",
    "travel":True,"selector":True,"obj":None,"mix":True,"listeMix":listeMixs,"nbmix":infosMix["Nombre"],
    "pin":getPin(user,curseurGet,"mixes/{0}".format(infosMix["Nombre"]),option,"ranks","")}

    return render(request, "companion/Perso/perso.html", ctx)

@login_required(login_url="/login")
def iFrameMixPerso(request,mix,option):
    all=request.GET.get("data")
    obj,mois,annee=all.split("?")
    user=request.user
    if obj==None:
        obj=user.id
    
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    mix_ids,infosMix,listeMixs=getInfoMix(user,mix,curseurGet)

    stats=[]
    maxi=-inf
    nom=getNom(obj,option,curseurGet,False)
    if option in ("salons","voicechan"):
        mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
        for guild in listeMixs:
            table=getTablePerso(guild["ID"],dictOptions[option],user.id,obj,"M","countDesc")

        stats.sort(key=lambda x:x["Count"],reverse=True)
        if maxi<0:
            maxi=1
        ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"nom":nom,"option":option,"obj":obj}
        return render(request,"companion/Ranks/iFrameRanks_ranks.html",ctx)
    else:
        mois,annee,moisDB,anneeDB=getMoisAnneePerso(mois,annee)
        for guild in listeMixs:
            connexion,curseur=connectSQL(guild["ID"],dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
            try:
                ligne=curseur.execute("SELECT * FROM perso{0}{1}{2} WHERE ID={3}".format(moisDB,anneeDB,user.id,obj)).fetchone()
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