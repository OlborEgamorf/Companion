from math import inf

import requests
from companion.Getteurs import getChannels, getEmoteTable, getFreq
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..outils import (colorRoles, connectSQL, dictOptions,
                      dictRefCommands, dictRefOptions, dictRefPlus,
                      getCommands, getGuild, getMoisAnnee,
                      getMoisAnneePerso, getPlus, getTableRoles,
                      getTableRolesMem, getTimes, listeOptions,
                      rankingClassic, tableauMois)


@login_required(login_url="/login")
def viewRoles(request,guild,option):
    mois,annee,obj = request.GET.get("mois"),request.GET.get("annee"),request.GET.get("obj")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=getGuild(guild)
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)

    listeMois,listeAnnee=getTimes(guild,option,"Stats")

    stats=[]
    maxi=-inf

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")

    listeObj=curseur.execute("SELECT * FROM glob ORDER BY Count DESC").fetchall()
    if option in ("emotes","reactions"):
        listeObj=list(map(lambda x:getEmoteTable(x,curseurGet),listeObj))
    elif option in ("salons","voicechan"):
        listeObj=list(map(lambda x:getChannels(x,curseurGet),listeObj))
    elif option=="freq":
        listeObj=list(map(lambda x:getFreq(x),listeObj))
    roles=list(map(lambda x:{"Nom":roles_name[x],"ID":x}, roles_name))
    listeObj=roles[1:]+listeObj

    if len(listeObj)>300:
        listeObj=listeObj[:300]

    ctx={"rank":stats,"max":maxi,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"roles",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
    "lisPlus":getPlus("roles",option),"dictPlus":dictRefPlus,"plus":"",
    "travel":True,"selector":True,"obj":None,"listeObjs":listeObj}

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
    members=requests.get("https://discord.com/api/v9/guilds/{0}/members?limit=1000".format(guild),headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})
    if members.status_code==200:
        members=members.json()
    if option in ("messages","voice","mots"):
        table=getTableRoles(curseur,members,moisDB+anneeDB)
        for i in table:
            stats.append({"Rank":0,"Count":table[i],"Color":"#{0}".format(hex(roles_color[i])[2:]),"Nom":roles_name[i],"ID":i})
        rankingClassic(stats)
    else:
        if obj==None:
            obj=listeObj[0]["ID"]
        ctx["obj"]=int(obj)
        roles_id=list(map(lambda x:x["id"],guild_full["roles"]))
        if obj in roles_id:
            mois,annee,moisDB,anneeDB=getMoisAnneePerso(mois,annee)
            table=getTableRolesMem(curseur,members,obj,moisDB,anneeDB)
            for i in table:
                opti={"ID":i,"Count":table[i],"Rank":0}
                if option in ("emotes","reactions"):
                    opti=getEmoteTable(opti,curseurGet)

                elif option in ("salons","voicechan"):
                    opti=getChannels(opti,curseurGet)

                elif option=="freq":
                    opti=getFreq(opti)

                opti["Color"]=None
                stats.append(opti)
            rankingClassic(stats)
        else:
            table=getTableRoles(curseur,members,moisDB+anneeDB+str(obj))
            for i in table:
                stats.append({"Rank":0,"Count":table[i],"Color":"#{0}".format(hex(roles_color[i])[2:]),"Nom":roles_name[i],"ID":i})
            rankingClassic(stats)
        

    ctx["max"]=max(list(map(lambda x:x["Count"],stats)))
    connexion.close()
    return render(request,"companion/roles.html",ctx)
    

"""@login_required(login_url="/login")
def iFrameRoles(request,guild,option):
    all=request.GET.get("data")
    mois,annee,role=all.split("?")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    guild_full=getGuild(guild)
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)
    
    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)

    members=requests.get("https://discord.com/api/v9/guilds/{0}/members?limit=1000".format(guild),headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})
    if members.status_code==200:
        members=members.json()

    maxi=-inf
    stats=[]

    for i in members:
        if role in i["roles"]:
            table=curseur.execute("SELECT * FROM {0}{1} WHERE ID={2}".format(moisDB,anneeDB,i["user"]["id"])).fetchone()
            if table!=None:
                i["roles"].sort(key=lambda x:roles_position[x], reverse=True)
                if len(i["roles"])==0:
                    color=i
                else:
                    color="#{0}".format(hex(roles_color[i["roles"][0]])[2:])
                stats.append({"Count":table["Count"],"Rank":table["Rank"],"Nom":i["user"]["username"],"Color":color,"Avatar":i["user"]["avatar"],"ID":i["user"]["id"]})

                maxi=max(maxi,table["Count"])
    
    stats.sort(key=lambda x:x["Rank"])
    connexion.close()
    ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"role":roles_name[role],"option":option}
    return render(request, "companion/Ranks/iFrameRanks_ranks.html", ctx)"""


@login_required(login_url="/login")
def iFrameRoles(request,guild,option):
    all=request.GET.get("data")
    mois,annee,obj,objrank=all.split("?")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    guild_full=getGuild(guild)
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)
    
    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)

    members=requests.get("https://discord.com/api/v9/guilds/{0}/members?limit=1000".format(guild),headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})
    if members.status_code==200:
        members=members.json()

    maxi=-inf
    stats=[]

    if objrank=="None":
        objrank=""

    roles_id=list(map(lambda x:x["id"],guild_full["roles"]))
    if obj not in roles_id:
        obj,objrank=objrank,obj
    for i in members:
        if obj in i["roles"]:
            table=curseur.execute("SELECT * FROM {0}{1}{2} WHERE ID={3}".format(moisDB,anneeDB,objrank,i["user"]["id"])).fetchone()
            if table!=None:
                i["roles"].sort(key=lambda x:roles_position[x], reverse=True)
                if len(i["roles"])==0:
                    color=i
                else:
                    color="#{0}".format(hex(roles_color[i["roles"][0]])[2:])
                stats.append({"Count":table["Count"],"Rank":table["Rank"],"Nom":i["user"]["username"],"Color":color,"Avatar":i["user"]["avatar"],"ID":i["user"]["id"]})

                maxi=max(maxi,table["Count"])
    
    stats.sort(key=lambda x:x["Rank"])
    connexion.close()
    ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"option":option}
    return render(request, "companion/Ranks/iFrameRanks_ranks.html", ctx)
