import os
import sqlite3
from math import inf
from typing import final

import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from discord_login.views import refresh

listeMois=["Total","Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Aout","Septembre","Octobre","Novembre","Décembre"]
listeAnnee=["Global","2015","2016","2017","2018","2019","2020","2021"]

tableauMois={"01":"Janvier","02":"Février","03":"Mars","04":"Avril","05":"Mai","06":"Juin","07":"Juillet","08":"Aout","09":"Septembre","10":"Octobre","11":"Novembre","12":"Décembre","TO":"TO","janvier":"01","février":"02","mars":"03","avril":"04","mai":"05","juin":"06","juillet":"07","aout":"08","septembre":"09","octobre":"10","novembre":"11","décembre":"12","glob":"GL","to":"TO","Total":"TO"}

@login_required(login_url="/login")
def home(request):
    user=request.user

    bot_guilds=requests.get("https://discord.com/api/v9/users/@me/guilds",headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})
    bguild_json=bot_guilds.json()
    bot_ids=list(map(lambda x:x["id"], bguild_json))

    user_avatar=requests.get("https://discord.com/api/v9/users/@me",headers={"Authorization":"Bearer {0}".format(user.token)})
    if user_avatar.status_code==401:
        request.user.token=refresh(user.token)
        return home(request)
    user_avatar=user_avatar.json()
    
    user_avatar=user_avatar["avatar"]

    user_guild=requests.get("https://discord.com/api/v9/users/@me/guilds",headers={"Authorization":"Bearer {0}".format(user.token)})
    uguild_json=user_guild.json()

    common=list(filter(lambda x: x["id"] in bot_ids, uguild_json))
    final_guilds=[]

    for guild in common:
        if guild["icon"]!=None:
            end=avatarAnim(guild["icon"][0:2])
        final_guilds.append({"ID":guild["id"],"Nom":guild["name"],"Icon":guild["icon"],"Anim":end})

    final_guilds.sort(key=lambda x:x["Nom"])
    
    ctx={"guilds":final_guilds,"avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar)}
    return render(request, "companion/home.html", ctx)


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
        ctx={"rank":stats,"avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"max":maxi,"guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee}
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
        return render(request,"companion/evol.html",ctx)


def iFrameBlank(request):
    return render(request,"companion/blank.html")

@login_required(login_url="/login")
def iFrameEvol(request,guild):
    all=request.GET.get("data")
    mois,annee,id=all.split("?")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user
    if id==None:
        id=user.id

    guild_full=getGuild(guild)

    user_full=getUser(guild,id)
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)
    
    connexion,curseur=connectSQL(guild,"Messages","Stats",tableauMois[moisDB],anneeDB)

    table=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,id)).fetchall()
    table=collapseEvol(table)


    user_full["roles"].sort(key=lambda x:roles_position[x], reverse=True)
    if len(user_full["roles"])==0:
        color=None
    else:
        color="#{0}".format(hex(roles_color[user_full["roles"][0]])[2:])

    maxi=max(list(map(lambda x:x["Count"],table)))

    ctx={"rank":table,"id":user.id,"color":color,"max":maxi,"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,"nom":user_full["user"]["username"]}
    connexion.close()
    return render(request,"companion/evolIFrame.html",ctx)

@login_required(login_url="/login")
def iFrameRank(request,guild):
    all=request.GET.get("data")
    mois,annee=all.split("?")
    print(mois,annee)
    if annee!="GL":
        annee="20"+annee
    mois,annee,moisDB,anneeDB=getMoisAnnee(tableauMois[mois],annee)
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)
    
    connexion,curseur=connectSQL(guild,"Messages","Stats",tableauMois[moisDB],anneeDB)
    rank=curseur.execute("SELECT Rank FROM {0}{1} WHERE ID={2}".format(moisDB,anneeDB,user.id)).fetchone()["Rank"]

    rankPlus=rank-10
    rankMoins=rank+10

    if rankPlus<0:
        rankMoins-=rankPlus

    maxi=-inf
    stats=[]

    for i in curseur.execute("SELECT * FROM {0}{1} WHERE (Rank>={2} AND Rank<={3}) OR Rank=1 ORDER BY Rank ASC".format(moisDB,anneeDB,rankPlus,rankMoins)).fetchall():

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
    ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee}
    return render(request, "companion/rankIFrame.html", ctx)


