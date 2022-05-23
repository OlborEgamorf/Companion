from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companion.Getteurs import *
from companion.outils import (connectSQL, dictOptions, dictRefCommands, dictRefOptions,
                      dictRefPlus, getCommands, getMoisAnnee, getPlus,
                      getTablePerso, listeOptions, rankingClassic, tableauMois)


@login_required(login_url="/login")
def viewServ(request,guild,option):
    obj = request.GET.get("obj")
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
    
    ctx={"rankMois":None,"rankAnnee":None,"maxM":None,"maxA":None,
    "avatar":user_full["Avatar"],"id":user.id,"color":None,
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"periods",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("periods",option),"dictPlus":dictRefPlus,"plus":"serv",
    "selector":True,"travel":False,
    "pin":getPin(user,curseurGet,guild,option,"periods","serv")}

    if option in ("emotes","salons","voicechan","reactions","freq","divers"):
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
        
        ctx["obj"]=int(obj)
        ctx["listeObjs"]=listeObj

        ctx["rankMois"]=getTablePerso(guild,dictOptions[option],obj,False,"M","countDesc")
        ctx["rankAnnee"]=getTablePerso(guild,dictOptions[option],obj,False,"A","countDesc")
    else:
        tableMois=getTablePerso(guild,dictOptions[option],guild,False,"M","countDesc")
        rankingClassic(tableMois)
        tableAnnee=getTablePerso(guild,dictOptions[option],guild,False,"A","countDesc")
        rankingClassic(tableAnnee)
        ctx["rankMois"]=tableMois
        ctx["rankAnnee"]=tableAnnee

    ctx["maxM"]=max(list(map(lambda x:x["Count"],ctx["rankMois"])))
    ctx["maxA"]=max(list(map(lambda x:x["Count"],ctx["rankAnnee"])))
    
    return render(request, "companion/periods.html", ctx)


@login_required(login_url="/login")
def iFrameServ(request,guild,option):
    all=request.GET.get("data")
    mois,annee,obj=all.split("?")
    if len(annee)==4:
        mois=tableauMois[mois.lower()]
        annee=annee[2:4]
    if annee not in ("GL","Global"):
        annee="20"+annee
    mois,annee,moisDB,anneeDB=getMoisAnnee(tableauMois[mois],annee)
    user=request.user

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
    elif option!="freq":
        categ="Stats"
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    else:
        categ="Stats"
    
    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)

    

    rank=curseur.execute("SELECT Rank FROM {0}{1} WHERE ID={2}".format(moisDB.lower(),anneeDB,obj)).fetchone()["Rank"]

    rankPlus=rank-10
    rankMoins=rank+10

    if rankPlus<0:
        rankMoins-=rankPlus

    maxi=-inf
    stats=[]

    for i in curseur.execute("SELECT * FROM {0}{1} WHERE (Rank>={2} AND Rank<={3}) OR Rank=1 ORDER BY Rank ASC".format(moisDB.lower(),anneeDB,rankPlus,rankMoins)).fetchall():

        if option in ("emotes","reactions"):
            stats.append(getEmoteTable(i,curseurGet))
        elif option in ("salons","voicechan"):
            stats.append(getChannels(i,curseurGet))
        elif option=="freq":
            stats.append(getFreq(i))
        elif option in ("messages","voice","mots"):
            stats.append(getUserTable(i,curseurGet,guild))
        elif categ=="Jeux":
            stats.append(getUserJeux(i,curseurGet,option))
            
        maxi=max(maxi,i["Count"])
    
    connexion.close()
    ctx={"rank":stats,"id":int(obj),"max":maxi,"mois":mois,"annee":annee,"option":option}
    return render(request, "companion/Serv/iFrameServ.html", ctx)
