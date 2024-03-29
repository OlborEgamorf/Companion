from math import inf

from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, dictOptions, getMoisAnnee,
                              getTablePerso, listeOptions, rankingClassic,
                              tableauMois)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
def viewServ(request,guild,option):
    obj = request.GET.get("obj")
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
    
    ctx={"rankMois":None,"rankAnnee":None,"maxM":None,"maxA":None,"pagestats":True,
    "avatar":user_full["Avatar"],"id":user.id,"color":None,
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "command":"periods","options":listeOptions,"option":option,"plus":"serv","selector":True,"travel":False,
    "pin":getPin(user,curseurGet,guild,option,"periods","serv")}

    if option in ("emotes","salons","voicechan","reactions","freq","divers"):
        connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
        listeObj=objSelector(guild,option,"Stats",user,curseurGet,curseurGuild)

        if obj==None:
            obj=listeObj[0]["ID"]
        elif option in ("salons","voicechan"):
            hide=curseurGuild.execute("SELECT * FROM chans WHERE ID={0}".format(obj)).fetchone()
            assert hide!=None and not hide["Hide"]
        
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
    
    return render(request, "companion/Stats/Periods/periods.html", ctx)

def iFrameServJeux(request,option):
    return iFrameServ(request,"OT",option)

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
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)

    rank=curseur.execute("SELECT Rank FROM {0}{1} WHERE ID={2}".format(moisDB.lower(),anneeDB,obj)).fetchone()["Rank"]

    rankPlus=rank-10
    rankMoins=rank+10

    if rankPlus<0:
        rankMoins-=rankPlus

    maxi=-inf
    stats=[]

    for i in curseur.execute("SELECT * FROM {0}{1} WHERE (Rank>={2} AND Rank<={3}) OR Rank=1 ORDER BY Rank ASC".format(moisDB.lower(),anneeDB,rankPlus,rankMoins)).fetchall():
        stats.append(chooseGetteur(option,categ,i,guild,curseurGet,curseurGuild)) 
        maxi=max(maxi,i["Count"])
    
    connexion.close()
    ctx={"rank":stats,"id":int(obj),"max":maxi,"mois":mois,"annee":annee,"option":option}
    return render(request, "companion/Stats/Periods/iFrameServ.html", ctx)
