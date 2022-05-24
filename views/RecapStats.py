from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from companion.Decorator import CompanionStats
from django.http import JsonResponse

from companion.Getteurs import *
from companion.outils import (collapseEvol, connectSQL, dictOptions, dictRefCommands,
                      dictRefOptions, dictRefOptionsJeux, dictRefPlus,
                      getCommands, getMoisAnnee, getMoisAnneePerso, getPlus, getTableDay, getTablePerso,
                      getTimes, listeOptions, listeOptionsJeux,
                      tableauMois)


def rankJeux(request,option):
    return viewRecapStats(request,"OT",option)

@login_required(login_url="/login")
@CompanionStats
def viewRecapStats(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        pin=getPin(user,curseurGet,"jeux",option,"ranks","")
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
    else:
        pin=getPin(user,curseurGet,guild,option,"ranks","")
        categ="Stats"
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)
    connexionGL,curseurGL=connectSQL(guild,dictOptions[option],categ,"GL","")

    if option in ("messages","voice") or categ=="Jeux":
        ranks=getRanks(request,guild,option,curseur=curseur,curseurGet=curseurGet,moisDB=moisDB,anneeDB=anneeDB)
        evol=getEvol(request,guild,option,curseur=curseur,moisDB=moisDB,anneeDB=anneeDB,user=user)
        if moisDB=="glob" or moisDB=="to":
            periods=getPeriods(request,guild,option,moisDB=moisDB,anneeDB=anneeDB)
            first=getFirst(request,guild,option,curseur=curseurGL,curseurGet=curseurGet,moisDB=moisDB,anneeDB=anneeDB)
            jours=None
        else:
            jours=getJours(request,guild,option,curseur=curseurGL,moisDB=moisDB,anneeDB=anneeDB)
            periods,first=None,None
        perso=None
    else:
        ranks=getRanks(request,guild,option,curseur=curseur,curseurGet=curseurGet,moisDB=moisDB,anneeDB=anneeDB)
        mois,annee,moisDB,anneeDB=getMoisAnneePerso(mois,annee)
        perso=getPerso(request,guild,option,curseur=curseur,curseurGet=curseurGet,moisDB=moisDB,anneeDB=anneeDB,user=user)
        if moisDB=="glob" or moisDB=="to":
            first=getFirst(request,guild,option,curseur=curseurGL,curseurGet=curseurGet,moisDB=moisDB,anneeDB=anneeDB)
        else:
            first=None
        periods,jours,evol=None,None,None
    
    if categ=="Jeux":
        listeMois,listeAnnee=getTimes(guild,option,"Jeux")
        ctx={"ranks":ranks,"evol":evol,"first":first,"jours":jours,"periods":periods,"perso":perso,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":"Olbor Track - Mondial","guildid":"jeux",
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "commands":["ranks","periods","evol","first","badges"],"dictCommands":dictRefCommands,"command":"ranks",
        "options":listeOptionsJeux,"dictOptions":dictRefOptionsJeux,"option":option,
        "lisPlus":getPlus("ranks",option),"dictPlus":dictRefPlus,"plus":"",
        "travel":True,"selector":True,"obj":None,
        "pin":pin}
        return render(request, "companion/Ranks/ranks.html", ctx)
    else:
        listeMois,listeAnnee=getTimes(guild,option,"Stats")

        ctx={"ranks":ranks,"evol":evol,"first":first,"jours":jours,"periods":periods,"perso":perso,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"",
        "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
        "lisPlus":[],"dictPlus":dictRefPlus,"plus":"",
        "travel":True,"selector":True,"obj":None,
        "pin":pin}

        return render(request, "companion/RecapStats.html", ctx)


