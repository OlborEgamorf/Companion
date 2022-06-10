from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, dictOptions, listeOptions,
                                    listeOptionsJeux)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def firstGlobalJeux(request):
    return viewFirstGlobal(request,"OT")

@login_required(login_url="/login")
@CompanionStats
def viewFirstGlobal(request,guild):
    user=request.user

    statsM,statsA={},{}
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    pin=getPin(user,curseurGet,guild,"","first","")

    if guild=="OT":
        pin=getPin(user,curseurGet,"jeux","","first","")
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)

        ctx={"rankMois":statsM,"rankAnnee":statsA,"pagestats":True,"ot":True,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":"Olbor Track - Mondial","guildid":"ot/jeux",
        "command":"first","options":listeOptionsJeux,"option":"","plus":"","travel":False,"selector":True,"pin":pin}
    else:
        pin=getPin(user,curseurGet,guild,"","first","")
        categ="Stats"
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

        ctx={"rankMois":statsM,"rankAnnee":statsA,"pagestats":True,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "command":"first","options":listeOptions,"option":"","plus":"","travel":False,"selector":True,"pin":pin}

    for option in ctx["options"]:
        if option=="divers":
            continue
        
        try:
            connexion,curseur=connectSQL(guild,dictOptions[option],categ,"GL","")
        except:
            continue
    
        for i in curseur.execute("SELECT * FROM firstM ORDER BY Count DESC").fetchall():
            if i["Annee"]+i["Mois"] not in statsM:
                statsM[i["Annee"]+i["Mois"]]=[]
            i["Rank"]=0
            if categ=="Jeux":
                i["W"]=0
                i["L"]=0

            ligne=chooseGetteur(option,categ,i,guild,curseurGet,curseurGuild)

            ligne["option"]=option
            statsM[i["Annee"]+i["Mois"]].append(ligne)

        for i in curseur.execute("SELECT * FROM firstA ORDER BY Count DESC").fetchall():
            if "TO"+i["Annee"] not in statsA:
                statsA["TO"+i["Annee"]]=[]
            i["Rank"]=0
            if categ=="Jeux":
                i["W"]=0
                i["L"]=0

            ligne=chooseGetteur(option,categ,i,guild,curseurGet,curseurGuild)

            ligne["option"]=option
            statsA["TO"+i["Annee"]].append(ligne)

    dates=list(map(lambda x:x, statsM))
    annees=list(map(lambda x:x, statsA))
    dates.sort(reverse=True)
    annees.sort(reverse=True)
    ctx["dates"]=dates
    ctx["annees"]=annees
    connexion.close()
    
    return render(request, "companion/Stats/First/firstGlobal.html", ctx)

