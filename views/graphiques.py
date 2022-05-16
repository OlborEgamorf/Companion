from math import inf

from companion.Getteurs import getUserInfo, getUserTable
from companion.graphs.Evol import graphLineEvol
from companion.graphs.HeatGlobal import heatGlobal
from companion.graphs.HeatMois import heatMois
from companion.graphs.Line import graphLine
from companion.graphs.LinePeriods import graphLinePeriods
from companion.graphs.Point import graphPoint
from companion.graphs.Rank import graphAnim, graphRank
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..outils import (collapseEvol, connectSQL, dictOptions, dictRefCommands, dictRefOptions,
                      dictRefPlus, getCommands, getMoisAnnee,
                      getPlus, getTablePerso, getTimes, listeOptions, tableauMois)


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
        div4,div5,div6=None,None,None
        div7=None
    elif moisDB=="to":
        div4,div5=graphPoint(guild,option,curseur,curseurGet,moisDB,anneeDB)
        div6=None
    else:
        div3=heatMois(guild,option,tableauMois[moisDB],anneeDB)
        div4,div5=graphPoint(guild,option,curseur,curseurGet,moisDB,anneeDB)
        div6=graphLine(guild,option,user,curseur,curseurGet,mois,annee,moisDB,anneeDB)

        div7=graphAnim(guild,option,curseur,curseurGet,moisDB,anneeDB)

    connexion.close()
    ctx={"fig":div1,"fig2":div2,"fig3":div3,"fig4":div4,"fig5":div5,"fig6":div6,"fig7":div7,"avatar":user_full["Avatar"],"id":user.id,"guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"ranks",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("ranks",option),"dictPlus":dictRefPlus,"plus":"graphs",
    "travel":True,"selector":True,"obj":None}
    return render(request, "companion/Old/graph.html", ctx)

@login_required(login_url="/login")
def graphPeriods(request,guild,option):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
    infos=getUserInfo(user.id,curseurGet,guild)
    
    div1,div2,div3,div4=graphLinePeriods(guild,option,user,"#"+hex(infos["Color"])[2:],True,"M")
    div5,div6,div7=graphLinePeriods(guild,option,user,"turquoise",False,"M")

    #connexion.close()
    ctx={"fig":div1,"fig2":div2,"fig3":div3,"fig4":div4,"fig5":div5,"fig6":div6,"fig7":div7,"avatar":user_full["Avatar"],"id":user.id,"guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"periods",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("periods",option),"dictPlus":dictRefPlus,"plus":"graphs",
    "travel":False,"selector":True,"obj":None}
    return render(request, "companion/graphPeriods.html", ctx)


@login_required(login_url="/login")
def graphEvol(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    listeMois,listeAnnee=getTimes(guild,option,"Stats")

    div1,div2,div3,div4=graphLineEvol(guild,option,curseur,curseurGet,user,moisDB,anneeDB)

    connexion.close()
    ctx={"fig":div1,"fig2":div2,"fig3":div3,"fig4":div4,"fig5":None,"fig6":None,"fig7":None,"avatar":user_full["Avatar"],"id":user.id,"guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"evol",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("evol",option),"dictPlus":dictRefPlus,"plus":"graphs",
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


@login_required(login_url="/login")
def iFrameGraphPeriods(request,guild,option):
    user=request.user

    tableUser=getTablePerso(guild,option,user.id,False,"M","periodAsc")
    tableServ=getTablePerso(guild,option,guild,False,"M","periodAsc")
    maxiUser=max(tableUser,key=lambda x:x["Count"])
    maxiServ=max(tableServ,key=lambda x:x["Count"])

    ctx={"user":tableUser,"serv":tableServ,"id":user.id,"maxUser":maxiUser,"maxServ":maxiServ,"option":option,"plus":"graph"}
    return render(request, "companion/iFramePeriodsGraph.html", ctx)

@login_required(login_url="/login")
def iFrameGraphEvol(request,guild,option):
    all=request.GET.get("data")
    mois,annee,obj=all.split("?")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user
    if obj=="None":
        obj=user.id
    
    categ="Stats"
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)

    table=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,obj)).fetchall()
    table=collapseEvol(table)  
    table.reverse() 
    table=list(filter(lambda x:not x["Collapse"],table))
    maxi=max(list(map(lambda x:x["Count"],table)))

    ctx={"rank":table,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"option":option,"plus":"graph"}
    return render(request, "companion/Ranks/iFrameRanks_evol.html", ctx)
