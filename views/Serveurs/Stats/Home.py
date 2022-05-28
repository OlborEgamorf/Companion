from math import inf

from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, dictOptions, getTablePerso,
                              listeOptions, listeOptionsJeux)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def statsHomeJeux(request):
    return viewStatsHome(request,"OT")

@login_required(login_url="/login")
def viewStatsHome(request,guild):
    user=request.user

    stats_final=[]
    perso_final=[]

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_avatar=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Avatar"]
    user_name=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Nom"]

    if guild=="OT":
        pin=getPin(user,curseurGet,"jeux","home","","")
        liste=listeOptionsJeux.copy()
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
        color=curseurGet.execute("SELECT * FROM couleurs WHERE ID={0}".format(user.id)).fetchone()
        if color!=None:
            color="#"+hex(int('%02x%02x%02x' % (color["R"], color["G"], color["B"]),base=16))[2:]

        ctx={"avatar":user_avatar,"id":user.id,"nom":user_name,"color":color,
        "guildname":"Olbor Track - Mondial","guildid":"ot/jeux",
        "options":listeOptionsJeux,"option":"","command":"home","optNotHome":liste,
        "travel":False,"selector":False,"obj":None,"pin":pin,"pagestats":True,"ot":True}
    else:
        pin=getPin(user,curseurGet,guild,"home","","")
        liste=listeOptions.copy()
        liste.remove("divers")
        categ="Stats"
        color=curseurGet.execute("SELECT * FROM users JOIN users_{0} ON users.ID = users_{0}.ID WHERE users.ID={1}".format(guild,user.id)).fetchone()["Color"]
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
        ctx={"avatar":user_avatar,"id":user.id,"nom":user_name,"color":"#"+hex(color)[2:],
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "options":listeOptions,"command":"home","optNotHome":liste,
        "travel":False,"selector":False,"obj":None,"pin":pin,"pagestats":True,}


    for option in liste:
        connexion,curseur=connectSQL(guild,dictOptions[option],categ,"GL","")
        stats={}
        perso={}
        try:
            top2=curseur.execute("SELECT * FROM glob ORDER BY Count DESC LIMIT 2").fetchall()
            first=chooseGetteur(option,categ,top2[0],guild,curseurGet)

            if len(top2)==2:
                deux=chooseGetteur(option,categ,top2[1],guild,curseurGet)
            else:
                deux=None

            
            table=curseur.execute("SELECT * FROM evolglob{0} ORDER BY DateID DESC".format(first["ID"])).fetchall()
            end=False
            i=1
            while i<len(table) and not end:
                if table[i]["Rank"]!=1:
                    end=True
                else:
                    i+=1
            date="{0}/{1}/{2}".format(table[i-1]["Jour"],table[i-1]["Mois"],table[i-1]["Annee"])
            
            stats={"first":first,"deux":deux,"depuis":date,"option":option}

        except:
            pass

        try:
            if option in ("messages","voice") or categ=="Jeux":
                glob=curseur.execute("SELECT * FROM glob WHERE ID={0}".format(user.id)).fetchone()
                periods=getTablePerso(guild,dictOptions[option],user.id,False,"M","countDesc")
                perso={"rang":glob["Rank"],"count":glob["Count"],"option":option,"bestperiod":periods[0]}
            else:
                top2=curseur.execute("SELECT * FROM persoTOGL{0} ORDER BY Count DESC LIMIT 2".format(user.id)).fetchall()
                firstPerso=chooseGetteur(option,categ,top2[0],guild,curseurGet)

                if len(top2)==2:
                    deuxPerso=chooseGetteur(option,categ,top2[1],guild,curseurGet)
                else:
                    deuxPerso=None
                perso={"first":firstPerso,"deux":deuxPerso,"option":option}

        except:
            pass
        
        if stats!={}:
            stats_final.append(stats)
        if perso!={}:
            perso_final.append(perso)

    ctx["stats"]=stats_final
    ctx["perso"]=perso_final
    return render(request, "companion/Stats/Home.html", ctx)
