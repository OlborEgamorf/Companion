from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..Getteurs import *
from ..outils import (connectSQL, dictOptions, dictRefCommands, dictRefOptions,
                      dictRefOptionsJeux, getCommands, getGuilds,
                      getTablePerso, listeOptions, listeOptionsJeux)

def statsHomeJeux(request):
    return viewStatsHome(request,"OT")

@login_required(login_url="/login")
def viewStatsHome(request,guild):
    user=request.user
    full_guilds=getGuilds(user)

    stats_final={}
    maxis_final={}

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_avatar=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Avatar"]
    user_name=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Nom"]

    if guild=="OT":
        liste=listeOptionsJeux[1:]
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
        color=curseurGet.execute("SELECT * FROM couleurs WHERE ID={0}".format(user.id)).fetchone()
        if color!=None:
            color="#"+hex(int('%02x%02x%02x' % (color["R"], color["G"], color["B"]),base=16))[2:]

        ctx={"avatar":user_avatar,"id":user.id,"nom":user_name,"color":color,
        "guildname":"Olbor Track - Mondial","guildid":"jeux",
        "commands":[],"dictCommands":dictRefCommands,
        "options":listeOptionsJeux,"dictOptions":dictRefOptionsJeux,"option":"home","optNotHome":listeOptionsJeux[1:],
        "travel":False,"selector":False,"obj":None}
    else:
        liste=listeOptions[1:]
        categ="Stats"
        color=curseurGet.execute("SELECT * FROM users JOIN users_{0} ON users.ID = users_{0}.ID WHERE users.ID={1}".format(guild,user.id)).fetchone()["Color"]
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
        ctx={"avatar":user_avatar,"id":user.id,"nom":user_name,"color":hex(color)[2:],
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],"guilds":full_guilds,
        "commands":getCommands("home"),"dictCommands":dictRefCommands,
        "options":listeOptions,"dictOptions":dictRefOptions,"option":"home","optNotHome":listeOptions[1:],
        "travel":False,"selector":False,"obj":None}


    for option in liste:
        maxis={}
        stats=[]
        maxi=-inf

        connexion,curseur=connectSQL(guild,dictOptions[option],categ,"GL","")

        try:
            for i in curseur.execute("SELECT * FROM glob WHERE Rank<11 ORDER BY Rank ASC").fetchall():

                if option in ("messages","voice","mots"):
                    stats.append(getUserTable(i,curseurGet,guild))

                elif option in ("emotes","reactions"):
                    stats.append(getEmoteTable(i,curseurGet))

                elif option in ("salons","voicechan"):
                    stats.append(getChannels(i,curseurGet))

                elif option=="freq":
                    stats.append(getFreq(i))
                
                elif categ=="Jeux":
                    stats.append(getUserJeux(i,curseurGet,option))

                maxi=max(maxi,i["Count"])
            
            you=curseur.execute("SELECT * FROM glob WHERE ID={0} AND Rank>10".format(user.id)).fetchone()
            if option in ("messages","voice","mots") and you!=None:
                stats.append(getUserTable(you,curseurGet,guild))

        except:
            pass

        maxis["rank"]=maxi

        first=[]
        maxi=-inf
        for i in curseur.execute("SELECT * FROM firstM ORDER BY DateID DESC LIMIT 5").fetchall():
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
                ligne=getUserJeux(i,curseurGet,option)

            ligne["Mois"]=i["Mois"]
            ligne["Annee"]=i["Annee"]
            first.append(ligne)

            maxi=max(maxi,i["Count"])
        
        maxis["first"]=maxi
        
        maxi=-inf
        if option in ("messages","voice","mots") or categ=="Jeux":
            perso=getTablePerso(guild,dictOptions[option],user.id,False,"M","periodDesc")
            perso=perso[:5] if len(perso)>5 else perso
            if perso!=[]:
                maxi=max(list(map(lambda x:x["Count"],perso)))
            else:
                maxi=0
        else:
            perso=[]
            for i in curseur.execute("SELECT * FROM firstM ORDER BY DateID DESC LIMIT 5").fetchall():
                connexionMois,curseurMois=connectSQL(guild,dictOptions[option],"Stats",i["Mois"],i["Annee"])
                try:
                    obj=curseurMois.execute("SELECT * FROM perso{0}{1}{2} ORDER BY Count DESC LIMIT 1".format(i["Mois"],i["Annee"],user.id)).fetchone()
                    if obj!=None:
                        if option in ("emotes","reactions"):
                            ligne=getEmoteTable(obj,curseurGet)

                        elif option in ("salons","voicechan"):
                            ligne=getChannels(obj,curseurGet)

                        elif option=="freq":
                            ligne=getFreq(obj)

                        ligne["Mois"]=i["Mois"]
                        ligne["Annee"]=i["Annee"]
                        perso.append(ligne)

                        maxi=max(maxi,obj["Count"])
                except:
                    pass

        maxis["perso"]=maxi
        stats_final[option]={"rank":stats.copy(),"first":first.copy(),"perso":perso.copy()}
        maxis_final[option]=maxis

    ctx["stats"]=stats_final
    ctx["max"]=maxis_final
    return render(request, "companion/newSH.html", ctx)
