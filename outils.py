import sqlite3
import os
import requests

listeMois=["Total","Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Aout","Septembre","Octobre","Novembre","Décembre"]
listeAnnee=["Global","2015","2016","2017","2018","2019","2020","2021"]

tableauMois={"01":"Janvier","02":"Février","03":"Mars","04":"Avril","05":"Mai","06":"Juin","07":"Juillet","08":"Aout","09":"Septembre","10":"Octobre","11":"Novembre","12":"Décembre","TO":"TO","janvier":"01","février":"02","mars":"03","avril":"04","mai":"05","juin":"06","juillet":"07","aout":"08","septembre":"09","octobre":"10","novembre":"11","décembre":"12","glob":"GL","to":"TO","Total":"TO"}

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
        pathDir="E:/IFNO/OlborTrack/SQL/{0}/GL".format(guild)
        path="E:/IFNO/OlborTrack/SQL/{0}/GL/{1}.db".format(guild,db)
    else:
        pathDir="E:/IFNO/OlborTrack/SQL/{0}/{1}/{2}".format(guild,annee,mois.upper())
        path="E:/IFNO/OlborTrack/SQL/{0}/{1}/{2}/{3}.db".format(guild,annee,mois.upper(),db)

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
    if mois.lower() in ("glob","gl"):
        return curseur.execute("SELECT *, Annee || '' || Mois || '' || Jour AS DateID FROM dayRank ORDER BY Count DESC").fetchall()
    elif mois.lower()=="to":
        return curseur.execute("SELECT *, Annee || '' || Mois || '' || Jour AS DateID FROM dayRank WHERE Annee='{0}' ORDER BY Count DESC".format(annee)).fetchall()
    else:
        return curseur.execute("SELECT *, Annee || '' || Mois || '' || Jour AS DateID FROM dayRank WHERE Mois='{0}' AND Annee='{1}' ORDER BY Count DESC".format(mois,annee,)).fetchall()