import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..outils import avatarAnim, collapseEvol, getMoisAnnee, getGuild, getTableDay, getTableRoles, getTimes, getUser, colorRoles, connectSQL, rankingClassic, tableauMois
from math import inf
import plotly.graph_objects as go
from plotly.offline import plot
import plotly.express as px

@login_required(login_url="/login")
def guildGraph(request,guild,section):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    user_avatar=user_full["user"]["avatar"]
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)

    listeMois,listeAnnee=getTimes(guild,None)

    if section=="rank":
        old=1
        colors=[]
        counts=[]
        ranks=[]
        names=[]
        connexion,curseur=connectSQL(guild,"Messages","Stats",tableauMois[moisDB],anneeDB)
        flag=False

        for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC".format(moisDB,anneeDB)).fetchall():
            if i["ID"]==user.id:
                flag=True

            user_search=requests.get("https://discord.com/api/v9/guilds/{0}/members/{1}".format(guild,i["ID"]),headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})

            if user_search.status_code==200:
                user_search=user_search.json()
                user_search["roles"].sort(key=lambda x:roles_position[x], reverse=True)
                if len(user_search["roles"])==0:
                    colors.append("rgb(110,200,250)")
                else:
                    if roles_color[user_search["roles"][0]]!=0: 
                        r,g,b=tuple(int(hex(roles_color[user_search["roles"][0]])[2:][i:i+2], base=16) for i in (0, 2, 4))
                        colors.append("rgb({0},{1},{2})".format(r,g,b))
                    else:
                        colors.append("rgb(110,200,250)")
                if len(user_search["user"]["username"])<15:
                    names.append(user_search["user"]["username"])
                else:
                    names.append(user_search["user"]["username"][0:15]+"...")
            else:
                names.append("Anciens membres".format(old))
                colors.append("rgb(110,200,250)")
                old+=1
            counts.append(i["Count"])
            ranks.append(i["Rank"])

        if not flag:
            solo=curseur.execute("SELECT * FROM {0}{1} WHERE ID={2}".format(moisDB,anneeDB,user.id)).fetchone()
            if solo!=None:
                counts.append(i["Count"])
                ranks.append(i["Rank"])
                names.append(user_full["user"]["username"])
                r,g,b=tuple(int(roles_color[user_full["roles"][0]][i:i+2], 16) for i in (1, 3, 5))
                colors.append("rgb({0},{1},{2})".format(r,g,b))
        
        
        fig=go.Figure(data=go.Bar(x=names,y=counts,marker_color=colors,text=counts,textposition="auto"))
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="rgb(47,64,120)",
            font_family="Roboto",
            font_color="white",
            xaxis={'categoryorder':'total descending',"rangeslider":{"visible":True}},
        )
        fig.update_yaxes(automargin=True)
        div=plot(fig,output_type='div')

        if len(names)>10:
            names=names[0:10]+["Autres membres"]
            counts=counts[0:10]+[sum(counts[10:])]
            colors=colors[0:10]+["rgb(110,200,250)"]

        fig3=go.Figure(data=go.Pie(labels=names,values=counts))
        fig3.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="rgb(47,64,120)",
            font_family="Roboto",
            font_color="white"
        )
        fig3.update_traces(marker_colors=colors)
        fig3.update_yaxes(automargin=True)
        div3=plot(fig3,output_type='div')
        
        membres=["@everyone"]
        roles=[""]
        ids=["@everyone"]
        count=[curseur.execute("SELECT SUM(Count) AS Total FROM {0}{1}".format(moisDB,anneeDB)).fetchone()["Total"]]
        colors=["white"]
        members=requests.get("https://discord.com/api/v9/guilds/{0}/members?limit=1000".format(guild),headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})
        if members.status_code==200:
            members=members.json()
        table=getTableRoles(curseur,members,moisDB+anneeDB)
        for i in table:
            membres.append(roles_name[i])
            roles.append("@everyone")
            count.append(table[i])
            ids.append(roles_name[i])
            if roles_color[i]!=0:
                try:
                    r,g,b=tuple(int(hex(roles_color[i])[2:][j:j+2], base=16) for j in (0, 2, 4))
                    colors.append("rgb({0},{1},{2})".format(r,g,b))
                except:
                    colors.append("rgb(110,200,250)")
            else:
                colors.append("rgb(110,200,250)")
        for i in members:
            num=0
            mess=curseur.execute("SELECT * FROM {0}{1} WHERE ID={2}".format(moisDB,anneeDB,i["user"]["id"])).fetchone()
            if mess!=None:
                for j in i["roles"]:
                    ids.append(i["user"]["username"]+str(num))
                    membres.append(i["user"]["username"])
                    roles.append(roles_name[j])
                    count.append(mess["Count"])
                    num+=1
                    if roles_color[j]!=0:
                        try:
                            r,g,b=tuple(int(hex(roles_color[j])[2:][h:h+2], base=16) for h in (0, 2, 4))
                            colors.append("rgb({0},{1},{2})".format(r,g,b))
                        except:
                            colors.append("rgb(110,200,250)")
                    else:
                        colors.append("rgb(110,200,250)")

        data = dict(membres=membres,roles=roles,count=count)
        fig2 =go.Figure(go.Sunburst(
            labels=membres, parents=roles, values=count, ids=ids, marker_colors=colors
        ))
        fig2.update_yaxes(automargin=True)
        fig2.update_layout(
            margin=dict(l=5, r=5, t=5, b=5),
            paper_bgcolor="rgb(47,64,120)",
            font_family="Roboto",
        )
        div2=plot(fig2,output_type='div')

        connexion.close()
        ctx={"fig":div,"fig2":div2,"fig3":div3,"avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,"guilds":getGuilds(user)}
        return render(request, "companion/graph.html", ctx)

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
            tableRoles.append({"Rank":0,"Count":table[i],"Color":"#{0}".format(hex(roles_color[i])[2:]),"Name":roles_name[i],"ID":i})
        rankingClassic(tableRoles)

        maxi=max(list(map(lambda x:x["Count"],tableRoles)))
        connexion.close()
        ctx={"rank":tableRoles,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,"nom":user_full["user"]["username"],"avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"]}
        return render(request,"companion/roles.html",ctx)
    
    elif section=="jours":
        connexion,curseur=connectSQL(guild,"Messages","Stats","GL",None)
        table=getTableDay(curseur,tableauMois[moisDB],anneeDB)
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
        final_guilds.append({"ID":int(guild["id"]),"Nom":guild["name"],"Icon":guild["icon"],"Anim":end})

    final_guilds.sort(key=lambda x:x["Nom"])
    return final_guilds