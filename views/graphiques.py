from math import inf
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from companion.Getteurs import getUserTable

from companion.graphs.HeatGlobal import heatGlobal
from companion.graphs.HeatMois import heatMois
from companion.graphs.Point import graphPoint
from companion.graphs.Rank import graphRank

from ..outils import (connectSQL, dictRefCommands, dictRefOptions,
                      dictRefPlus, getCommands, getGuilds,
                      getMoisAnnee, getPlus, getTimes, listeOptions,
                      tableauMois,dictOptions)


@login_required(login_url="/login")
def graphRanks(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    listeMois,listeAnnee=getTimes(guild,option,"Stats")

    div1,div2=graphRank(guild,option,user,curseur,curseurGet,moisDB,anneeDB,True)

    if moisDB=="glob":
        div3=heatGlobal(guild,option,curseur)
        div4,div5=None,None
    elif moisDB=="to":
        div4,div5=graphPoint(guild,option,curseur,curseurGet,moisDB,anneeDB)
    else:
        div3=heatMois(guild,option,tableauMois[moisDB],anneeDB)
        div4,div5=graphPoint(guild,option,curseur,curseurGet,moisDB,anneeDB)

    connexion.close()
    ctx={"fig":div1,"fig2":div2,"fig3":div3,"fig4":div4,"fig5":div5,"avatar":user_full["Avatar"],"id":user.id,"guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,"guilds":getGuilds(user),
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"ranks",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("ranks",option),"dictPlus":dictRefPlus,"plus":"graphs",
    "travel":True,"selector":True,"obj":None}
    return render(request, "companion/Old/graph.html", ctx)


@login_required(login_url="/login")
def iFrameGraphRanks(request,guild,option):
    all=request.GET.get("data")
    mois,annee,obj=all.split("?")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user
    if obj=="None":
        obj=""
    
    categ="Stats"
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)

    maxi=-inf
    stats=[]
    for i in curseur.execute("SELECT * FROM {0}{1}{2} ORDER BY Rank ASC LIMIT 150".format(moisDB,anneeDB,obj)).fetchall():
        stats.append(getUserTable(i,curseurGet,guild))
        maxi=max(maxi,i["Count"])

    ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"option":option,"plus":"graph"}
    return render(request, "companion/Ranks/iFrameRanks_ranks.html", ctx)
