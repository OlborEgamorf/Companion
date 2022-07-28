from math import inf

from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, dictOptions, getMoisAnnee, getTimes,
                              listeOptions, tableauMois,listeOptionsJeux)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def compareRankJeux(request,option):
    return viewRankCompare(request,"OT",option)

@login_required(login_url="/login")
@CompanionStats
def viewRankCompare(request,guild,option):
    mois1,annee1 = request.GET.get("mois1"),request.GET.get("annee1")
    mois2,annee2 = request.GET.get("mois2"),request.GET.get("annee2")
    mois1,annee1,moisDB1,anneeDB1=getMoisAnnee(mois1,annee1)
    mois2,annee2,moisDB2,anneeDB2=getMoisAnnee(mois2,annee2)
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        pin=getPin(user,curseurGet,"jeux",option,"ranks","")
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
    else:
        pin=getPin(user,curseurGet,guild,option,"ranks","")
        categ="Stats"
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    listeMois,listeAnnee=getTimes(guild,option,categ)

    maxi=-inf
    stats1=[]
    stats2=[]

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB1],anneeDB1)

    for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT 150".format(moisDB1,anneeDB1)).fetchall():
        stats1.append(chooseGetteur(option,categ,i,guild,curseurGet,curseurGuild))
        maxi=max(maxi,i["Count"])

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB2],anneeDB2)

    for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT 150".format(moisDB2,anneeDB2)).fetchall():
        stats2.append(chooseGetteur(option,categ,i,guild,curseurGet,curseurGuild))
        maxi=max(maxi,i["Count"])

    connexion.close()

    for i in range(len(stats2)):
        if i<len(stats1):
            stats1[i]["Nom2"]=stats2[i]["Nom"]
            stats1[i]["Count2"]=stats2[i]["Count"]
            stats1[i]["ID2"]=stats2[i]["ID"]
            if option in ("messages","voice","mots"): 
                stats1[i]["Color2"]=stats2[i]["Color"]
                stats1[i]["Avatar2"]=stats2[i]["Avatar"]
            elif categ=="Jeux":
                stats1[i]["Color2"]=stats2[i]["Color"]
                stats1[i]["Emote2"]=stats2[i]["Emote"]
                stats1[i]["Win2"]=stats2[i]["Win"]
                stats1[i]["Lose2"]=stats2[i]["Lose"]
            try:
                evolLine=list(filter(lambda x:stats2[i]["ID"]==x["ID"], stats1))
                stats1[i]["Evol"]=evolLine[0]["Rank"]-stats2[i]["Rank"]
                stats1[i]["CountVar"]=evolLine[0]["Count"]-stats2[i]["Count"]
            except:
                stats1[i]["Evol"]=0
                stats1[i]["CountVar"]=0
            stats1[i]["Rank"]=i+1
        else:
            try:
                evolLine=list(filter(lambda x:stats2[i]["ID"]==x["ID"], stats1))
                evol=evolLine[0]["Rank"]-stats2[i]["Rank"]
                countVar=evolLine[0]["Count"]-stats2[i]["Count"]
            except:
                evol=0
                countVar=0
            if option in ("messages","voice","mots"):
                stats1.append({"Nom2":stats2[i]["Nom"],"Count2":stats2[i]["Count"],"Avatar2":stats2[i]["Avatar"],"Color2":stats2[i]["Color"],"ID2":stats2[i]["ID"],"Evol":evol,"Rank":i+1,"CountVar":countVar})
            elif categ=="Jeux":
                stats1.append({"Nom2":stats2[i]["Nom"],"Count2":stats2[i]["Count"],"Emote2":stats2[i]["Emote"],"Color2":stats2[i]["Color"],"ID2":stats2[i]["ID"],"Evol":evol,"Rank":i+1,"Win2":stats2[i]["Win"],"Lose2":stats2[i]["Lose"],"CountVar":countVar}) 
            else:
                stats1.append({"Nom2":stats2[i]["Nom"],"Count2":stats2[i]["Count"],"ID2":stats2[i]["ID"],"Evol":evol,"Rank":i+1,"CountVar":countVar}) 
    
    if categ=="Jeux":
        ctx={"rank":stats1,"max":maxi,"pagestats":True,"ot":True,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":"Classements Jeux","guildid":"ot/jeux",
        "mois1":mois1,"annee1":annee1,"mois2":mois2,"annee2":annee2,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "command":"ranks","plus":"compare","options":listeOptionsJeux,"option":option,
        "travel":False,"selector":True,"obj":None,
        "pin":getPin(user,curseurGet,"ot/jeux",option,"ranks","compare")}
    else:
        ctx={"rank":stats1,"max":maxi,"pagestats":True,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "mois1":mois1,"annee1":annee1,"mois2":mois2,"annee2":annee2,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "command":"ranks","plus":"compare","options":listeOptions,"option":option,
        "travel":False,"selector":True,"obj":None,
        "pin":getPin(user,curseurGet,guild,option,"ranks","compare")}

    return render(request, "companion/Stats/Ranks/ranksCompare.html", ctx)
