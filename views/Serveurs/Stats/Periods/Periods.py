from math import inf

from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, dictOptions, getMoisAnnee,
                              getTablePerso, listeOptions, listeOptionsJeux,
                              tableauMois)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def periodsJeux(request,option):
    return viewPeriods(request,"OT",option)

def iFramePeriodsJeux(request,option):
    return iFramePeriods(request,"OT",option)

@login_required(login_url="/login")
def viewPeriods(request,guild,option):
    obj = request.GET.get("obj")
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_avatar=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Avatar"]
    user_name=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Nom"]

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
        connexion,curseur=connectSQL("OT","Titres","Titres",None,None)
        color=curseur.execute("SELECT * FROM couleurs WHERE ID={0}".format(user.id)).fetchone()
        if color!=None:
            color="#"+hex(int('%02x%02x%02x' % (color["R"], color["G"], color["B"]),base=16))[2:]

        ctx={"rankMois":None,"rankAnnee":None,"maxM":None,"maxA":None,"pagestats":True,"ot":True,
        "avatar":user_avatar,"id":user.id,"color":color,"nom":user_name,
        "guildname":"Olbor Track - Mondial","guildid":"ot/jeux",
        "command":"periods","options":listeOptionsJeux,"option":option,"plus":"",
        "travel":False,"selector":True}
    else:
        categ="Stats"
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
        color=curseurGet.execute("SELECT * FROM users JOIN users_{0} ON users.ID = users_{0}.ID WHERE users.ID={1}".format(guild,user.id)).fetchone()["Color"]

        ctx={"rankMois":None,"rankAnnee":None,"maxM":None,"maxA":None,"pagestats":True,
        "avatar":user_avatar,"id":user.id,"color":"#"+hex(color)[2:],"nom":user_name,
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "command":"periods","options":listeOptions,"option":option,"plus":"perso",
        "travel":False,"selector":True,
        "pin":getPin(user,curseurGet,guild,option,"periods","perso")}
    

    if option in ("messages","voice","mots") or categ=="Jeux":
        ctx["rankMois"]=getTablePerso(guild,dictOptions[option],user.id,False,"M","countDesc")
        ctx["rankAnnee"]=getTablePerso(guild,dictOptions[option],user.id,False,"A","countDesc")
    else:
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

        ctx["rankMois"]=getTablePerso(guild,dictOptions[option],user.id,obj,"M","countDesc")
        ctx["rankAnnee"]=getTablePerso(guild,dictOptions[option],user.id,obj,"A","countDesc")

    ctx["maxM"]=max(list(map(lambda x:x["Count"],ctx["rankMois"])))
    ctx["maxA"]=max(list(map(lambda x:x["Count"],ctx["rankAnnee"])))
    
    return render(request, "companion/Stats/Periods/periods.html", ctx)


@login_required(login_url="/login")
def iFramePeriods(request,guild,option):
    all=request.GET.get("data")
    mois,annee,obj=all.split("?")
    if len(annee)==4:
        mois=tableauMois[mois.lower()]
        annee=annee[2:4]
    if annee not in ("GL","Global"):
        annee="20"+annee
    mois,annee,moisDB,anneeDB=getMoisAnnee(tableauMois[mois],annee)
    user=request.user

    if obj=="None":
        obj=""

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
    else:
        categ="Stats"
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    
    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)
    
    rank=curseur.execute("SELECT Rank FROM {0}{1}{2} WHERE ID={3}".format(moisDB.lower(),anneeDB,obj,user.id)).fetchone()["Rank"]

    rankPlus=rank-10
    rankMoins=rank+10

    if rankPlus<0:
        rankMoins-=rankPlus

    maxi=-inf
    stats=[]

    for i in curseur.execute("SELECT * FROM {0}{1}{2} WHERE (Rank>={3} AND Rank<={4}) OR Rank=1 ORDER BY Rank ASC".format(moisDB.lower(),anneeDB,obj,rankPlus,rankMoins)).fetchall():

        if categ=="Jeux":
            stats.append(getUserJeux(i,curseurGet,option))
        else:
            stats.append(getUserTable(i,curseurGet,guild))
        maxi=max(maxi,i["Count"])
    
    connexion.close()
    ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"option":option,"obj":obj}
    return render(request, "companion/Stats/Ranks/iFrameRanks_ranks.html", ctx)