def getRanks(request,guild,option,start=0,curseur=None,curseurGet=None,moisDB=None,anneeDB=None):
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
    else:
        categ="Stats"
    if curseurGet==None:
        if categ=="Jeux":
            connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
        else:
            connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    if moisDB==None and anneeDB==None:
        mois,annee = request.GET.get("mois"),request.GET.get("annee")
        mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    if curseur==None:
        connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)

    ranks=[]
    for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT {2}".format(moisDB,anneeDB,20*(start+1))).fetchall():
        if option in ("messages","voice","mots"):
            ranks.append(getUserTable(i,curseurGet,guild))

        elif option in ("emotes","reactions"):
            ranks.append(getEmoteTable(i,curseurGet))

        elif option in ("salons","voicechan"):
            ranks.append(getChannels(i,curseurGet))

        elif option=="freq":
            ranks.append(getFreq(i))

        elif option=="divers":
            ranks.append(getDivers(i))
        
        elif categ=="Jeux":
            ranks.append(getUserJeux(i,curseurGet,option))

    lentable=curseur.execute("SELECT COUNT() AS Len FROM {0}{1}".format(moisDB,anneeDB)).fetchone()["Len"]
    maxiRanks=curseur.execute("SELECT MAX(Count) AS Max FROM {0}{1}".format(moisDB,anneeDB)).fetchone()["Max"]
    if lentable>=15*(start+1):
        ranks=ranks[15*start:15*(start+1)]
        end=True
    elif start!=0:
        ranks=ranks[15*start:]
        end=False
    else:
        end=False

    return ranks,maxiRanks,end


def getFirst(request,guild,option,start=0,curseur=None,curseurGet=None,moisDB=None,anneeDB=None):
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
    else:
        categ="Stats"
    if curseurGet==None:
        if categ=="Jeux":
            connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
        else:
            connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    if anneeDB==None:
        mois,annee = request.GET.get("mois"),request.GET.get("annee")
        mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    if curseur==None:
        connexion,curseur=connectSQL(guild,dictOptions[option],categ,"GL","")

    first=[]
    if moisDB=="to":
        table=curseur.execute("SELECT * FROM firstM WHERE Annee='{0}' ORDER BY DateID DESC".format(anneeDB)).fetchall()
        lentable=curseur.execute("SELECT COUNT() AS Len FROM firstM WHERE Annee='{0}'".format(anneeDB)).fetchone()["Len"]
        maxiFirst=curseur.execute("SELECT MAX(Count) AS Max FROM firstM WHERE Annee='{0}'".format(anneeDB)).fetchone()["Max"]
    else:
        table=curseur.execute("SELECT * FROM firstM ORDER BY DateID ASC LIMIT {0}".format(20*(start+1))).fetchall()
        lentable=curseur.execute("SELECT COUNT() AS Len FROM firstM").fetchone()["Len"]
        maxiFirst=curseur.execute("SELECT MAX(Count) AS Max FROM firstM").fetchone()["Max"]
    for i in table:
        i["Rank"]=1
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
        first.append(ligne)
        
    if lentable>=15*(start+1):
        first=first[15*start:15*(start+1)]
        end=True
    elif start!=0:
        first=first[15*start:]
        end=False
    else:
        end=False

    return first,maxiFirst,end


def getPeriods(request,guild,option,start=0,moisDB=None,anneeDB=None):
    user=request.user
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
    else:
        categ="Stats"
    if anneeDB==None:
        mois,annee = request.GET.get("mois"),request.GET.get("annee")
        mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)

    periods=getTablePerso(guild,dictOptions[option],user.id,False,"M","periodDesc")
    if moisDB=="to":
        periods=getTablePerso(guild,dictOptions[option],user.id,False,"M","periodDesc")
        periods=list(filter(lambda x:x["Annee"]==anneeDB,periods))
        
    lentable=len(periods)
    maxiPeriods=max(periods, key=lambda x:x["Count"])["Count"]
    
    if lentable>=15*(start+1):
        periods=periods[15*start:15*(start+1)]
        end=True
    elif start!=0:
        periods=periods[15*start:]
        end=False
    else:
        end=False

    return periods,maxiPeriods,end


