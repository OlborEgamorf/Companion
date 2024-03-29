from companion.tools.Getteurs import formatColor, getNom, getUserInfo
from companion.tools.outils import (connectSQL, dictOptions, getMoisAnnee, getMoisAnneePerso,
                                    getTablePerso, tableauMois)
from django.http import JsonResponse

from companion.views.Serveurs.Stats.Evol.EvolGraph import evolGraphCompare, linePlots


def getIndics(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    if request.GET.get("perso")!=None:
        annee="20"+annee
        mois,annee,moisDB,anneeDB=getMoisAnneePerso(mois,annee)
        moisDB=moisDB.lower()
    else:
        mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
    else:
        categ="Stats"

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)
    connexionGL,curseurGL=connectSQL(guild,dictOptions[option],categ,"GL","")
    maxi=curseur.execute("SELECT MAX(Count) AS Max FROM {0}{1}".format(moisDB,anneeDB)).fetchone()["Max"]
    mini=curseur.execute("SELECT MIN(Count) AS Min FROM {0}{1}".format(moisDB,anneeDB)).fetchone()["Min"]
    moy=int(curseur.execute("SELECT AVG(Count) AS Moy FROM {0}{1}".format(moisDB,anneeDB)).fetchone()["Moy"])
    som=curseur.execute("SELECT SUM(Count) AS Somme FROM {0}{1}".format(moisDB,anneeDB)).fetchone()["Somme"]
    ent=curseur.execute("SELECT COUNT() AS Count FROM {0}{1}".format(moisDB,anneeDB)).fetchone()["Count"]

    if option in ("messages","voice") or categ=="Jeux":
        you=curseur.execute("SELECT Count FROM {0}{1} WHERE ID={2}".format(moisDB,anneeDB,user.id)).fetchone()
        if you!=None:
            you=you["Count"]
    else:
        you=None

    table=curseur.execute("SELECT Count FROM {0}{1} ORDER BY Count DESC".format(moisDB,anneeDB)).fetchall()
    med=table[len(table)//2]["Count"]

    if moisDB=="glob":
        allMois=getTablePerso(guild,dictOptions[option],guild,False,"M","countDesc")
        allAnnee=getTablePerso(guild,dictOptions[option],guild,False,"A","countDesc")

        if option in ("messages","voice"):
            bestJour=curseurGL.execute("SELECT * FROM dayRank ORDER BY Count DESC").fetchone()
        else:
            bestJour=None
        bestMois=allMois[0]
        bestAnnee=allAnnee[0]
    elif moisDB=="to":
        allMois=getTablePerso(guild,dictOptions[option],guild,False,"M","countDesc")
        allMois=list(filter(lambda x:x["Annee"]==anneeDB, allMois))

        if option in ("messages","voice"):
            bestJour=curseurGL.execute("SELECT * FROM dayRank WHERE Annee='{0}' ORDER BY Count DESC".format(anneeDB)).fetchone()
        else:
            bestJour=None
        bestMois=allMois[0]
        bestAnnee=None
    else:
        if option in ("messages","voice"):
            bestJour=curseurGL.execute("SELECT * FROM dayRank WHERE Annee='{0}' AND Mois='{1}' ORDER BY Count DESC".format(anneeDB,tableauMois[moisDB])).fetchone()
        else:
            bestJour=None
        bestMois,bestAnnee=None,None

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    color=curseurGet.execute("SELECT * FROM users JOIN users_{0} ON users.ID = users_{0}.ID WHERE users.ID={1}".format(guild,user.id)).fetchone()["Color"]
    color=formatColor(color)

    return JsonResponse(data={"max":maxi,"min":mini,"moy":moy,"sum":som,"entrees":ent,"you":you,"med":med,"bestJour":bestJour,"bestMois":bestMois,"bestAnnee":bestAnnee,"color":color},safe=False)




def getHistoFirst(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    connexionArc,curseurArc=connectSQL(guild,"Rapports","Stats","GL","")
    if moisDB=="glob":
        premiers=curseurArc.execute("SELECT * FROM archives WHERE Type='{0}' AND Periode='Global' AND Rank=1 ORDER BY DateID ASC".format(dictOptions[option])).fetchall()
        if len(premiers)==0:
            histo=None
        else:
            histo=[]
            idFirst=premiers[0]["ID"]
            date=premiers[0]["DateID"]
            jours=0
            for i in premiers:
                if i["ID"]!=idFirst:
                    if option in ("messages","voice","mots"):
                        infos=getUserInfo(idFirst,curseurGet,guild)
                        histo.append({"ID":str(idFirst),"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(i["DateID"])),"Nom":infos["Nom"],"Avatar":infos["Avatar"],"Jours":jours,"Color":infos["Color"]})
                    else:
                        infos=getNom(idFirst,option,curseurGet,False)
                        histo.append({"ID":str(idFirst),"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(i["DateID"])),"Nom":infos,"Jours":jours})
                    idFirst=i["ID"]
                    date=i["DateID"]
                    jours=0
                jours+=1

            if option in ("messages","voice","mots"):
                infos=getUserInfo(idFirst,curseurGet,guild)
                histo.append({"ID":str(idFirst),"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"En cours","Nom":infos["Nom"],"Avatar":infos["Avatar"],"Jours":jours,"Color":infos["Color"]})
            else:
                infos=getNom(idFirst,option,curseurGet,False)
                histo.append({"ID":str(idFirst),"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"En cours","Nom":infos,"Jours":jours})

    elif moisDB=="to":
        premiers=curseurArc.execute("SELECT * FROM archives WHERE Type='{0}' AND Periode='Annee' AND Annee='{1}' AND Rank=1 ORDER BY DateID ASC".format(dictOptions[option],anneeDB)).fetchall()
        if len(premiers)==0:
            histo=None
        else:
            histo=[]
            idFirst=premiers[0]["ID"]
            date=premiers[0]["DateID"]
            jours=0
            for i in premiers:
                if i["ID"]!=idFirst:
                    if option in ("messages","voice","mots"):
                        infos=getUserInfo(idFirst,curseurGet,guild)
                        histo.append({"ID":str(idFirst),"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(i["DateID"])),"Nom":infos["Nom"],"Avatar":infos["Avatar"],"Jours":jours,"Color":infos["Color"]})
                    else:
                        infos=getNom(idFirst,option,curseurGet,False)
                        histo.append({"ID":str(idFirst),"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(i["DateID"])),"Nom":infos,"Jours":jours})
                    idFirst=i["ID"]
                    date=i["DateID"]
                    jours=0
                jours+=1

            if option in ("messages","voice","mots"):
                infos=getUserInfo(idFirst,curseurGet,guild)
                histo.append({"ID":str(idFirst),"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"En cours","Nom":infos["Nom"],"Avatar":infos["Avatar"],"Jours":jours,"Color":infos["Color"]})
            else:
                infos=getNom(idFirst,option,curseurGet,False)
                histo.append({"ID":str(idFirst),"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"En cours","Nom":infos,"Jours":jours})

    else:
        premiers=curseurArc.execute("SELECT * FROM archives WHERE Type='{0}' AND Periode='Mois' AND Mois='{1}' AND Annee='{2}' AND Rank=1 ORDER BY DateID ASC".format(dictOptions[option],tableauMois[moisDB],anneeDB)).fetchall()
        if len(premiers)==0:
            histo=None
        else:
            histo=[]
            idFirst=premiers[0]["ID"]
            date=premiers[0]["DateID"]
            jours=0
            for i in premiers:
                if i["ID"]!=idFirst:
                    if option in ("messages","voice","mots"):
                        infos=getUserInfo(idFirst,curseurGet,guild)
                        histo.append({"ID":str(idFirst),"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(i["DateID"])),"Nom":infos["Nom"],"Avatar":infos["Avatar"],"Jours":jours,"Color":infos["Color"]})
                    else:
                        infos=getNom(idFirst,option,curseurGet,False)
                        histo.append({"ID":str(idFirst),"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(i["DateID"])),"Nom":infos,"Jours":jours})
                    idFirst=i["ID"]
                    date=i["DateID"]
                    jours=0
                jours+=1

            if option in ("messages","voice","mots"):
                infos=getUserInfo(idFirst,curseurGet,guild)
                histo.append({"ID":str(idFirst),"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"En cours","Nom":infos["Nom"],"Avatar":infos["Avatar"],"Jours":jours,"Color":infos["Color"]})
            else:
                infos=getNom(idFirst,option,curseurGet,False)
                histo.append({"ID":str(idFirst),"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"En cours","Nom":infos,"Jours":jours})

    return JsonResponse(data=histo,safe=False)


def getEvol(request,guild,option):
    mois,annee,obj = request.GET.get("mois"),request.GET.get("annee"),request.GET.get("obj")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
    else:
        categ="Stats"

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)

    if user.id==int(obj):
        graph=linePlots(guild,option,curseur,curseurGet,curseurGuild,user.id,moisDB,anneeDB,True,categ)
    else:
        if option in ("messages","voice"):
            infos1=getUserInfo(user.id,curseurGet,guild)
            infos2=getUserInfo(obj,curseurGet,guild)
            graph=evolGraphCompare(option,curseur,user.id,obj,moisDB,anneeDB,infos1["Nom"],infos2["Nom"],infos1["Color"],infos2["Color"])
        else:
            nom=getNom(obj,option,curseurGet,False)
            graph=evolGraphCompare(option,curseur,user.id,obj,moisDB,anneeDB,None,nom,None,"turquoise")
    return JsonResponse(data={"graph":graph},safe=False)


def getAvAp(request,guild,option):
    mois,annee,obj = request.GET.get("mois"),request.GET.get("annee"),request.GET.get("obj")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
    else:
        categ="Stats"

    table=[]
    if moisDB=="to":
        allAnnee=getTablePerso(guild,dictOptions[option],guild,False,"A","periodAsc")
        for i in allAnnee:
            table.append(avApIndics(guild,option,categ,"TO",i["Annee"],user))
    else:
        allMois=getTablePerso(guild,dictOptions[option],guild,False,"M","countDesc")
        bestMois=allMois[0]
        moisPrec,anneePrec=datePrec(tableauMois[moisDB],anneeDB)
        moisSuiv,anneeSuiv=dateSuiv(tableauMois[moisDB],anneeDB)

        try:
            table.append(avApIndics(guild,option,categ,moisPrec,anneePrec,user))
        except:
            pass
        table.append(avApIndics(guild,option,categ,tableauMois[moisDB],anneeDB,user))
        try:
            table.append(avApIndics(guild,option,categ,moisSuiv,anneeSuiv,user))
        except:
            pass

        if bestMois["Annee"] not in (anneePrec,anneeSuiv,anneeDB) and tableauMois[bestMois["Mois"]] not in (moisPrec,moisSuiv,moisDB):
            table.append(avApIndics(guild,option,categ,bestMois["Mois"],bestMois["Annee"],user))
    
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    color=curseurGet.execute("SELECT * FROM users JOIN users_{0} ON users.ID = users_{0}.ID WHERE users.ID={1}".format(guild,user.id)).fetchone()["Color"]
    color=formatColor(color)

    return JsonResponse(data={"table":table,"maxSum":max(table, key=lambda x:x["sum"])["sum"],"maxVal":max(table, key=lambda x:x["max"])["max"],"color":color},safe=False)


def avApIndics(guild,option,categ,mois,anneeDB,user):
    connexion,curseur=connectSQL(guild,dictOptions[option],categ,mois,anneeDB)
    maxi=curseur.execute("SELECT MAX(Count) AS Max FROM {0}{1}".format(tableauMois[mois],anneeDB)).fetchone()["Max"]
    moy=int(curseur.execute("SELECT AVG(Count) AS Moy FROM {0}{1}".format(tableauMois[mois],anneeDB)).fetchone()["Moy"])
    som=curseur.execute("SELECT SUM(Count) AS Somme FROM {0}{1}".format(tableauMois[mois],anneeDB)).fetchone()["Somme"]
    you=curseur.execute("SELECT Count FROM {0}{1} WHERE ID={2}".format(tableauMois[mois],anneeDB,user.id)).fetchone()
    if you!=None:
        you=you["Count"]
    return {"max":maxi,"moy":moy,"sum":som,"you":you,"mois":mois,"annee":anneeDB}

def datePrec(mois,annee):
    if mois=="01":
        annee=str(int(annee)-1)
        mois="12"
    else:
        mois=int(mois)-1
        if mois<10:
            mois="0"+str(mois)
        else:
            mois=str(mois)
    return mois,annee

def dateSuiv(mois,annee):
    if mois=="12":
        annee=str(int(annee)+1)
        mois="01"
    else:
        mois=int(mois)+1
        if mois<10:
            mois="0"+str(mois)
        else:
            mois=str(mois)
    return mois,annee