@login_required(login_url="/login")
def iFrameArchive(request,guild):
    all=request.GET.get("data")
    jour,mois,annee=all.split("?")
    if annee!="GL":
        annee="20"+annee
    mois,annee,moisDB,anneeDB=getMoisAnnee(tableauMois[mois],annee)
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    
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
    

@login_required(login_url="/login")
def iFrameRoles(request,guild):
    all=request.GET.get("data")
    mois,annee,role=all.split("?")
    print(mois,annee,role)
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    print(moisDB,anneeDB)
    user=request.user

    guild_full=getGuild(guild)

    user_full=getUser(guild,user.id)
    
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
    ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee}
    return render(request, "companion/rankIFrame.html", ctx)
    


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def connectSQL(guild,db,option,mois,annee):
    if option=="Guild":
        pathDir="SQL/{0}/Guild".format(guild)
        path="SQL/{0}/Guild/{1}.db".format(guild,db)
    elif db in ("Voice","Voicechan"):
        if mois in ("GL","glob") or annee in ("GL","glob"):
            pathDir="SQL/{0}/Voice/GL".format(guild)
            path="SQL/{0}/Voice/GL/{1}.db".format(guild,db)
        else:
            pathDir="SQL/{0}/Voice/{1}/{2}".format(guild,annee,mois.upper())
            path="SQL/{0}/Voice/{1}/{2}/{3}.db".format(guild,annee,mois.upper(),db)
    elif option=="Jeux":
        if mois in ("GL","glob") or annee in ("GL","glob"):
            pathDir="SQL/{0}/Jeux/GL".format(guild)
            path="SQL/{0}/Jeux/GL/{1}.db".format(guild,db)
        else:
            pathDir="SQL/{0}/Jeux/{1}/{2}".format(guild,annee,mois.upper())
            path="SQL/{0}/Jeux/{1}/{2}/{3}.db".format(guild,annee,mois.upper(),db)
    elif option in ("Trivial","Titres"):
        pathDir="SQL/OT/{0}".format(option)
        path="SQL/OT/{0}/{1}.db".format(option,db)
    elif mois in ("GL","glob") or annee in ("GL","glob"):
        pathDir="G:/IFNO/OlborTrack/SQL/{0}/GL".format(guild)
        path="G:/IFNO/OlborTrack/SQL/{0}/GL/{1}.db".format(guild,db)
    else:
        pathDir="G:/IFNO/OlborTrack/SQL/{0}/{1}/{2}".format(guild,annee,mois.upper())
        path="G:/IFNO/OlborTrack/SQL/{0}/{1}/{2}/{3}.db".format(guild,annee,mois.upper(),db)

    if not os.path.exists(pathDir):
        os.makedirs(pathDir)
    connexion = sqlite3.connect(path)

    connexion.row_factory = dict_factory
    curseur = connexion.cursor()
    return connexion,curseur


def avatarAnim(user_avatar):
    if user_avatar[0:2]=="a_":
        return "gif"
    else:
        return "png"


def getMoisAnnee(mois,annee):
    print(mois,annee)
    if mois==None or annee==None:
        mois,annee="Total","Global"
    if annee in ("Global","GL"):
        mois="Total"
        moisDB,anneeDB="glob",""
    elif mois in ("Total","TO"):
        moisDB,anneeDB="to",annee[2:4]
    else:
        moisDB,anneeDB=mois.lower(),annee[2:4]
    return mois,annee,moisDB,anneeDB


