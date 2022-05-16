from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..Getteurs import *
from ..outils import (collapseEvol, connectSQL, dictOptions, dictRefCommands,
                      dictRefOptions, dictRefOptionsJeux, dictRefPlus,
                      getCommands, getMoisAnnee, getPlus,
                      getTimes, listeOptions, listeOptionsJeux, rankingClassic,
                      tableauMois)

@login_required(login_url="/login")
def viewPantheon(request,guild,option):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
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

        if option in ("messages","voice","mots"):
            ligne=getUserTable(i,curseurGet,guild)

        elif option in ("emotes","reactions"):
            ligne=getEmoteTable(i,curseurGet)

        elif option in ("salons","voicechan"):
            ligne=getChannels(i,curseurGet)

        elif option=="freq":
            ligne=getFreq(i)
        
        elif categ=="Jeux":
            ligne=getUserJeux(i,curseurGet,option)
        
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
        ctx={"rank":stats,"max":maxi,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":"Olbor Track - Mondial","guildid":"jeux",
        "commands":["ranks","periods","evol","first","badges"],"dictCommands":dictRefCommands,"command":"ranks",
        "options":listeOptionsJeux,"dictOptions":dictRefOptionsJeux,"option":option,
        "lisPlus":getPlus("ranks",option),"dictPlus":dictRefPlus,"plus":"pantheon",
        "travel":False,"selector":True,"obj":None}
        return render(request, "companion/Ranks/ranks.html", ctx)
    else:
        ctx={"rank":stats,"max":maxi,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"ranks",
        "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
        "lisPlus":getPlus("ranks",option),"dictPlus":dictRefPlus,"plus":"pantheon" if option in ("messages","voice","mots") else "serv",
        "travel":False,"selector":True,"obj":None}

        return render(request, "companion/Ranks/ranksPantheon.html", ctx)