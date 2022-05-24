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
    obj = request.GET.get("obj")
    user=request.user

    statsMois=[]
    statsAnnee=[]

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    
    mix_ids,infosMix,listeMixs=getInfoMix(user,mix,curseurGet)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    dictStats={}
    if option not in ("messages","voice","mots"):
        listeObj=[]
        for guild in mix_ids:
            try:
                connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")
                for i in curseur.execute("SELECT * FROM glob ORDER BY Rank ASC LIMIT 300").fetchall():
                    if i["ID"] not in dictStats:
                        dictStats[i["ID"]]=i["Count"]
                    else:
                        dictStats[i["ID"]]+=i["Count"]
            except:
                pass
        
        listeObj=list(map(lambda x:{"ID":x,"Count":dictStats[x]},dictStats))
        listeObj.sort(key=lambda x:x["Count"],reverse=True)
        if len(listeObj)>150:
            listeObj=listeObj[:150]

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

        obj=int(obj)
    else:
        obj,listeObj=None,None

    for guild in mix_ids:
        try:
            for i in getTablePerso(guild,dictOptions[option],user.id,obj,"M","countDesc"):
                it=0
                while it<len(statsMois) and it!=-1:
                    if statsMois[it]["Mois"]==i["Mois"] and statsMois[it]["Annee"]==i["Annee"]:
                        statsMois[it]["Count"]+=i["Count"]
                        it=-1
                    else:
                        it+=1
                if it!=-1:
                    statsMois.append(i)
            for i in getTablePerso(guild,dictOptions[option],user.id,obj,"A","countDesc"):
                it=0
                while it<len(statsAnnee) and it!=-1:
                    if statsAnnee[it]["Annee"]==i["Annee"]:
                        statsAnnee[it]["Count"]+=i["Count"]
                        it=-1
                    else:
                        it+=1
                if it!=-1:
                    statsAnnee.append(i)
        except:
            pass
    
    assert statsMois!=[] and statsAnnee!=[]
    statsMois.sort(key=lambda x:x["Count"],reverse=True)
    rankingClassic(statsMois)
    statsAnnee.sort(key=lambda x:x["Count"],reverse=True)
    rankingClassic(statsAnnee)

    maxiM=max(list(map(lambda x:x["Count"],statsMois)))
    if maxiM<=0:
        maxiM=1
    maxiA=max(list(map(lambda x:x["Count"],statsAnnee)))
    if maxiA<=0:
        maxiA=1

    listeMois,listeAnnee=getTimesMix(mix_ids,option)

    ctx={"rankMois":statsMois,"maxM":maxiM,"rankAnnee":statsAnnee,"maxA":maxiA,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":infosMix["Nom"],"guildid":"mixes/{0}".format(infosMix["Nombre"]),
    "commands":["ranks","periods"],"dictCommands":dictRefCommands,"command":"periods",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":["serv","perso"] if option in ("salons","voicechan") else ["serv","perso","compare","compareperso"],"dictPlus":dictRefPlus,"plus":"perso",
    "travel":False,"selector":True,"obj":obj,"listeObjs":listeObj,"mix":True,"listeMix":listeMixs,"nbmix":infosMix["Nombre"],
    "pin":getPin(user,curseurGet,"mixes/{0}".format(infosMix["Nombre"]),option,"ranks","")}

    return render(request, "companion/periods.html", ctx)

@login_required(login_url="/login")
def iFrameMixPeriods(request,mix,option):
    all=request.GET.get("data")
    mois,annee,obj=all.split("?")
    if len(annee)==4:
        mois=tableauMois[mois.lower()]
        annee=annee[2:4]
    if annee not in ("GL","Global"):
        annee="20"+annee
    mois,annee,moisDB,anneeDB=getMoisAnnee(tableauMois[mois],annee)
    user=request.user
    if obj=="None" or obj==None:
        obj=""
    
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    mix_ids,infosMix,listeMixs=getInfoMix(user,mix,curseurGet)

    stats=[]
    maxi=-inf
    if obj=="":
        nom=getNom(user.id,option,curseurGet,False)
    else:
        nom=getNom(obj,option,curseurGet,False)
    if option in ("salons","voicechan"):
        for guild in listeMixs:
            try:
                connexion,curseur=connectSQL(guild["ID"],dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
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
            try:
                connexion,curseur=connectSQL(guild["ID"],dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
                ligne=curseur.execute("SELECT * FROM {0}{1}{2} WHERE ID={3}".format(moisDB,anneeDB,obj,user.id)).fetchone()
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
