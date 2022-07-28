from math import inf
from companion.tools.Decorator import CompanionStats

from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, dictOptions, getTimes, listeOptions,
                              listeOptionsJeux, rankingClassic, tableauMois)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse

def pantheonJeux(request,option):
    return viewPantheon(request,"OT",option)

@login_required(login_url="/login")
@CompanionStats
def viewPantheon(request,guild,option):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
    else:
        categ="Stats"
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
    connexion,curseur=connectSQL(guild,dictOptions[option],categ,"GL","")

    table=[]
    for i in curseur.execute("SELECT * FROM firstM").fetchall():
        connexionMois,curseurMois=connectSQL(guild,dictOptions[option],categ,i["Mois"],i["Annee"])
        table+=curseurMois.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC".format(tableauMois[i["Mois"]],i["Annee"])).fetchall()
    
    table.sort(key=lambda x:x["Count"],reverse=True)
    if len(table)>250:
        table=table[:250]
    for i in table:
        i["RankOri"]=i["Rank"]
    rankingClassic(table)

    stats=[]
    maxi=-inf
    for i in table:

        ligne=chooseGetteur(option,categ,i,guild,curseurGet,curseurGuild)
        
        ligne["RankOri"]=i["RankOri"]
        ligne["Mois"]=i["Mois"]
        ligne["Annee"]=i["Annee"]

        stats.append(ligne)
        
        maxi=max(maxi,i["Count"])

    connexion.close()

    if maxi<=0:
        maxi=1

    if categ=="Jeux":
        listeMois,listeAnnee=getTimes(guild,option,"Jeux")
        ctx={"rank":stats,"max":maxi,"pagestats":True,"ot":True,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":"Olbor Track - Mondial","guildid":"ot/jeux",
        "command":"ranks","options":listeOptionsJeux,"option":option,"plus":"pantheon",
        "travel":False,"selector":True,"obj":None,
        "pin":getPin(user,curseurGet,"ot/jeux",option,"ranks","pantheon")}
        return render(request, "companion/Stats/Ranks/Pantheon.html", ctx)
    else:
        ctx={"rank":stats,"max":maxi,"pagestats":True,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "command":"ranks","options":listeOptions,"option":option,"plus":"pantheon" if option in ("messages","voice","mots") else "serv",
        "travel":False,"selector":True,"obj":None}

        return render(request, "companion/Stats/Ranks/Pantheon.html", ctx)



def morePantheon(request,guild,option):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
    else:
        categ="Stats"
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
    connexion,curseur=connectSQL(guild,dictOptions[option],categ,"GL","")

    table=[]
    for i in curseur.execute("SELECT * FROM firstM").fetchall():
        connexionMois,curseurMois=connectSQL(guild,dictOptions[option],categ,i["Mois"],i["Annee"])
        table+=curseurMois.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC".format(tableauMois[i["Mois"]],i["Annee"])).fetchall()
    
    table.sort(key=lambda x:x["Count"],reverse=True)

    moy=round(sum(list(map(lambda x:x["Count"],table)))/len(table),2)
    med=table[len(table)//2]["Count"]
    ent=len(table)
    maxi=table[0]["Count"]

    if len(table)>50:
        table=table[:50]
    for i in table:
        i["RankOri"]=i["Rank"]
    rankingClassic(table)

    dates={}
    membres={}

    for i in table:
        if i["Mois"]+"/"+i["Annee"] not in dates:
            dates[i["Mois"]+"/"+i["Annee"]]=0
        dates[i["Mois"]+"/"+i["Annee"]]+=1

        if i["ID"] not in membres:
            membres[i["ID"]]=0
        membres[i["ID"]]+=1
    
    membres=list(map(lambda x:{"ID":x,"Count":membres[x]},membres))
    dates=list(map(lambda x:{"ID":x,"Count":dates[x]},dates))

    membres.sort(key=lambda x:x["Count"],reverse=True)
    dates.sort(key=lambda x:x["Count"],reverse=True)

    for i in membres:
        if option in ("messages","voice"):
            infos=getUserInfo(i["ID"],curseurGet,guild)
            i["Avatar"]=infos["Avatar"]
            i["Color"]=infos["Color"]
            i["Nom"]=infos["Nom"]
        else:
            nom=getNom(i["ID"],option,curseurGet,False)
            i["Nom"]=nom
        i["ID"]=str(i["ID"])

    maxiDates=max(dates,key=lambda x:x["Count"])["Count"]
    maxiMembres=max(membres,key=lambda x:x["Count"])["Count"]

    return JsonResponse(data={"moy":moy,"med":med,"membres":membres,"dates":dates,"maxiDates":maxiDates,"maxiMembres":maxiMembres,"entrees":ent,"maxi":maxi},safe=False)