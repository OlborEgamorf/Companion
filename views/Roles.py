from math import inf

import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..outils import (avatarAnim, colorRoles, connectSQL, getGuild, getGuilds,
                      getMoisAnnee, getTableRoles, getTimes, getUser, rankingClassic, tableauMois)


@login_required(login_url="/login")
def viewRoles(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)

    listeMois,listeAnnee=getTimes(guild,option)

    listeCateg=["Classements","Périodes","Évolution","Rôles","Jours","Rapports"]
    listeSections=["Accueil","Messages","Salons","Emotes","Vocal","Réactions","Mots","Fréquences"]
    dictRef={"Classements":"rank","Périodes":"periods","Évolution":"evol","Rôles":"roles","Jours":"jours","Rapport":"rapport"}

    
    maxi=-inf
    connexion,curseur=connectSQL(guild,"Messages","Stats",tableauMois[moisDB],anneeDB)
    members=requests.get("https://discord.com/api/v9/guilds/{0}/members?limit=1000".format(guild),headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})
    if members.status_code==200:
        members=members.json()
    table=getTableRoles(curseur,members,moisDB+anneeDB)
    tableRoles=[]
    for i in table:
        tableRoles.append({"Rank":0,"Count":table[i],"Color":"#{0}".format(hex(roles_color[i])[2:]),"Name":roles_name[i],"ID":i})
    rankingClassic(tableRoles)

    maxi=max(list(map(lambda x:x["Count"],tableRoles)))
    connexion.close()
    ctx={"rank":tableRoles,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,"nom":user_full["user"]["username"],"avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":getGuilds(user),"type":"Rôles","categs":listeCateg,"hrefs":dictRef,"travel":True,"sections":listeSections,"section":"Messages","selector":True}
    return render(request,"companion/roles.html",ctx)
    

@login_required(login_url="/login")
def iFrameRoles(request,guild,option):
    all=request.GET.get("data")
    mois,annee,role=all.split("?")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    guild_full=getGuild(guild)
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)
    
    connexion,curseur=connectSQL(guild,"Messages","Stats",tableauMois[moisDB],anneeDB)

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
    ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"role":roles_name[role]}
    return render(request, "companion/rankIFrame.html", ctx)