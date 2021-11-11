from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from math import inf 
import requests
from ..outils import getMoisAnnee, getGuild, getUser, colorRoles, connectSQL, tableauMois

@login_required(login_url="/login")
def iFrameRoles(request,guild):
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