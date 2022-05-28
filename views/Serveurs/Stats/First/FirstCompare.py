from math import inf
from random import choice

from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import *
from companion.tools.outils import connectSQL, dictOptions, getTimes, listeOptions
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
@CompanionStats
def viewFirstCompare(request,guild,option):
    annee1 = request.GET.get("annee1")
    annee2 = request.GET.get("annee2")
    listeAnnee=getTimes(guild,option,"Stats")[1]
    listeAnnee.remove("Global")
    if annee1==None:
        annee1=choice(listeAnnee)
    anneeDB1=annee1[2:4]
    if annee2==None:
        annee2=choice(listeAnnee)
    anneeDB2=annee2[2:4]
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    maxi=-inf
    maxiA=-inf
    stats1=[]
    stats2=[]

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","TO","GL")

    for i in curseur.execute("SELECT * FROM firstM WHERE Annee={0} ORDER BY Mois ASC".format(anneeDB1)).fetchall()+curseur.execute("SELECT * FROM firstA WHERE Annee={0}".format(anneeDB1)).fetchall():

        i["Rank"]=0
        ligne=chooseGetteur(option,"Stats",i,guild,curseurGet)

        ligne["Mois"]=i["Mois"]
        ligne["Annee"]=i["Annee"]
        stats1.append(ligne)

        if i["Mois"]=="TO":
            maxiA=max(maxiA,i["Count"])
        else:
            maxi=max(maxi,i["Count"])

    for i in curseur.execute("SELECT * FROM firstM WHERE Annee={0} ORDER BY Mois ASC".format(anneeDB2)).fetchall()+curseur.execute("SELECT * FROM firstA WHERE Annee={0}".format(anneeDB2)).fetchall():
        
        i["Rank"]=0

        ligne=chooseGetteur(option,"Stats",i,guild,curseurGet)

        ligne["Mois"]=i["Mois"]
        ligne["Annee"]=i["Annee"]
        stats2.append(ligne)

        if i["Mois"]=="TO":
            maxiA=max(maxiA,i["Count"])
        else:
            maxi=max(maxi,i["Count"])

    connexion.close()


    for i in range(len(stats1)):
        period=list(filter(lambda x:x["Mois"]==stats1[i]["Mois"],stats2))
        print(period)
        if period!=[]:
            stats1[i]["Nom2"]=period[0]["Nom"]
            stats1[i]["ID2"]=period[0]["ID"]
            stats1[i]["Count2"]=period[0]["Count"]
            if option in ("messages","voice","mots"):
                stats1[i]["Avatar2"]=period[0]["Avatar"]
                stats1[i]["Color2"]=period[0]["Color"]

    ctx={"rank":stats1,"max":maxi,"maxA":maxiA,"pagestats":True,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "mois1":"Total","annee1":annee1,"mois2":"Total","annee2":annee2,"listeMois":["Total"],"listeAnnee":listeAnnee,
    "command":"first","options":listeOptions,"option":option,"plus":"compare",
    "travel":False,"selector":True,"obj":None,
    "pin":getPin(user,curseurGet,guild,option,"evol","compare")}

    return render(request, "companion/Stats/First/firstCompare.html", ctx)
