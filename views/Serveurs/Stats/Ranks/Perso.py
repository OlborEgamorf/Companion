from math import inf

from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, dictOptions, getMoisAnnee,
                              getMoisAnneePerso, getTablePerso, getTimes,
                              listeOptions)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
@CompanionStats
def viewPerso(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnneePerso(mois,annee)
    moisGen,anneeGen,moisDBGen,anneeDBGen=getMoisAnnee(mois,annee)
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    listeMois,listeAnnee=getTimes(guild,option,"Stats")

    stats=[]
    maxi=-inf

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    
    ctx={"rank":stats,"max":None,"pagestats":True,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"color":getColor(user.id,guild,curseurGet),
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "command":"ranks","options":listeOptions,"option":option,"plus":"perso","travel":True,"selector":True,
    "pin":getPin(user,curseurGet,guild,option,"ranks","perso")}

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",moisDB,anneeDB)

    for i in curseur.execute("SELECT * FROM perso{0}{1}{2} ORDER BY Count DESC LIMIT 200".format(moisDB,anneeDB,user.id)).fetchall():

        ligne=chooseGetteur(option,"Stats",i,guild,curseurGet,curseurGuild)

        if option!="divers":
            more=curseur.execute("SELECT * FROM {0}{1} WHERE ID={2}".format(moisDBGen,anneeDBGen,i["ID"])).fetchone()
            if more!=None:
                ligne["CountGen"]=more["Count"]
                ligne["RankGen"]=more["Rank"]
        stats.append(ligne)
        maxi=max(maxi,i["Count"])

    ctx["max"]=maxi
    if option=="divers":
        return render(request, "companion/Stats/Ranks/ranksDivers.html", ctx)
    else:
        return render(request, "companion/Stats/Perso/perso.html", ctx)


@login_required(login_url="/login")
def iFramePerso(request,guild,option):
    obj=request.GET.get("data")
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    
    ctx={"rankMois":None,"rankAnnee":None,"maxM":None,"maxA":None,"color":None,"option":option,"color":getColor(user.id,guild,curseurGet)}

    ctx["rankMois"]=getTablePerso(guild,dictOptions[option],user.id,obj,"M","countDesc")
    ctx["rankAnnee"]=getTablePerso(guild,dictOptions[option],user.id,obj,"A","countDesc")

    ctx["maxM"]=max(list(map(lambda x:x["Count"],ctx["rankMois"])))
    ctx["maxA"]=max(list(map(lambda x:x["Count"],ctx["rankAnnee"])))
    
    return render(request, "companion/Stats/Perso/iFramePerso.html", ctx)
