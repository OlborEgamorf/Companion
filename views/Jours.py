from math import inf

import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..outils import (avatarAnim, colorRoles, connectSQL, getGuild, getGuilds,
                      getMoisAnnee, getTableDay, getTimes, getUser, tableauMois)


@login_required(login_url="/login")
def viewJours(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]

    listeMois,listeAnnee=getTimes(guild,option)
    
    listeCateg=["Classements","Périodes","Évolution","Rôles","Jours","Rapports"]
    listeSections=["Accueil","Messages","Salons","Emotes","Vocal","Réactions","Mots","Fréquences"]
    dictRef={"Classements":"rank","Périodes":"periods","Évolution":"evol","Rôles":"roles","Jours":"jours","Rapport":"rapport"}

    maxi=-inf
    
    connexion,curseur=connectSQL(guild,"Messages","Stats","GL",None)

    table=getTableDay(curseur,tableauMois[moisDB],anneeDB)

    maxi=max(list(map(lambda x:x["Count"],table)))

    ctx={"rank":table,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,"nom":user_full["user"]["username"],"avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":getGuilds(user),"type":"Jours","categs":listeCateg,"hrefs":dictRef,"travel":True,"sections":listeSections,"section":"Messages","selector":True}
    return render(request,"companion/jours.html",ctx)


@login_required(login_url="/login")
def iFrameJour(request,guild,option):
    all=request.GET.get("data")
    jour,mois,annee=all.split("?")
    print(jour,mois,annee)
    user=request.user

    guild_full=getGuild(guild)
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)
    
    connexion,curseur=connectSQL(guild,"Rapports","Stats","GL",None)
    stats=[]
    maxi=-inf
    for i in curseur.execute("SELECT * FROM ranks WHERE Jour='{0}' AND Mois='{1}' AND Annee='{2}' AND Type='{3}' ORDER BY Rank ASC".format(jour,mois,annee,"Messages")).fetchall():

        user_search=requests.get("https://discord.com/api/v9/guilds/{0}/members/{1}".format(guild,i["ID"]),headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})

        if user_search.status_code==200:
            user_search=user_search.json()
            user_search["roles"].sort(key=lambda x:roles_position[x], reverse=True)
            if len(user_search["roles"])==0:
                color=None
            else:
                color="#{0}".format(hex(roles_color[user_search["roles"][0]])[2:])
            stats.append({"Count":i["Count"],"Rank":i["Rank"],"Nom":user_search["user"]["username"],"Color":color,"Avatar":user_search["user"]["avatar"],"ID":i["ID"]})
        else:
            stats.append({"Count":i["Count"],"Rank":i["Rank"],"Nom":"Ancien membre","Color":None})

        maxi=max(maxi,i["Count"])
    
    connexion.close()
    ctx={"rank":stats,"id":user.id,"max":maxi,"jour":jour, "mois":mois,"annee":annee}
    return render(request, "companion/rankIFrame.html", ctx)
