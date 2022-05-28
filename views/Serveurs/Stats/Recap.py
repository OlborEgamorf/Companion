from math import inf

from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import *
from companion.tools.outils import (collapseEvol, connectSQL, dictOptions,
                              getMoisAnnee, getMoisAnneePerso, getTableDay,
                              getTablePerso, getTimes, listeOptions,
                              listeOptionsJeux, tableauMois)
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render


def recapJeux(request,option):
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
        color=curseurGet.execute("SELECT * FROM couleurs WHERE ID={0}".format(user.id)).fetchone()
        if color!=None:
            color="#"+hex(int('%02x%02x%02x' % (color["R"], color["G"], color["B"]),base=16))[2:]
    else:
        pin=getPin(user,curseurGet,guild,option,"ranks","")
        categ="Stats"
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
        color=curseurGet.execute("SELECT * FROM users JOIN users_{0} ON users.ID = users_{0}.ID WHERE users.ID={1}".format(guild,user.id)).fetchone()["Color"]
        color="#"+hex(color)[2:]
        nom=user_full["Nom"]

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)
    connexionGL,curseurGL=connectSQL(guild,dictOptions[option],categ,"GL","")

    if option in ("messages","voice") or categ=="Jeux":
        ranks=getRanks(request,guild,option,"",curseur=curseur,curseurGet=curseurGet,moisDB=moisDB,anneeDB=anneeDB)
        evol=getEvol(request,guild,option,curseur=curseur,moisDB=moisDB,anneeDB=anneeDB,user=user.id)
        if moisDB=="glob" or moisDB=="to":
            periods=getPeriods(request,guild,option,moisDB=moisDB,anneeDB=anneeDB)
            first=getFirst(request,guild,option,curseur=curseurGL,curseurGet=curseurGet,moisDB=moisDB,anneeDB=anneeDB)
            jours=None
        else:
            if categ!="Jeux":
                jours=getJours(request,guild,option,curseur=curseurGL,moisDB=moisDB,anneeDB=anneeDB)
            else:
                jours=None
            periods,first=None,None
        perso=None
        obj,listeObj=None,None
    else:
        obj=request.GET.get("obj")
        listeObj=curseurGL.execute("SELECT * FROM glob ORDER BY Count DESC LIMIT 150").fetchall()
        if option in ("emotes","reactions"):
            listeObj=[{"ID":0,"Nom":"Serveur"}]+list(map(lambda x:getEmoteTable(x,curseurGet),listeObj))
        elif option in ("salons","voicechan"):
            listeObj=[{"ID":0,"Nom":"Serveur"}]+list(map(lambda x:getChannels(x,curseurGet),listeObj))
        elif option=="freq":
            listeObj=[{"ID":0,"Nom":"Serveur"}]+list(map(lambda x:getFreq(x),listeObj))
        elif option=="divers":
            listeObj=[{"ID":0,"Nom":"Serveur"}]+list(map(lambda x:getDivers(x),listeObj))
        
        if obj==None or obj=="0":
            ranks=getRanks(request,guild,option,"",curseur=curseur,curseurGet=curseurGet,moisDB=moisDB,anneeDB=anneeDB)
            if moisDB=="glob" or moisDB=="to":
                first=getFirst(request,guild,option,curseur=curseurGL,curseurGet=curseurGet,moisDB=moisDB,anneeDB=anneeDB)
            else:
                first=None
            mois,annee,moisDB,anneeDB=getMoisAnneePerso(mois,annee)
            perso=getPerso(request,guild,option,curseur=curseur,curseurGet=curseurGet,moisDB=moisDB,anneeDB=anneeDB,user=user)
            
            periods,jours,evol=None,None,None
            obj=0
        else:
            obj=int(obj)
            color=None
            ranks=getRanks(request,guild,option,obj,curseur=curseur,curseurGet=curseurGet,moisDB=moisDB,anneeDB=anneeDB)
            evol=getEvol(request,guild,option,curseur=curseur,moisDB=moisDB,anneeDB=anneeDB,user=obj)
            if moisDB=="glob" or moisDB=="to":
                periods=getPeriods(request,guild,option,moisDB=moisDB,anneeDB=anneeDB)
                first=getFirst(request,guild,option,curseur=curseurGL,curseurGet=curseurGet,moisDB=moisDB,anneeDB=anneeDB)
            else:
                periods,first=None,None
            perso,jours=None,None
    
    if categ=="Jeux":
        listeMois,listeAnnee=getTimes(guild,option,"Jeux")
        ctx={"ranks":ranks,"evol":evol,"first":first,"jours":jours,"periods":periods,"perso":perso,
        "avatar":user_full["Avatar"],"id":str(user.id),"nom":user_full["Nom"],"color":color,
        "guildname":"Olbor Track - Mondial","guildid":"ot/jeux",
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "command":"ranks","options":listeOptionsJeux,"option":option,"plus":"",
        "travel":True,"selector":True,"obj":obj,"ot":True,"pagestats":True,
        "pin":pin}
        return render(request, "companion/Stats/Recap.html", ctx)
    else:
        listeMois,listeAnnee=getTimes(guild,option,"Stats")

        ctx={"ranks":ranks,"evol":evol,"first":first,"jours":jours,"periods":periods,"perso":perso,
        "avatar":user_full["Avatar"],"id":str(user.id),"nom":user_full["Nom"],"color":color,
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "command":"recap","options":listeOptions,"option":option,"plus":"",
        "travel":True,"selector":True,"obj":obj,"listeObjs":listeObj,"pagestats":True,
        "pin":pin}

        return render(request, "companion/Stats/Recap.html", ctx)


