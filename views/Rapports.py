from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..outils import (avatarAnim, connectSQL, dictRefCommands, dictRefOptions,
                      getCommands, getGuild, getGuilds, getMoisAnnee, getPlus, getTimes,
                      getUser, listeOptions, tableauMois, dictRefPlus)
from ..OutilsRapports import (anecdotesSpe, descipGlobal, descipMoyennes,
                              getEarlierAnnee, getEarlierMois, hierMAG,
                              paliers)


@login_required(login_url="/login")
def viewRapports(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    if annee=="Global":
        period="global"
    elif mois=="Total":
        period="annee"
    else:
        period="mois"

    user=request.user
    listeMois,listeAnnee=getTimes(guild,option,"Stats")
    guild_full=getGuild(guild)
    full_guilds=getGuilds(user)

    if option!="freq":
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    else:
        curseurGet=None

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]
    

    # Avant Après
    connexionNow,curseurNow=connectSQL(guild,option,"Stats",tableauMois[moisDB],anneeDB)
    result=curseurNow.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC".format(moisDB,anneeDB)).fetchall()
    hier=hierMAG([moisDB,anneeDB],period,guild,option)
    if period=="mois":
        demain=getEarlierMois(tableauMois[moisDB],anneeDB,guild,option)
    elif period=="annee":
        demain=getEarlierAnnee(anneeDB,guild,option)
    elif period=="global":
        demain=None
    print(hier,demain)

    hierTable=[]
    if hier!=None:
        connexion,curseurHier=connectSQL(guild,option,"Stats",tableauMois[hier[0]],hier[1])
        resultH=curseurHier.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC".format(hier[0],hier[1])).fetchall()
        stop=15 if len(resultH)>15 else len(resultH)
        hierTable=descipGlobal(option,resultH,0,stop,hier,guild,curseurGet,False)

    stop=15 if len(result)>15 else len(result)
    now=descipGlobal(option,result,0,stop,hier,guild,curseurGet,False)

    demainTable=[]
    if demain!=None:
        connexion,curseur=connectSQL(guild,option,"Stats",tableauMois[demain[0]],demain[1])
        resultD=curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC".format(demain[0],demain[1])).fetchall()
        stop=15 if len(resultD)>15 else len(resultD)
        demainTable=descipGlobal(option,resultD,0,stop,hier,guild,curseurGet,False)
        connexion.close()

    
    # Tables obj
    tablesObj=[]
    tablesObj2=[]
    if option not in ("messages","voice","mots"):
        if result!=[]:
            start=0
            stop=8 if len(result)>8 else len(result)
            for i in range(start,stop):
                if True:
                    obj=curseurNow.execute("SELECT * FROM {0}{1}{2} ORDER BY Rank ASC".format(moisDB,anneeDB,result[i]["ID"])).fetchall()
                else:
                    continue
                stop2=6 if len(obj)>6 else len(obj)
                tablesObj.append(descipGlobal(option,obj,0,stop2,None,guild,curseurGet,True))
        if len(tablesObj)>4:
            tablesObj=tablesObj[0:4]
            tablesObj2=tablesObj[4:]


    # Paliers
    pal=paliers(curseurNow,period,(moisDB,anneeDB),option)

    
    # Détails
    descip=[]
    if result!=[]:
        descip=descipMoyennes(option,result)

    
    # Années
    annees=[]
    if period in ("mois","annee"):
        connexion,curseur=connectSQL(guild,option,"Stats","GL","")
        if period=="mois":
            table=curseur.execute("SELECT DISTINCT * FROM firstM WHERE Mois='{0}' ORDER BY Annee ASC".format(tableauMois[moisDB])).fetchall()
        elif period=="annee":
            table=curseur.execute("SELECT DISTINCT * FROM firstA ORDER BY Annee ASC").fetchall()
        for i in table:
            i["Rank"]=1
            ligne=descipGlobal(option,[i],0,1,None,guild,curseurGet,False)
            ligne[0]["Annee"]=i["Annee"]
            annees.append(ligne[0])
        connexion.close()
    
    """
    anecs=anecdotesSpe([moisDB,anneeDB],guild,option,period,curseurNow,curseurGet,curseurHier)"""

    ctx={"hier":hierTable,"now":now,"demain":demainTable,"objs1":tablesObj,"objs2":tablesObj2,"paliers":pal,"details":descip,"annees":annees,#"anecdotes":anecs,
    "avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":full_guilds,
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"rapport",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("rapport"),"dictPlus":dictRefPlus,"plus":"",
    "travel":True,"selector":False,"obj":None}

    return render(request, "companion/Rapports.html", ctx)
