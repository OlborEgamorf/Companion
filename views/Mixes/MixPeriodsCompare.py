from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companion.Getteurs import *
from companion.outils import (connectSQL, dictOptions, dictRefCommands, dictRefOptions,
                      dictRefPlus, getMoisAnnee, getTimesMix, listeOptions, rankingClassic, tableauMois)


@login_required(login_url="/login")
def viewMixPeriodsCompare(request,mix,option):
    assert option not in ("salons","voicechan")
    mois1,annee1 = request.GET.get("mois1"),request.GET.get("annee1")
    mois2,annee2 = request.GET.get("mois2"),request.GET.get("annee2")
    obj = request.GET.get("obj")
    mois1,annee1,moisDB1,anneeDB1=getMoisAnnee(mois1,annee1)
    mois2,annee2,moisDB2,anneeDB2=getMoisAnnee(mois2,annee2)
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    mix_ids,infosMix,listeMixs=getInfoMix(user,mix,curseurGet)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    listeMois,listeAnnee=getTimesMix(mix_ids,option)

    if option not in ("messages","voice","mots"):
        connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")
        listeObj=curseur.execute("SELECT * FROM glob ORDER BY Count DESC LIMIT 150").fetchall()
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
    else:
        listeObj=None
        obj=""

    maxi=-inf
    stats1=[]
    stats2=[]

    # Stats 1
    for guild in listeMixs:
        try:
            connexion,curseur=connectSQL(guild["ID"],dictOptions[option],"Stats",tableauMois[moisDB1],anneeDB1)
            ligne=curseur.execute("SELECT * FROM {0}{1}{2} WHERE ID={3}".format(moisDB1,anneeDB1,obj,user.id)).fetchone()
            ligne["Nom"]=guild["Nom"]
            ligne["ID"]=guild["ID"]
            ligne["Icon"]=guild["Icon"]
            maxi=max(maxi,ligne["Count"])
            stats1.append(ligne)
        except:
            pass
    stats1.sort(key=lambda x:x["Count"],reverse=True)
    rankingClassic(stats1)


    # Stats 2
    for guild in listeMixs:
        try:
            connexion,curseur=connectSQL(guild["ID"],dictOptions[option],"Stats",tableauMois[moisDB2],anneeDB2)
            ligne=curseur.execute("SELECT * FROM {0}{1}{2} WHERE ID={3}".format(moisDB2,anneeDB2,obj,user.id)).fetchone()
            ligne["Nom"]=guild["Nom"]
            ligne["ID"]=guild["ID"]
            ligne["Icon"]=guild["Icon"]
            maxi=max(maxi,ligne["Count"])
            stats2.append(ligne)
        except:
            pass
    stats2.sort(key=lambda x:x["Count"],reverse=True)
    rankingClassic(stats2)

    connexion.close()

    for i in range(len(stats2)):
        if i<len(stats1):
            stats1[i]["Nom2"]=stats2[i]["Nom"]
            stats1[i]["ID2"]=stats2[i]["ID"]
            stats1[i]["Count2"]=stats2[i]["Count"]
            stats1[i]["Icon2"]=stats2[i]["Icon"]
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
                    stats1.append({"Nom2":stats2[i]["Nom"],"Count2":stats2[i]["Count"],"ID2":stats2[i]["ID"],"Evol":evol,"Rank":i+1,"Icon2":stats2[i]["Icon"]})
                else:
                    stats1.append({"Nom2":stats2[i]["Nom"],"Count2":stats2[i]["Count"],"ID2":stats2[i]["ID"],"Evol":evol,"Rank":i+1,"Icon2":stats2[i]["Icon"]}) 

    if option in ("messages","voice","mots"):
        obj=None

    ctx={"rank":stats1,"max":maxi,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "mois1":mois1,"annee1":annee1,"mois2":mois2,"annee2":annee2,"listeMois":listeMois,"listeAnnee":listeAnnee,"guildname":infosMix["Nom"],"guildid":"mixes/{0}".format(infosMix["Nombre"]),
    "commands":["ranks","periods"],"dictCommands":dictRefCommands,"command":"periods",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":["serv","perso","compare","compareperso"],"dictPlus":dictRefPlus,"plus":"compareperso",
    "travel":False,"selector":True,"obj":None,"mix":True,"listeMix":listeMixs,"nbmix":infosMix["Nombre"],
    "pin":getPin(user,curseurGet,"mixes/{0}".format(infosMix["Nombre"]),option,"ranks","compareperso")}

    return render(request, "companion/Compare/ranksCompare.html", ctx)