def getRanks(request,guild,option,obj,start=0,curseur=None,curseurGet=None,moisDB=None,anneeDB=None):
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
    for i in curseur.execute("SELECT * FROM {0}{1}{2} ORDER BY Rank ASC LIMIT {3}".format(moisDB,anneeDB,obj,20*(start+1))).fetchall():
        i["ID"]=str(i["ID"])
        ranks.append(chooseGetteur(option,categ,i,guild,curseurGet))

    if categ=="Jeux":
        for i in ranks:
            if i["Emote"]!=None:
                i["Emote"]=str(i["Emote"])

    lentable=curseur.execute("SELECT COUNT() AS Len FROM {0}{1}{2}".format(moisDB,anneeDB,obj)).fetchone()["Len"]
    maxiRanks=curseur.execute("SELECT MAX(Count) AS Max FROM {0}{1}{2}".format(moisDB,anneeDB,obj)).fetchone()["Max"]
    if lentable>15*(start+1):
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
        table=curseur.execute("SELECT * FROM firstM ORDER BY DateID DESC LIMIT {0}".format(20*(start+1))).fetchall()
        lentable=curseur.execute("SELECT COUNT() AS Len FROM firstM").fetchone()["Len"]
        maxiFirst=curseur.execute("SELECT MAX(Count) AS Max FROM firstM").fetchone()["Max"]
    for i in table:
        i["Rank"]=1
        i["ID"]=str(i["ID"])
        if categ=="Jeux":
            i["W"]=0
            i["L"]=0
        
        ligne=chooseGetteur(option,categ,i,guild,curseurGet)

        ligne["Mois"]=i["Mois"]
        ligne["Annee"]=i["Annee"]
        first.append(ligne)
    
    if categ=="Jeux":
        for i in first:
            if i["Emote"]!=None:
                i["Emote"]=str(i["Emote"])

    if lentable>15*(start+1):
        first=first[15*start:15*(start+1)]
        end=True
    elif start!=0:
        first=first[15*start:]
        end=False
    else:
        end=False

    return first,maxiFirst,end


def getPeriods(request,guild,option,start=0,moisDB=None,anneeDB=None):
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
    else:
        categ="Stats"
    if option in ("messages","voice") or categ=="Jeux":
        user=request.user.id
    else:
        user=request.GET.get("obj")
    if anneeDB==None:
        mois,annee = request.GET.get("mois"),request.GET.get("annee")
        mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)

    periods=getTablePerso(guild,dictOptions[option],user,False,"M","periodDesc")
    if moisDB=="to":
        periods=list(filter(lambda x:x["Annee"]==anneeDB,periods))
        
    lentable=len(periods)
    maxiPeriods=max(periods, key=lambda x:x["Count"])["Count"]
    
    if lentable>15*(start+1):
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
        if option in ("messages","voice") or categ=="Jeux":
            user=request.user.id
        else:
            user=request.GET.get("obj")

    evol=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,user)).fetchall()
    evol=collapseEvol(evol)  
    evol.reverse() 
    evol=list(filter(lambda x:not x["Collapse"],evol))
    lentable=len(evol)
    maxiEvol=curseur.execute("SELECT MAX(Count) AS Max FROM evol{0}{1}{2}".format(moisDB,anneeDB,user)).fetchone()["Max"]
    
    if lentable>15*(start+1):
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
    
    if lentable>15*(start+1):
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
        connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",moisDB,anneeDB)
    if user==None:
        user=request.user

    perso=[]
    for i in curseur.execute("SELECT * FROM perso{0}{1}{2} ORDER BY Count DESC LIMIT {3}".format(moisDB,anneeDB,user.id,20*(start+1))).fetchall():
        i["ID"]=str(i["ID"])
        perso.append(chooseGetteur(option,"Stats",i,guild,curseurGet))


    lentable=curseur.execute("SELECT COUNT() AS Len FROM perso{0}{1}{2}".format(moisDB,anneeDB,user.id)).fetchone()["Len"]
    maxiPerso=curseur.execute("SELECT MAX(Count) AS Max FROM perso{0}{1}{2}".format(moisDB,anneeDB,user.id)).fetchone()["Max"]
    if lentable>15*(start+1):
        perso=perso[15*start:15*(start+1)]
        end=True
    elif start!=0:
        perso=perso[15*start:]
        end=False
    else:
        end=False

    return perso,maxiPerso,end

def addMoreRecapJeux(request,option):
    return addMoreRecap(request,"OT",option)

def addMoreRecap(request,guild,option):
    command = request.GET.get("command")
    start=request.GET.get("start")
    obj=request.GET.get("obj")
    if obj=="None" or obj=="0":
        obj=""
    if command =="ranks":
        return JsonResponse(data=getRanks(request,guild,option,obj,start=int(start)),safe=False)
    if command =="first":
        return JsonResponse(data=getFirst(request,guild,option,start=int(start)),safe=False)
    if command =="periods":
        return JsonResponse(data=getPeriods(request,guild,option,start=int(start)),safe=False)
    if command =="evol":
        return JsonResponse(data=getEvol(request,guild,option,start=int(start)),safe=False)
    if command=="perso":
        return JsonResponse(data=getPerso(request,guild,option,start=int(start)),safe=False)
    if command=="jours":
        return JsonResponse(data=getJours(request,guild,option,start=int(start)),safe=False)
