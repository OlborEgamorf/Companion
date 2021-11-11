from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from math import inf 
import requests
from ..outils import getMoisAnnee, getGuild, getUser, colorRoles, connectSQL, tableauMois

@login_required(login_url="/login")
def iFrameJour(request,guild):
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