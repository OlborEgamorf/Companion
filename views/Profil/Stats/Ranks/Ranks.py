from math import inf

from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, dictOptions, dictRefCommands,
                              dictRefOptions, dictRefPlus, getGuilds,
                              getMoisAnnee, getMoisAnneePerso, getTimesMix, listeOptions,
                              tableauMois)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
def mixRank(request,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    user=request.user

    maxi=-inf
    stats=[]

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    connexionUser,curseurUser=connectSQL("OT",user,"Titres",None,None)
    
    infos=getAllInfos(curseur,curseurUser,connexionUser,user)
    full_guilds=getGuilds(request.user,curseurGet)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    if option not in ("messages","voice"):
        mois,annee,moisDB,anneeDB=getMoisAnneePerso(mois,annee)
        for guild in full_guilds:
            try:
                connexion,curseur=connectSQL(guild["ID"],dictOptions[option],"Stats",moisDB,anneeDB)
                for i in curseur.execute("SELECT * FROM perso{0}{1}{2} ORDER BY Count DESC LIMIT 200".format(moisDB,anneeDB,user.id)).fetchall():
                    if option in ("emotes","reactions"):
                        stats.append(getEmoteTable(i,curseurGet))

                    elif option in ("salons","voicechan"):
                        stats.append(getChannels(i,curseurGet))

                    elif option=="freq":
                        stats.append(getFreq(i))

                    maxi=max(maxi,i["Count"])
            except:
                pass

    else:
        mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
        for guild in full_guilds:
            try:
                connexion,curseur=connectSQL(guild["ID"],dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
                ligne=curseur.execute("SELECT * FROM {0}{1} WHERE ID={2}".format(moisDB,anneeDB,user.id)).fetchone()
                ligne["Nom"]=guild["Nom"]
                ligne["ID"]=guild["ID"]
                ligne["Icon"]=guild["Icon"]
                maxi=max(maxi,ligne["Count"])
                stats.append(ligne)
            except:
                pass

    stats.sort(key=lambda x:x["Count"],reverse=True)
    if maxi<0:
        maxi=1

    connexion.close()

    listeMois,listeAnnee=getTimesMix(list(map(lambda x:x["ID"],full_guilds)),option)

    ctx={"rank":stats,"max":maxi,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "commands":["ranks","periods"],"dictCommands":dictRefCommands,"command":"ranks",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":["","compare"], "dictPlus":dictRefPlus,"plus":"",
    "travel":True,"selector":True,"obj":None,
    "pin":getPin(user,curseurGet,"profil/{0}".format(user.id),option,"ranks","")}

    return render(request, "companion/Profil/ProfilRanks.html", ctx)



@login_required(login_url="/login")
def iFrameMixRank(request,mix,option):
    all=request.GET.get("data")
    mois,annee,obj=all.split("?")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user
    if obj=="None" or obj==None:
        obj=user.id
    
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    mix_ids,infosMix,listeMixs=getInfoMix(user,mix,curseurGet)

    stats=[]
    maxi=-inf
    nom=getNom(obj,option,curseurGet,False)
    if option in ("salons","voicechan"):
        for guild in listeMixs:
            try:
                connexion,curseur=connectSQL(guild["ID"],dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
                for i in curseur.execute("SELECT * FROM {0}{1}{2} ORDER BY Rank ASC LIMIT 150".format(moisDB,anneeDB,obj)).fetchall():
                    ligne=getUserTable(i,curseurGet,guild["ID"])
                    stats.append(ligne)
                    maxi=max(maxi,i["Count"])
            except:
                pass
        stats.sort(key=lambda x:x["Count"],reverse=True)
        if maxi<0:
            maxi=1
        ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"nom":nom,"option":option,"obj":obj}
        return render(request,"companion/Ranks/iFrameRanks_ranks.html",ctx)
    else:
        for guild in listeMixs:
            try:
                connexion,curseur=connectSQL(guild["ID"],dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
                ligne=curseur.execute("SELECT * FROM {0}{1} WHERE ID={2}".format(moisDB,anneeDB,obj)).fetchone()
                ligne["Nom"]=guild["Nom"]
                ligne["ID"]=guild["ID"]
                ligne["Icon"]=guild["Icon"]
                maxi=max(maxi,ligne["Count"])
                stats.append(ligne)
            except:
                pass
        stats.sort(key=lambda x:x["Count"],reverse=True)
        if maxi<0:
            maxi=1
        ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"nom":nom,"option":option}
        return render(request,"companion/EmotesWW/iFrameEmotesWW.html",ctx)
