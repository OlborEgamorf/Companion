from math import inf

from companion.Getteurs import (getChannels, getEmoteTable, getFreq,
                                getUserInfo, getUserJeux, getUserTable)
from companion.graphs.Evol import graphLineEvol
from companion.graphs.HeatGlobal import heatGlobal
from companion.graphs.HeatMois import heatMois
from companion.graphs.Line import graphLine
from companion.graphs.LineFirst import graphLineFirst
from companion.graphs.LineJours import graphLineJours
from companion.graphs.LinePeriods import graphLinePeriods
from companion.graphs.Point import graphPoint
from companion.graphs.Rank import graphAnim, graphRank
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..outils import (collapseEvol, connectSQL, dictOptions, dictRefCommands,
                      dictRefOptions, dictRefPlus, getCommands, getMoisAnnee,
                      getPlus, getTablePerso, getTimes, listeOptions,
                      tableauMois)


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
        if option in ("messages","voice","mots"):
            div3=heatGlobal(guild,option,curseur)
        else:
            div3=None
        div4,div5,div6=None,None,None
        div7=None
    elif moisDB=="to":
        div4,div5=graphPoint(guild,option,curseur,curseurGet,moisDB,anneeDB)
        div3,div6,div7=None
    else:
        if option in ("messages","voice","mots"):
            div3=heatMois(guild,option,tableauMois[moisDB],anneeDB)
        else:
            div3=None
        div4,div5=graphPoint(guild,option,curseur,curseurGet,moisDB,anneeDB)
        div6=graphLine(guild,option,user,curseur,curseurGet,mois,annee,moisDB,anneeDB)

        div7=graphAnim(guild,option,curseur,curseurGet,moisDB,anneeDB)

    connexion.close()
    ctx={"fig":div1,"fig2":div2,"fig3":div3,"fig4":div4,"fig5":div5,"fig6":div6,"fig7":div7,"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"ranks",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("ranks",option),"dictPlus":dictRefPlus,"plus":"graphs",
    "travel":True,"selector":True,"obj":None}
    return render(request, "companion/Old/graph.html", ctx)

@login_required(login_url="/login")
def graphPeriods(request,guild,option):
    obj = request.GET.get("obj")
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
    infos=getUserInfo(user.id,curseurGet,guild)

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")
    listeObj=curseur.execute("SELECT * FROM glob ORDER BY Count DESC").fetchall()
    if option in ("emotes","reactions"):
        listeObj=list(map(lambda x:getEmoteTable(x,curseurGet),listeObj))
    elif option in ("salons","voicechan"):
        listeObj=list(map(lambda x:getChannels(x,curseurGet),listeObj))
    elif option=="freq":
        listeObj=list(map(lambda x:getFreq(x),listeObj))
    else:
        listeObj=None

    if option not in ("messages","voice","mots"):
        if obj==None:
            obj=listeObj[0]["ID"]

        if len(listeObj)>150:
            listeObj=listeObj[:150]
    
    if option in ("messages","voice","mots"):
        div1,div2,div3,div4=graphLinePeriods(guild,option,user.id,False,"#"+hex(infos["Color"])[2:],True,"M")
        div5,div6,div7=graphLinePeriods(guild,option,user.id,False,"turquoise",False,"M")
        div8=None
    else:
        div1,div2,div3,div4=graphLinePeriods(guild,option,user.id,obj,"#"+hex(infos["Color"])[2:],True,"M")
        div5,div6,div7,div8=graphLinePeriods(guild,option,user.id,obj,"turquoise",False,"M")

    #connexion.close()
    ctx={"fig":div1,"fig2":div2,"fig3":div3,"fig4":div4,"fig5":div5,"fig6":div6,"fig7":div7,"fig8":div8,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"periods",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("periods",option),"dictPlus":dictRefPlus,"plus":"graphs",
    "travel":False,"selector":True,"obj":obj,"listeObjs":listeObj}
    return render(request, "companion/graphPeriods.html", ctx)


