import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..outils import avatarAnim, collapseEvol, getMoisAnnee, getGuild, getTableDay, getTableRoles, getUser, colorRoles, connectSQL, rankingClassic, tableauMois, listeAnnee, listeMois
from math import inf

@login_required(login_url="/login")
def guildMessages(request,guild,section):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)

    
    maxi=-inf
    if section=="rank":
        stats=[]
        connexion,curseur=connectSQL(guild,"Messages","Stats",tableauMois[moisDB],anneeDB)
        flag=False

        for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT 20".format(moisDB,anneeDB)).fetchall():
            if i["ID"]==user.id:
                flag=True

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

        if not flag:
            solo=curseur.execute("SELECT * FROM {0}{1} WHERE ID={2}".format(moisDB,anneeDB,user.id)).fetchone()
            if solo!=None:
                stats.append({"Count":i["Count"],"Rank":i["Rank"],"Nom":user_search["user"]["username"],"Color":color,"Avatar":user_search["user"]["avatar"],"ID":i["ID"]})
        
        connexion.close()
        ctx={"rank":stats,"avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"max":maxi,"guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,"guilds":getGuilds(user)}
        return render(request, "companion/ranks.html", ctx)

    elif section=="periods":
        connexion,curseur=connectSQL(guild,"Messages","Stats","GL","")

        user_full["roles"].sort(key=lambda x:roles_position[x], reverse=True)
        if len(user_full["roles"])==0:
            color=None
        else:
            color="#{0}".format(hex(roles_color[user_full["roles"][0]])[2:])

        statsMois=curseur.execute("SELECT * FROM persoM{0} ORDER BY Count DESC".format(user.id)).fetchall()
        statsAnnee=curseur.execute("SELECT * FROM persoA{0} ORDER BY Count DESC".format(user.id)).fetchall()

        maxiM=max(list(map(lambda x:x["Count"],statsMois)))
        maxiA=max(list(map(lambda x:x["Count"],statsAnnee)))
        
        connexion.close()
        ctx={"rankMois":statsMois,"rankAnnee":statsAnnee,"avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"maxM":maxiM,"maxA":maxiA,"guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"color":color}
        return render(request, "companion/periods.html", ctx)

    elif section=="evol":
        connexion,curseur=connectSQL(guild,"Messages","Stats",tableauMois[moisDB],anneeDB)
        table=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,user.id)).fetchall()
        table=collapseEvol(table)


        user_full["roles"].sort(key=lambda x:roles_position[x], reverse=True)
        if len(user_full["roles"])==0:
            color=None
        else:
            color="#{0}".format(hex(roles_color[user_full["roles"][0]])[2:])

        maxi=max(list(map(lambda x:x["Count"],table)))

        ctx={"rank":table,"id":user.id,"color":color,"max":maxi,"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,"nom":user_full["user"]["username"],"avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"]}
        connexion.close()
        return render(request,"companion/evol.html",ctx)

    elif section=="roles":
        connexion,curseur=connectSQL(guild,"Messages","Stats",tableauMois[moisDB],anneeDB)
        members=requests.get("https://discord.com/api/v9/guilds/{0}/members?limit=1000".format(guild),headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})
        if members.status_code==200:
            members=members.json()
        table=getTableRoles(curseur,members,moisDB+anneeDB)
        tableRoles=[]
        for i in table:
            print(roles_color[i])
            tableRoles.append({"Rank":0,"Count":table[i],"Color":"#{0}".format(hex(roles_color[i])[2:]),"Name":roles_name[i],"ID":i})
        rankingClassic(tableRoles)

        maxi=max(list(map(lambda x:x["Count"],tableRoles)))
        connexion.close()
        ctx={"rank":tableRoles,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,"nom":user_full["user"]["username"],"avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"]}
        return render(request,"companion/roles.html",ctx)
    
    elif section=="jours":
        connexion,curseur=connectSQL(guild,"Messages","Stats","GL",None)
        table=getTableDay(curseur,tableauMois[moisDB],anneeDB)
        print(table)
        maxi=max(list(map(lambda x:x["Count"],table)))
        ctx={"rank":table,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,"nom":user_full["user"]["username"],"avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"]}
        return render(request,"companion/jours.html",ctx)


def getGuilds(user):
    bot_guilds=requests.get("https://discord.com/api/v9/users/@me/guilds",headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})
    bguild_json=bot_guilds.json()
    bot_ids=list(map(lambda x:x["id"], bguild_json))
    user_guild=requests.get("https://discord.com/api/v9/users/@me/guilds",headers={"Authorization":"Bearer {0}".format(user.token)})
    uguild_json=user_guild.json()

    common=list(filter(lambda x: x["id"] in bot_ids, uguild_json))
    final_guilds=[]

    for guild in common:
        if guild["icon"]!=None:
            end=avatarAnim(guild["icon"][0:2])
        final_guilds.append({"ID":guild["id"],"Nom":guild["name"],"Icon":guild["icon"],"Anim":end})

    final_guilds.sort(key=lambda x:x["Nom"])
    return final_guilds