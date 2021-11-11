from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from math import inf 
import requests
from ..outils import getMoisAnnee, getGuild, getUser, colorRoles, connectSQL, tableauMois

@login_required(login_url="/login")
def iFrameArchive(request,guild):
    all=request.GET.get("data")
    jour,mois,annee=all.split("?")
    if annee!="GL":
        annee="20"+annee
    mois,annee,moisDB,anneeDB=getMoisAnnee(tableauMois[mois],annee)
    user=request.user

    guild_full=getGuild(guild)
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)
    
    connexion,curseur=connectSQL(guild,"Rapports","Stats","GL","")
    tabMois=curseur.execute("SELECT * FROM archives WHERE DateID={0}{1}{2} AND Type='Messages' AND Periode='Mois'".format(anneeDB,tableauMois[moisDB],jour)).fetchall()
    tabAnnee=curseur.execute("SELECT * FROM archives WHERE DateID={0}{1}{2} AND Type='Messages' AND Periode='Annee'".format(anneeDB,tableauMois[moisDB],jour)).fetchall()
    tabGlob=curseur.execute("SELECT * FROM archives WHERE DateID={0}{1}{2} AND Type='Messages' AND Periode='Global'".format(anneeDB,tableauMois[moisDB],jour)).fetchall()

    maxi=-inf
    dictUsers={}
    ctx={"id":user.id,"mois":mois,"annee":annee,"jour":jour}
    liste={"moisTab":tabMois,"anneeTab":tabAnnee,"globTab":tabGlob}

    for table in liste:
        stats=[]
        for i in liste[table]:
            if i["ID"] not in dictUsers:
                user_search=requests.get("https://discord.com/api/v9/guilds/{0}/members/{1}".format(guild,i["ID"]),headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})

                if user_search.status_code==200:
                    user_search=user_search.json()
                    user_search["roles"].sort(key=lambda x:roles_position[x], reverse=True)
                    if len(user_search["roles"])==0:
                        color=None
                    else:
                        color="#{0}".format(hex(roles_color[user_search["roles"][0]])[2:])
                    stats.append({"Count":i["Count"],"Rank":i["Rank"],"Nom":user_search["user"]["username"],"Color":color,"Avatar":user_search["user"]["avatar"],"ID":i["ID"]})
                    dictUsers[i["ID"]]=[color,user_search["user"]["username"],user_search["user"]["avatar"]]

                else:
                    stats.append({"Count":i["Count"],"Rank":i["Rank"],"Nom":"Ancien membre","Color":None})
            
            else:
                stats.append({"Count":i["Count"],"Rank":i["Rank"],"Nom":dictUsers[i["ID"]][1],"Color":dictUsers[i["ID"]][0],"Avatar":dictUsers[i["ID"]][2],"ID":i["ID"]})
            maxi=max(maxi,i["Count"])

        ctx[table]=stats.copy()
        ctx[table+"Maxi"]=maxi
    connexion.close()
    return render(request, "companion/archiveIFrame.html", ctx)