def getEvol(request,guild,option,start=0,curseur=None,moisDB=None,anneeDB=None,user=None):
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
    else:
        categ="Stats"
    if anneeDB==None:
        mois,annee = request.GET.get("mois"),request.GET.get("annee")
        mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    if curseur==None:
        connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)
    if user==None:
        user=request.user

    evol=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,user.id)).fetchall()
    evol=collapseEvol(evol)  
    evol.reverse() 
    evol=list(filter(lambda x:not x["Collapse"],evol))
    lentable=curseur.execute("SELECT COUNT() AS Len FROM evol{0}{1}{2}".format(moisDB,anneeDB,user.id)).fetchone()["Len"]
    maxiEvol=curseur.execute("SELECT MAX(Count) AS Max FROM evol{0}{1}{2}".format(moisDB,anneeDB,user.id)).fetchone()["Max"]
    
    if lentable>=15*(start+1):
        evol=evol[15*start:15*(start+1)]
        end=True
    elif start!=0:
        evol=evol[15*start:]
        end=False
    else:
        end=False

    return evol,maxiEvol,end


def getJours(request,guild,option,start=0,curseur=None,moisDB=None,anneeDB=None):
    if anneeDB==None:
        mois,annee = request.GET.get("mois"),request.GET.get("annee")
        mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    if curseur==None:
        connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")

    jours=getTableDay(curseur,tableauMois[moisDB],anneeDB)
    jours.sort(key=lambda x:x["DateID"])
    lentable=len(jours)
    maxiJours=max(jours, key=lambda x:x["Count"])["Count"]
    
    if lentable>=15*(start+1):
        jours=jours[15*start:15*(start+1)]
        end=True
    elif start!=0:
        jours=jours[15*start:]
        end=False
    else:
        end=False

    return jours,maxiJours,end

def getPerso(request,guild,option,start=0,curseur=None,curseurGet=None,moisDB=None,anneeDB=None,user=None):
    if curseurGet==None:
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    if moisDB==None and anneeDB==None:
        mois,annee = request.GET.get("mois"),request.GET.get("annee")
        mois,annee,moisDB,anneeDB=getMoisAnneePerso(mois,annee)
    if curseur==None:
        connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
    if user==None:
        user=request.user.id

    perso=[]
    for i in curseur.execute("SELECT * FROM perso{0}{1}{2} ORDER BY Count DESC LIMIT {3}".format(moisDB,anneeDB,20*(start+1),user.id)).fetchall():
        if option in ("emotes","reactions"):
            perso.append(getEmoteTable(i,curseurGet))

        elif option in ("salons","voicechan"):
            perso.append(getChannels(i,curseurGet))

        elif option=="freq":
            perso.append(getFreq(i))

        elif option=="divers":
            perso.append(getDivers(i))


    lentable=curseur.execute("SELECT COUNT() AS Len FROM perso{0}{1}{2}".format(moisDB,anneeDB,user.id)).fetchone()["Len"]
    maxiPerso=curseur.execute("SELECT MAX(Count) AS Max FROM perso{0}{1}{2}".format(moisDB,anneeDB,user.id)).fetchone()["Max"]
    if lentable>=15*(start+1):
        perso=perso[15*start:15*(start+1)]
        end=True
    elif start!=0:
        perso=perso[15*start:]
        end=False
    else:
        end=False

    return perso,maxiPerso,end


def addMoreRecap(request,guild,option):
    command = request.GET.get("command")
    if command =="ranks":
        return JsonResponse(data=getRanks(request,guild,option),safe=False)
    if command =="first":
        return JsonResponse(data=getFirst(request,guild,option))
    if command =="periods":
        return JsonResponse(data=getPeriods(request,guild,option))
    if command =="evol":
        return JsonResponse(data=getEvol(request,guild,option))
    if command=="perso":
        return JsonResponse(data=getPerso(request,guild,option))
    if command=="jours":
        return JsonResponse(data=getJours(request,guild,option))
