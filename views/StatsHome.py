from math import inf

from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import render

from ..Getteurs import *
from ..outils import (avatarAnim, connectSQL, dictOptions, dictRefCommands,
                      dictRefOptions, getCommands, getGuild, getGuilds,
                      getMoisAnnee, getTablePerso, getUser, listeOptions,
                      tableauMois)


@login_required(login_url="/login")
def viewStatsHome(request,guild):
    user=request.user

    guild_full=getGuild(guild)
    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]
    full_guilds=getGuilds(user)

    stats_final={}
    maxis_final={}
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    ctx={
    "avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"color":getColor(user.id,guild,curseurGet),
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":full_guilds,
    "commands":getCommands("home"),"dictCommands":dictRefCommands,"command":"ranks",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":"home","optNotHome":listeOptions[1:],
    "travel":False,"selector":False,"obj":None}

    

    for option in listeOptions[1:]:
        tables=[]
        maxis={}
        for j in (("Octobre","2021","mois"),("Total","2021","annee"),("Total","Global","global")):
            stats=[]
            maxi=-inf
            mois,annee,moisDB,anneeDB=getMoisAnnee(j[0],j[1])

            connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)

            try:
                for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT 10".format(moisDB,anneeDB)).fetchall():

                    if option in ("messages","voice","mots"):
                        stats.append(getUserTable(i,curseurGet,guild))

                    elif option in ("emotes","reactions"):
                        stats.append(getEmoteTable(i,curseurGet))

                    elif option in ("salons","voicechan"):
                        stats.append(getChannels(i,curseurGet))

                    elif option=="freq":
                        stats.append(getFreq(i))

                    maxi=max(maxi,i["Count"])
            except:
                pass

            maxis[j[2]]=maxi
            connexion.close()
            tables.append(stats.copy())

        first=[]
        maxi=-inf
        connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
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

            ligne["Mois"]=i["Mois"]
            ligne["Annee"]=i["Annee"]
            first.append(ligne)

            maxi=max(maxi,i["Count"])
        
        maxis["first"]=maxi
        
        maxi=-inf
        maxiB=-inf
        if option in ("messages","voice","mots"):
            perso=getTablePerso(guild,dictOptions[option],user.id,False,"M","periodDesc")
            perso=perso[:5] if len(perso)>5 else perso
            maxi=max(list(map(lambda x:x["Count"],perso)))

            best=getTablePerso(guild,dictOptions[option],user.id,False,"M","countDesc")
            best=best[:5] if len(best)>5 else best
            maxiB=max(list(map(lambda x:x["Count"],best)))
        else:
            best=[]
            try:
                for i in curseur.execute("SELECT * FROM persoTOGL{0} ORDER BY Count DESC LIMIT 5".format(user.id)).fetchall():
                    if option in ("emotes","reactions"):
                        best.append(getEmoteTable(i,curseurGet))

                    elif option in ("salons","voicechan"):
                        best.append(getChannels(i,curseurGet))

                    elif option=="freq":
                        best.append(getFreq(i))

                    maxiB=max(maxiB,i["Count"])
            except:
                pass

            perso=[]
            for i in curseur.execute("SELECT * FROM firstM ORDER BY DateID DESC LIMIT 5").fetchall():
                connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",i["Mois"],i["Annee"])
                try:
                    obj=curseur.execute("SELECT * FROM perso{0}{1}{2} ORDER BY Count DESC LIMIT 1".format(i["Mois"],i["Annee"],user.id)).fetchone()
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
        maxis["best"]=maxiB

        stats_final[option]={"mois":tables[0].copy(),"annee":tables[1].copy(),"global":tables[2].copy(),"first":first.copy(),"perso":perso.copy(),"best":best.copy()}
        maxis_final[option]=maxis

    ctx["stats"]=stats_final
    ctx["max"]=maxis_final
    return render(request, "companion/statsHome.html", ctx)
