from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, dictOptions, dictRefCommands, dictRefOptions,
                      dictRefPlus, getMoisAnnee, getTimesMix, listeOptions, rankingClassic, tableauMois)


@login_required(login_url="/login")
def viewMixRankCompare(request,mix,option):
    mois1,annee1 = request.GET.get("mois1"),request.GET.get("annee1")
    mois2,annee2 = request.GET.get("mois2"),request.GET.get("annee2")
    mois1,annee1,moisDB1,anneeDB1=getMoisAnnee(mois1,annee1)
    mois2,annee2,moisDB2,anneeDB2=getMoisAnnee(mois2,annee2)
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    mix_ids,infosMix,listeMixs=getInfoMix(user,mix,curseurGet)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    listeMois,listeAnnee=getTimesMix(mix_ids,option)

    maxi=-inf
    stats1=[]
    stats2=[]

    dictStats={}
    # Stats 1
    for guild in mix_ids:
        try:
            connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB1],anneeDB1)
            for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT 1000".format(moisDB1,anneeDB1)).fetchall():
                if i["ID"] not in dictStats:
                    dictStats[i["ID"]]=i["Count"]
                else:
                    dictStats[i["ID"]]+=i["Count"]
        except:
            pass

    stats1=list(map(lambda x:{"ID":x,"Count":dictStats[x]},dictStats))
    assert stats1!=[]
    stats1.sort(key=lambda x:x["Count"],reverse=True)
    if len(stats1)>150:
        stats1=stats1[:150]
    rankingClassic(stats1)

    for i in stats1:
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

    dictStats={}
    # Stats 2
    for guild in mix_ids:
        try:
            connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB2],anneeDB2)
            for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT 1000".format(moisDB2,anneeDB2)).fetchall():
                if i["ID"] not in dictStats:
                    dictStats[i["ID"]]=i["Count"]
                else:
                    dictStats[i["ID"]]+=i["Count"]
        except:
            pass
    
    stats2=list(map(lambda x:{"ID":x,"Count":dictStats[x]},dictStats))
    assert stats2!=[]
    stats2.sort(key=lambda x:x["Count"],reverse=True)
    if len(stats2)>150:
        stats2=stats2[:150]
    rankingClassic(stats2)

    for i in stats2:
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


    for i in range(len(stats2)):
        if i<len(stats1):
            stats1[i]["Nom2"]=stats2[i]["Nom"]
            stats1[i]["ID2"]=stats2[i]["ID"]
            stats1[i]["Count2"]=stats2[i]["Count"]
            if option in ("messages","voice","mots"): 
                stats1[i]["Avatar2"]=stats2[i]["Avatar"]
            try:
                stats1[i]["Evol"]=list(filter(lambda x:stats2[i]["ID"]==x["ID"], stats1))[0]["Rank"]-stats2[i]["Rank"]
            except:
                stats1[i]["Evol"]=0
            stats1[i]["Rank"]=i+1
        else:
            try:
                evol=list(filter(lambda x:stats2[i]["ID"]==x["ID"], stats1))[0]["Rank"]-stats2[i]["Rank"]
            except:
                evol=0
                if option in ("messages","voice","mots"):
                    stats1.append({"Nom2":stats2[i]["Nom"],"Count2":stats2[i]["Count"],"Avatar2":stats2[i]["Avatar"],"ID2":stats2[i]["ID"],"Evol":evol,"Rank":i+1})
                else:
                    stats1.append({"Nom2":stats2[i]["Nom"],"Count2":stats2[i]["Count"],"ID2":stats2[i]["ID"],"Evol":evol,"Rank":i+1}) 

    ctx={"rank":stats1,"max":maxi,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "mois1":mois1,"annee1":annee1,"mois2":mois2,"annee2":annee2,"listeMois":listeMois,"listeAnnee":listeAnnee,"guildname":infosMix["Nom"],"guildid":"mixes/{0}".format(infosMix["Nombre"]),
    "commands":["ranks","periods"],"dictCommands":dictRefCommands,"command":"ranks",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":["","compare"] if option in ("messages","voice","mots") else ["serv","perso","compare"],"dictPlus":dictRefPlus,"plus":"compare",
    "travel":False,"selector":True,"obj":None,"mix":True,"listeMix":listeMixs,"nbmix":infosMix["Nombre"],
    "pin":getPin(user,curseurGet,"mixes/{0}".format(infosMix["Nombre"]),option,"ranks","compare")}

    return render(request, "companion/Compare/ranksCompare.html", ctx)