def getGuild(guild):
    guild_full=requests.get("https://discord.com/api/v9/guilds/{0}".format(guild),headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})
    assert guild_full.status_code==200
    guild_full=guild_full.json()
    return guild_full


def getUser(guild,id):
    user_full=requests.get("https://discord.com/api/v9/guilds/{0}/members/{1}".format(guild,id),headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})
    assert user_full.status_code==200
    user_full=user_full.json()
    return user_full


def colorRoles(guild_full):
    roles_position={}
    roles_color={}
    roles_name={}
    for i in guild_full["roles"]:
        roles_position[i["id"]]=i["position"]
        roles_color[i["id"]]=i["color"]
        roles_name[i["id"]]=i["name"]
    return roles_position, roles_color, roles_name


def collapseEvol(table:list) -> list:
    """Permet d'écraser une table évol pour ne faire ressortir que les dates importantes si la table est trop grande : changement de rang et changement de mois
    Entrée : 
        table : la table évol à écraser
    Sortie :
        table si len(table)<=31, sinon newTable, la table écrasée"""
    newTable=[table[0]]
    temp=(table[0]["Mois"],table[0]["Annee"])
    if len(table)>31:
        for i in range(1,len(table)-1):
            if table[i]["Evol"]!=0 or temp!=(table[i]["Mois"],table[i]["Annee"]):
                newTable.append(table[i])
                temp=(table[i]["Mois"],table[i]["Annee"])
        newTable.append(table[i+1])
        return newTable
    return table

def getTableRoles(curseur,members,nom) -> list:
    """Permet d'obtenir le classement des rôles pour une table donnée
    Entrées :
        curseur : curseur pour accéder à la base de données
        guild : le serveur d'où vient la commande
        nom : le nom de la table
        tri : comment la liste doit être triée 
    Sortie :
        tableRole : le classement des rôles"""
    tableRole=[]
    dictRoles={}
    for i in members:
        count=curseur.execute("SELECT * FROM {0} WHERE ID={1}".format(nom,i["user"]["id"])).fetchone()
        if count!=None:
            for j in i["roles"]:
                if j not in dictRoles:
                    dictRoles[j]=0
                dictRoles[j]+=count["Count"]
    return dictRoles
        
def rankingClassic(table:list):
    """Cette fonction effectue un classement de type 'classique' d'une table donnée.
    Entrée :
        table : la liste de dictionnaires formant la table à classer"""
    table.sort(key=lambda x:x["Count"],reverse=True)
    countTemp=0
    rankTemp=0
    for i in range(len(table)):
        if table[i]["Count"]==countTemp:
            table[i]["Rank"]=rankTemp
        else:
            countTemp=table[i]["Count"]
            rankTemp=i+1
            table[i]["Rank"]=rankTemp

def getTableDay(curseur:sqlite3.Cursor,mois:str,annee:str) -> list:
    """Permet d'extraire une liste des jours d'activité selon les critères de période que l'on veut.
    Entrées : 
        curseur : curseur pour accéder à la base de données
        mois : mois de la période voulue
        annee : année de la période voulue
        tri : comment la liste doit être triée
    Sortie :
        la liste qui répond à nos critères, renvoyée par la requête SQL"""
    print(mois,annee)
    if mois.lower()=="glob":
        return curseur.execute("SELECT *, Annee || '' || Mois || '' || Jour AS DateID FROM dayRank ORDER BY Count DESC").fetchall()
    elif mois.lower()=="to":
        return curseur.execute("SELECT *, Annee || '' || Mois || '' || Jour AS DateID FROM dayRank WHERE Annee='{0}' ORDER BY Count DESC".format(annee)).fetchall()
    else:
        return curseur.execute("SELECT *, Annee || '' || Mois || '' || Jour AS DateID FROM dayRank WHERE Mois='{0}' AND Annee='{1}' ORDER BY Count DESC".format(mois,annee,)).fetchall()