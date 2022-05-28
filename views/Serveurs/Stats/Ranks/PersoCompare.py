from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from companion.tools.Decorator import CompanionStats

from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, dictOptions, getMoisAnneePerso,
                      getTimes, listeOptions, tableauMois)


@login_required(login_url="/login")
@CompanionStats
def viewPersoCompare(request,guild,option):
    mois1,annee1 = request.GET.get("mois1"),request.GET.get("annee1")
    mois2,annee2 = request.GET.get("mois2"),request.GET.get("annee2")

    mois1,annee1,moisDB1,anneeDB1=getMoisAnneePerso(mois1,annee1)
    mois2,annee2,moisDB2,anneeDB2=getMoisAnneePerso(mois2,annee2)

    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
    color=curseurGet.execute("SELECT * FROM users JOIN users_{0} ON users.ID = users_{0}.ID WHERE users.ID={1}".format(guild,user.id)).fetchone()["Color"]
    color="#"+hex(color)[2:]

    listeMois,listeAnnee=getTimes(guild,option,"Stats")

    maxi=-inf
    stats1=[]
    stats2=[]

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB1],anneeDB1)

    for i in curseur.execute("SELECT * FROM perso{0}{1}{2} ORDER BY Count DESC LIMIT 150".format(moisDB1,anneeDB1,user.id)).fetchall():
        stats1.append(chooseGetteur(option,"Stats",i,guild,curseurGet))
        maxi=max(maxi,i["Count"])

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB2],anneeDB2)

    for i in curseur.execute("SELECT * FROM perso{0}{1}{2} ORDER BY Count DESC LIMIT 150".format(moisDB2,anneeDB2,user.id)).fetchall():
        stats2.append(chooseGetteur(option,"Stats",i,guild,curseurGet))
        maxi=max(maxi,i["Count"])

    connexion.close()

    for i in range(len(stats2)):
        if i<len(stats1):
            stats1[i]["Nom2"]=stats2[i]["Nom"]
            stats1[i]["Count2"]=stats2[i]["Count"]
            stats1[i]["ID2"]=stats2[i]["ID"]
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
                stats1.append({"Nom2":stats2[i]["Nom"],"Count2":stats2[i]["Count"],"ID2":stats2[i]["ID"],"Evol":evol,"Rank":i+1}) 
        stats1[i]["Color"]=color
        stats1[i]["Color2"]=color

    ctx={"rank":stats1,"max":maxi,"pagestats":True,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"color":color,
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "mois1":mois1,"annee1":annee1,"mois2":mois2,"annee2":annee2,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "command":"ranks","plus":"compareperso","options":listeOptions,"option":option,"travel":False,"selector":True,"obj":None,
    "pin":getPin(user,curseurGet,guild,option,"ranks","compareperso")}

    return render(request, "companion/Stats/Ranks/ranksCompare.html", ctx)