@login_required(login_url="/login")
def graphEvol(request,guild,option):
    mois,annee,obj = request.GET.get("mois"),request.GET.get("annee"),request.GET.get("obj")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    listeMois,listeAnnee=getTimes(guild,option,"Stats")

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")
    listeObj=curseur.execute("SELECT * FROM glob ORDER BY Count DESC").fetchall()
    if option in ("emotes","reactions"):
        listeObj=list(map(lambda x:getEmoteTable(x,curseurGet),listeObj))
    elif option in ("salons","voicechan"):
        listeObj=list(map(lambda x:getChannels(x,curseurGet),listeObj))
    elif option=="freq":
        listeObj=list(map(lambda x:getFreq(x),listeObj))
    else:
        listeObj=None

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
    if option not in ("messages","voice","mots"):
        if obj==None:
            obj=listeObj[0]["ID"]

        if len(listeObj)>150:
            listeObj=listeObj[:150]

        div1,div2,div3,div4=graphLineEvol(guild,option,curseur,curseurGet,obj,moisDB,anneeDB)
    else:
        div1,div2,div3,div4=graphLineEvol(guild,option,curseur,curseurGet,user,moisDB,anneeDB)

    connexion.close()
    ctx={"fig":div1,"fig2":div2,"fig3":div3,"fig4":div4,"fig5":None,"fig6":None,"fig7":None,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"evol",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("evol",option),"dictPlus":dictRefPlus,"plus":"graphs",
    "travel":True,"selector":True,"obj":obj,"listeObjs":listeObj}
    return render(request, "companion/Old/graph.html", ctx)


@login_required(login_url="/login")
def graphFirst(request,guild,option):
    user=request.user

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    infos=getUserInfo(user.id,curseurGet,guild)
    hexa=hex(infos["Color"])[2:]
    if len(hexa)==6:
        hexa="#"+hexa
    else:
        hexa="#"+"0"*(6-len(hexa))+hexa
    
    div1,div2=graphLineFirst(guild,option,user,hexa,curseur,curseurGet)

    #connexion.close()
    ctx={"fig":div1,"fig2":div2,"fig3":None,"fig4":None,"fig5":None,"fig6":None,"fig7":None,"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"first",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("first",option),"dictPlus":dictRefPlus,"plus":"graphs",
    "travel":False,"selector":True,"obj":None}
    return render(request, "companion/Old/graph.html", ctx)


@login_required(login_url="/login")
def graphJours(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    listeMois,listeAnnee=getTimes(guild,option,"Stats")

    div1=graphLineJours(curseur,moisDB,anneeDB)

    connexion.close()
    ctx={"fig":div1,"fig2":None,"fig3":None,"fig4":None,"fig5":None,"fig6":None,"fig7":None,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"jours",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("jours",option),"dictPlus":dictRefPlus,"plus":"graphs",
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
        if option in ("messages","voice","mots"):
            stats.append(getUserTable(i,curseurGet,guild))

        elif option in ("emotes","reactions"):
            stats.append(getEmoteTable(i,curseurGet))

        elif option in ("salons","voicechan"):
            stats.append(getChannels(i,curseurGet))

        elif option=="freq":
            stats.append(getFreq(i))
        
        elif categ=="Jeux":
            stats.append(getUserJeux(i,curseurGet,option))
        maxi=max(maxi,i["Count"])

    ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"option":option,"plus":"graph"}
    return render(request, "companion/Ranks/iFrameRanks_ranks.html", ctx)


@login_required(login_url="/login")
def iFrameGraphPeriods(request,guild,option):
    obj=request.GET.get("data")
    user=request.user

    if option in ("messages","voice","mots"):
        tableUser=getTablePerso(guild,option,user.id,False,"M","periodAsc")
        tableServ=getTablePerso(guild,option,guild,False,"M","periodAsc")
    else:
        tableUser=getTablePerso(guild,option,user.id,obj,"M","periodAsc")
        tableServ=getTablePerso(guild,option,obj,False,"M","periodAsc")
    maxiUser=max(tableUser,key=lambda x:x["Count"])
    maxiServ=max(tableServ,key=lambda x:x["Count"])

    ctx={"user":tableUser,"serv":tableServ,"id":user.id,"maxUser":maxiUser,"maxServ":maxiServ,"option":option,"plus":"graph"}
    return render(request, "companion/iFramePeriodsGraph.html", ctx)


@login_required(login_url="/login")
def iFrameGraphFirst(request,guild,option):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")

    stats=[]
    maxi=-inf
    for i in curseur.execute("SELECT * FROM firstM ORDER BY DateID DESC").fetchall():
        i["Rank"]=0

        if option in ("messages","voice","mots"):
            ligne=getUserTable(i,curseurGet,guild)

        elif option in ("emotes","reactions"):
           ligne=getEmoteTable(i,curseurGet)

        elif option in ("salons","voicechan"):
            ligne=getChannels(i,curseurGet)

        elif option=="freq":
            ligne=getFreq(i)

        ligne["Mois"]=i["Mois"]
        ligne["Annee"]=i["Annee"]
        stats.append(ligne)

        maxi=max(maxi,i["Count"])

    ctx={"rank":stats,"id":user.id,"max":maxi,"option":option,"plus":"graph"}
    return render(request, "companion/First/iFrameFirstGraph.html", ctx)


@login_required(login_url="/login")
def iFrameGraphJours(request,guild,option):
    return render(request, "companion/Blank/Empty.html")

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
