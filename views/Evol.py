from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..Getteurs import *
from ..outils import (avatarAnim, collapseEvol, colorRoles, connectSQL,
                      dictOptions, dictRefCommands, dictRefOptions,
                      getCommands, getGuild, getGuilds, getMoisAnnee, getTimes,
                      getUser, listeOptions, tableauMois)


@login_required(login_url="/login")
def viewEvol(request,guild,option):
    mois,annee,obj = request.GET.get("mois"),request.GET.get("annee"),request.GET.get("obj")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)

    listeMois,listeAnnee=getTimes(guild,option)

    full_guilds=getGuilds(user)

    ctx={"rank":None,"max":None,
    "id":user.id,"color":None,"nom":user_full["user"]["username"],"avatar":user_avatar,"anim":avatarAnim(user_avatar),
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":full_guilds,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"evol",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "travel":True,"selector":True,}

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
    if option in ("messages","voice","mots"):
        ctx["obj"]=None
        obj=user.id
        user_full["roles"].sort(key=lambda x:roles_position[x], reverse=True)
        if len(user_full["roles"])==0:
            ctx["color"]=None
        else:
            ctx["color"]="#{0}".format(hex(roles_color[user_full["roles"][0]])[2:])
    else:
        if option in ("emotes","reactions"):
            full_emotes=getAllEmotes(full_guilds)
        listeObj=curseur.execute("SELECT * FROM {0}{1} WHERE Rank<150 ORDER BY Rank ASC".format(moisDB,anneeDB)).fetchall()
        if option in ("emotes","reactions"):
            listeObj=list(map(lambda x:getEmoteTable(x,full_emotes),listeObj))
        elif option in ("salons","voicechan"):
            listeObj=list(map(lambda x:getChannels(x),listeObj))
        elif option=="freq":
            listeObj=list(map(lambda x:getFreq(x),listeObj))

        if obj==None:
            obj=listeObj[0]["ID"]
        
        ctx["obj"]=int(obj)
        ctx["listeObjs"]=listeObj
            
    maxi=-inf
    
    table=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,obj)).fetchall()
    table=collapseEvol(table)   
    ctx["rank"]=table
    ctx["max"]=max(list(map(lambda x:x["Count"],table)))

    connexion.close()
    return render(request,"companion/Evol/evol.html",ctx)


@login_required(login_url="/login")
def iFrameEvol(request,guild,option):
    all=request.GET.get("data")
    jour,mois,annee,obj=all.split("?")
    if annee!="GL":
        annee="20"+annee
    mois,annee,moisDB,anneeDB=getMoisAnnee(tableauMois[mois],annee)
    user=request.user

    guild_full=getGuild(guild)
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)
    
    connexion,curseur=connectSQL(guild,"Rapports","Stats","GL","")
    tabMois=curseur.execute("SELECT * FROM archives WHERE DateID={0}{1}{2} AND Type='{3}' AND Periode='Mois'".format(anneeDB,tableauMois[moisDB],jour,dictOptions[option])).fetchall()
    tabAnnee=curseur.execute("SELECT * FROM archives WHERE DateID={0}{1}{2} AND Type='{3}' AND Periode='Annee'".format(anneeDB,tableauMois[moisDB],jour,dictOptions[option])).fetchall()
    tabGlob=curseur.execute("SELECT * FROM archives WHERE DateID={0}{1}{2} AND Type='{3}' AND Periode='Global'".format(anneeDB,tableauMois[moisDB],jour,dictOptions[option])).fetchall()

    maxi=-inf
    dictUsers={}
    ctx={"id":user.id,"mois":mois,"annee":annee,"jour":jour,"option":option}
    liste={"moisTab":tabMois,"anneeTab":tabAnnee,"globTab":tabGlob}

    if obj!="None":
        ctx["id"]=int(obj)

    if option in ("emotes","reactions"):
        full_emotes=getAllEmotes(getGuilds(user))

    for table in liste:
        stats=[]
        if option in ("messages","voice","mots"):
            for i in liste[table]:
                if i["ID"] not in dictUsers:
                    userTable=getUserTable(i,guild,roles_position,roles_color)
                    if userTable["Nom"]!="Ancien membre":
                        dictUsers[i["ID"]]=[userTable["Color"],userTable["Nom"],userTable["Avatar"]]
                    else:
                        dictUsers[i["ID"]]=[None,userTable["Nom"],None]
                    stats.append(userTable)
                else:
                    stats.append({"Count":i["Count"],"Rank":i["Rank"],"Nom":dictUsers[i["ID"]][1],"Color":dictUsers[i["ID"]][0],"Avatar":dictUsers[i["ID"]][2],"ID":i["ID"]})
                maxi=max(maxi,i["Count"])

        elif option in ("emotes","reactions"):
            for i in liste[table]:
                if i["ID"] not in dictUsers:
                    emote=getEmoteTable(i,full_emotes)
                    dictUsers[i["ID"]]=[emote["Nom"],emote["Animated"]]
                    stats.append(emote)
                else:
                    stats.append({"Count":i["Count"],"Rank":i["Rank"],"Nom":dictUsers[i["ID"]][0],"Animated":dictUsers[i["ID"]][1],"ID":i["ID"]})

                maxi=max(maxi,i["Count"])

        elif option in ("salons","voicechan"):
            for i in liste[table]:
                if i["ID"] not in dictUsers:
                    chan=getChannels(i)
                    dictUsers[i["ID"]]=chan["Nom"]
                    stats.append(chan)
                else:
                    stats.append({"Count":i["Count"],"Rank":i["Rank"],"Nom":dictUsers[i["ID"]],"ID":i["ID"]})
                
                maxi=max(maxi,i["Count"])
        
        elif option=="freq":
            for i in liste[table]:
                if i["ID"] not in dictUsers:
                    freq=getFreq(i)
                    dictUsers[i["ID"]]=freq["Nom"]
                    stats.append(freq)
                else:
                    stats.append({"Count":i["Count"],"Rank":i["Rank"],"Nom":dictUsers[i["ID"]],"ID":i["ID"]})
                
                maxi=max(maxi,i["Count"])
    
        ctx[table]=stats.copy()
        ctx[table+"Maxi"]=maxi

    connexion.close()
    if option in ("messages","voice","mots"):
        return render(request, "companion/Evol/iFrameEvol_archives.html", ctx)
    elif option in ("emotes","reactions"):
        return render(request, "companion/Evol/iFrameEvol_archivesEmotes.html", ctx)
    else:
        return render(request, "companion/Evol/iFrameEvol_archivesAutres.html", ctx)
