from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from companion.Decorator import CompanionStats

from companion.Getteurs import *
from companion.outils import (collapseEvol, connectSQL, dictOptions, dictRefCommands,
                      dictRefOptions, dictRefOptionsJeux, dictRefPlus,
                      getCommands, getMoisAnnee, getPlus, listeOptions,
                      listeOptionsJeux, tableauMois)


def firstJeux(request,option):
    return viewFirst(request,"OT",option)

def iFrameFirstJeux(request,option):
    return iFrameFirst(request,"OT",option)

@login_required(login_url="/login")
@CompanionStats
def viewFirst(request,guild,option):
    user=request.user

    maxiM,maxiA=-inf,-inf
    statsM,statsA=[],[]
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    pin=getPin(user,curseurGet,guild,option,"first","")

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        pin=getPin(user,curseurGet,"jeux",option,"first","")
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)

        ctx={"rankMois":statsM,"rankAnnee":statsA,"maxM":maxiM,"maxA":maxiA,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":"Olbor Track - Mondial","guildid":"jeux",
        "commands":["ranks","periods","evol","first","badges"],"dictCommands":dictRefCommands,"command":"first",
        "options":listeOptionsJeux,"dictOptions":dictRefOptionsJeux,"option":option,
        "lisPlus":getPlus("first",option),"dictPlus":dictRefPlus,"plus":"",
        "travel":False,"selector":True,
        "pin":pin}
    else:
        pin=getPin(user,curseurGet,guild,option,"first","")
        categ="Stats"
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

        ctx={"rankMois":statsM,"rankAnnee":statsA,"maxM":maxiM,"maxA":maxiA,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"first",
        "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
        "lisPlus":getPlus("first",option),"dictPlus":dictRefPlus,"plus":"",
        "travel":False,"selector":True,
        "pin":pin}

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,"GL","")

    for i in curseur.execute("SELECT * FROM firstM ORDER BY Count DESC").fetchall():
        i["Rank"]=0

        if option in ("messages","voice","mots"):
            ligne=getUserTable(i,curseurGet,guild)

        elif option in ("emotes","reactions"):
           ligne=getEmoteTable(i,curseurGet)

        elif option in ("salons","voicechan"):
            ligne=getChannels(i,curseurGet)

        elif option=="freq":
            ligne=getFreq(i)
        
        elif categ=="Jeux":
            i["W"]=0
            i["L"]=0
            ligne=getUserJeux(i,curseurGet,option)

        ligne["Mois"]=i["Mois"]
        ligne["Annee"]=i["Annee"]
        statsM.append(ligne)

        maxiM=max(maxiM,i["Count"])

    for i in curseur.execute("SELECT * FROM firstA ORDER BY Count DESC").fetchall():
        i["Rank"]=0

        if option in ("messages","voice","mots"):
            ligne=getUserTable(i,curseurGet,guild)

        elif option in ("emotes","reactions"):
           ligne=getEmoteTable(i,curseurGet)

        elif option in ("salons","voicechan"):
            ligne=getChannels(i,curseurGet)

        elif option=="freq":
            ligne=getFreq(i)

        elif categ=="Jeux":
            i["W"]=0
            i["L"]=0
            ligne=getUserJeux(i,curseurGet,option)

        ligne["Mois"]=i["Mois"]
        ligne["Annee"]=i["Annee"]
        statsA.append(ligne)

        maxiA=max(maxiA,i["Count"])

    ctx["maxM"]=maxiM
    ctx["maxA"]=maxiA
    connexion.close()
    
    return render(request, "companion/First/first.html", ctx)


@login_required(login_url="/login")
def iFrameFirst(request,guild,option):
    all=request.GET.get("data")
    mois,annee,id=all.split("?")
    mois=tableauMois[mois]
    if annee!="GL":
        annee="20"+annee
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user
    
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        connexion,curseur=connectSQL(guild,dictOptions[option],"Jeux",tableauMois[moisDB],anneeDB)
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
    else:
        connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    table=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,id)).fetchall()
    table=collapseEvol(table)
    table.reverse()

    ctx={"rank":table,"id":user.id,"color":None,"max":None,"mois":mois,"annee":annee,"nom":None,"option":option}

    if option in ("messages","voice","mots"):
        user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(id)).fetchone()
        ctx["color"]=getColor(id,guild,curseurGet)
        ctx["nom"]=user_full["Nom"]
    else:
        titre=curseurGet.execute("SELECT titres.Nom FROM active JOIN titres ON active.TitreID=titres.ID WHERE MembreID={0}".format(id)).fetchone()
        custom=curseurGet.execute("SELECT Custom FROM custom WHERE ID={0}".format(id)).fetchone()
        color=curseurGet.execute("SELECT * FROM couleurs WHERE ID={0}".format(id)).fetchone()
        if titre!=None:
            titre=titre["Nom"]
        else:
            titre="Inconnu"
        if custom!=None:
            custom=custom["Custom"]
            full=custom+", "+titre
        else:
            full=titre
        if color!=None:
            color="#"+hex(int('%02x%02x%02x' % (color["R"], color["G"], color["B"]),base=16))[2:]
        ctx["color"]=color
        ctx["nom"]=full

    ctx["max"]=max(list(map(lambda x:x["Count"],table)))

    connexion.close()
    return render(request,"companion/Ranks/iFrameRanks_evol.html",ctx)
