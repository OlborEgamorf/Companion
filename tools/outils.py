import os
import sqlite3

import requests
from os.path import exists

listeSections=["Accueil","Messages","Salons","Emotes","Vocal","Réactions","Mots","Fréquences"]

tableauMois={"01":"Janvier","02":"Février","03":"Mars","04":"Avril","05":"Mai","06":"Juin","07":"Juillet","08":"Aout","09":"Septembre","10":"Octobre","11":"Novembre","12":"Décembre","TO":"TO","janvier":"01","février":"02","mars":"03","avril":"04","mai":"05","juin":"06","juillet":"07","aout":"08","septembre":"09","octobre":"10","novembre":"11","décembre":"12","glob":"GL","to":"TO","Total":"TO","total":"to"}

dictOptions={"messages":"Messages","voice":"Voice","salons":"Salons","voicechan":"Voicechan","emotes":"Emotes","reactions":"Reactions","mots":"Mots","freq":"Freq","p4":"P4","tortues":"Tortues","tortuesduo":"TortuesDuo","trivialversus":"TrivialVersus","trivialbr":"TrivialBR","trivialparty":"TrivialParty","morpion":"Morpion","matrice":"Matrice","divers":"Divers"}

listeCommands=["","ranks","periods","evol","first","jours","rapport"]
listeOptions=["messages","voice","emotes","salons","voicechan","freq","reactions","divers"]
listePlus=["","graphs","compare"]
dictRefCommands={"ranks":"Classements","periods":"Périodes","serv":"Serveur","perso":"Perso","evol":"Évolutions","first":"Premiers","roles":"Rôles","jours":"Jours","moy":"Moyennes","rapport":"Rapports","mondial":"Mondial","badges":"Badges","recap":"Récap","home":"Accueil"}
dictRefOptions={"home":"Accueil","messages":"Messages","voice":"Vocal","salons":"Salons","voicechan":"Salons vocaux","emotes":"Emotes","reactions":"Réactions","mots":"Mots","freq":"Fréquences","divers":"Divers","p4":"P4","tortues":"Tortues","tortuesduo":"TortuesDuo","trivialversus":"Trivial VS","trivialbr":"Trivial BR","trivialparty":"Trivial Party","morpion":"Morpion","matrice":"Matrice","":"Global"}
dictRefPlus={"":"Tableaux","graphs":"Graphiques","compare":"Comparateur","perso":"Pour vous","serv":"Pour le serveur","compareperso":"Comparateur personnel","obj":"Pour un objet","pantheon":"Panthéon"}

listeOptionsJeux=["p4","tortues","tortuesduo","trivialversus","trivialbr","trivialparty","morpion","matrice"]

dictDivers={3:"Images envoyées",2:"GIFs envoyés",1:"Fichiers envoyés",4:"Liens envoyés",5:"Réponses envoyés",6:"Réactions effectuées",7:"Messages édités",8:"Emotes envoyées",9:"Messages envoyés",10:"Mots écrits",11:"Temps passé en vocal","images":3,"gifs":2,"fichiers":1,"liens":4,"réponse":5,"réactions":6,"edits":7,"emotes":8,"messages":9,"mots":10,"vocal":11}

with open('os/SQL.txt') as f:
    root = f.read().strip()


def getTimes(guild,option,categ):
    connexion,curseur=connectSQL(guild,dictOptions[option],categ,"GL","")
    mois=curseur.execute("SELECT DISTINCT Mois FROM firstM ORDER BY Mois ASC").fetchall()
    annee=curseur.execute("SELECT DISTINCT Annee FROM firstM ORDER BY Annee ASC").fetchall()
    mois=list(map(lambda x:tableauMois[x["Mois"]],mois))+["Total"]
    annee=list(map(lambda x:"20{0}".format(x["Annee"]),annee))+["Global"]
    return mois,annee

def getTimesMix(guilds,option):
    allMois,allAnnee=[],[]
    for guild in guilds:
        connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")
        mois=curseur.execute("SELECT DISTINCT Mois FROM firstM ORDER BY Mois ASC").fetchall()
        annee=curseur.execute("SELECT DISTINCT Annee FROM firstM ORDER BY Annee ASC").fetchall()
        allMois+=mois
        allAnnee+=annee
    distMois,distAnnee=[],[]
    for i in allMois:
        if i not in distMois:
            distMois.append(i)
    for i in allAnnee:
        if i not in distAnnee:
            distAnnee.append(i)
    distMois.sort(key=lambda x:x["Mois"])
    distAnnee.sort(key=lambda x:x["Annee"])
    mois=list(map(lambda x:tableauMois[x["Mois"]],distMois))+["Total"]
    annee=list(map(lambda x:"20{0}".format(x["Annee"]),distAnnee))+["Global"]
    return mois,annee

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def connectSQL(guild,db,option,mois,annee):
    if option=="Guild":
        pathDir=root+"/SQL/{0}/Guild".format(guild)
        path=root+"/SQL/{0}/Guild/{1}.db".format(guild,db)
    elif db in ("Voice","Voicechan"):
        if mois in ("GL","glob") or annee in ("GL","glob"):
            pathDir=root+"/SQL/{0}/Voice/GL".format(guild)
            path=root+"/SQL/{0}/Voice/GL/{1}.db".format(guild,db)
        else:
            pathDir=root+"/SQL/{0}/Voice/{1}/{2}".format(guild,annee,mois.upper())
            path=root+"/SQL/{0}/Voice/{1}/{2}/{3}.db".format(guild,annee,mois.upper(),db)
    elif option=="Jeux":
        if mois in ("GL","glob") or annee in ("GL","glob"):
            pathDir=root+"/SQL/{0}/Jeux/GL".format(guild)
            path=root+"/SQL/{0}/Jeux/GL/{1}.db".format(guild,db)
        else:
            pathDir=root+"/SQL/{0}/Jeux/{1}/{2}".format(guild,annee,mois.upper())
            path=root+"/SQL/{0}/Jeux/{1}/{2}/{3}.db".format(guild,annee,mois.upper(),db)
    elif option in ("Trivial","Titres"):
        pathDir=root+"/SQL/OT/{0}".format(option)
        path=root+"/SQL/OT/{0}/{1}.db".format(option,db)
    elif mois in ("GL","glob") or annee in ("GL","glob"):
        pathDir=root+"/SQL/{0}/GL".format(guild)
        path=root+"/SQL/{0}/GL/{1}.db".format(guild,db)
    else:
        pathDir=root+"/SQL/{0}/{1}/{2}".format(guild,annee,mois.upper())
        path=root+"/SQL/{0}/{1}/{2}/{3}.db".format(guild,annee,mois.upper(),db)

    assert exists(path)
    if not os.path.exists(pathDir):
        os.makedirs(pathDir)
    connexion = sqlite3.connect(path)

    connexion.row_factory = dict_factory
    curseur = connexion.cursor()
    return connexion,curseur

def getMoisAnnee(mois,annee):
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

def getMoisAnneePerso(mois,annee):
    if mois==None or annee==None:
        mois,annee="Total","Global"
    if annee in ("Global","GL"):
        mois="Total"
        moisDB,anneeDB="TO","GL"
    elif mois in ("Total","TO"):
        moisDB,anneeDB="TO",annee[2:4]
    else:
        moisDB,anneeDB=tableauMois[mois.lower()],annee[2:4]
    return mois,annee,moisDB,anneeDB


def getGuild(guild):
    guild_full=requests.get("https://discord.com/api/v9/guilds/{0}".format(guild),headers={"Authorization":"Bot //TOKEN//"})
    assert guild_full.status_code==200
    guild_full=guild_full.json()
    return guild_full


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
    table.sort(key=lambda x:x["Annee"]+x["Mois"]+x["Jour"])
    temp=(table[0]["Mois"],table[0]["Annee"])
    if len(table)>31:
        table[0]["Collapse"]=False
        table[-1]["Collapse"]=False
        for i in range(1,len(table)-1):
            if table[i]["Evol"]!=0 or temp!=(table[i]["Mois"],table[i]["Annee"]):
                table[i]["Collapse"]=False
                temp=(table[i]["Mois"],table[i]["Annee"])
            else:
                table[i]["Collapse"]=True
    else:
        for i in table:
            i["Collapse"]=False
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

def getTableRolesMem(curseur,members,id,mois,annee) -> list:
    """Permet d'obtenir le classement des membres ayant un certain rôles pour une table donnée
    Entrées :
        curseur : curseur pour accéder à la base de données
        guild : le serveur d'où vient la commande
        id : l'ID du rôle
        nom : le nom de la table
        tri : comment la liste doit être triée 
    Sortie :
        newTable : le classement des membres ayant le rôle"""
    table={}
    for i in members:
        if id in i["roles"]:
            stats=curseur.execute("SELECT * FROM perso{0}{1}{2}".format(mois,annee,i["user"]["id"])).fetchall()
            for j in stats:
                if j["ID"] not in table:
                    table[j["ID"]]=0
                table[j["ID"]]+=j["Count"]
    return table
        
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


def getTablePerso(guild,option,id,idobj,period,tri):
    if option in ("Tortues","TortuesDuo","P4","Matrice","Morpion","TrivialVersus","TrivialBR","TrivialParty"):
        categ="Jeux"
    else:
        categ="Stats"
    liste=[]
    connectionF,curseurF=connectSQL(guild,option,categ,"GL","")
    for i in curseurF.execute("SELECT Mois,Annee FROM first{0}".format(period)).fetchall():
        try:
            connection,curseur=connectSQL(guild,option,categ,i["Mois"],i["Annee"])
            if categ=="Jeux" and id!=guild:
                stat=curseur.execute("SELECT Rank,Count,Mois,Annee,ID,W,L FROM {0}{1} WHERE ID={2}".format(tableauMois[i["Mois"]],i["Annee"],id)).fetchone()
            elif id==guild:
                stat=curseur.execute("SELECT Mois,Annee,SUM(Count) AS Count FROM {0}{1}".format(tableauMois[i["Mois"]],i["Annee"])).fetchone()
            elif not idobj:
                stat=curseur.execute("SELECT Rank,Count,Mois,Annee,ID FROM {0}{1} WHERE ID={2}".format(tableauMois[i["Mois"]],i["Annee"],id)).fetchone()
            else:
                stat=curseur.execute("SELECT Rank,Count,Mois,Annee,ID FROM perso{0}{1}{2} WHERE ID={3}".format(i["Mois"],i["Annee"],id,idobj)).fetchone()
            if stat!=None:
                liste.append(stat)
        except:
            pass
    if tri=="countDesc":
        liste.sort(key=lambda x:x["Count"],reverse=True)
    elif tri=="periodAsc":
        liste.sort(key=lambda x:x["Annee"]+x["Mois"])
    elif tri=="periodDesc":
        liste.sort(key=lambda x:x["Annee"]+x["Mois"],reverse=True)
    elif tri=="rankAsc":
        liste.sort(key=lambda x:x["Rank"])
    return liste


def getGuilds(user,curseurGet):
    bot_guilds=curseurGet.execute("SELECT ID FROM guilds").fetchall()
    bot_ids=list(map(lambda x:x["ID"], bot_guilds))
    user_guild=requests.get("https://discord.com/api/v9/users/@me/guilds",headers={"Authorization":"Bearer {0}".format(user.token)})
    uguild_json=user_guild.json()

    common=list(filter(lambda x: int(x["id"]) in bot_ids, uguild_json))
    final_guilds=[]

    for guild in common:
        final_guilds.append({"ID":int(guild["id"]),"Nom":guild["name"],"Icon":guild["icon"]})

    final_guilds.sort(key=lambda x:x["Nom"])
    return final_guilds

def createPhrase(args:list) -> str:
    """Formate une liste de str pour en faire une phrase sans ' , pour que l'insertion dans les bases de données se fasse sans casse.
    Entrée : 
        args : liste de mots qui forme une phrase
    Sortie :
        descip : la phrase reconstituée"""
    descip=""
    for i in args:
        mot=""
        for lettre in i:
            if lettre=="'":
                mot+="’"
            else:
                mot+=lettre
        descip+=mot+" "
    return descip


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


def getCommon(guilds_me,user,curseurGet):
    listeCom=[]
    for i in guilds_me:
        if curseurGet.execute("SELECT * FROM users_{0} WHERE ID={1}".format(i["ID"],user)).fetchone()!=None:
            guild=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(i["ID"])).fetchone()
            listeCom.append({"ID":i["ID"],"Icon":guild["Icon"],"Nom":guild["Nom"]})
    return listeCom

def voiceAxe(option:str,listeCount:list) -> int:
    if option in ("voice","voicechan"):
        maxi=max(listeCount)
        if maxi<60:
            mesure=" (en secondes)"
            div=1
        elif maxi<3600:
            mesure=" (en minutes)"
            div=60
        elif maxi<86400:
            mesure=" (en heures)"
            div=3600
        else:
            mesure=" (en jours)"
            div=86400
        for i in range(len(listeCount)):
            listeCount[i]=round(listeCount[i]/div,2)
        return mesure,div
    return "",1

def createPhrase(text:(str or list)) -> str:
    """Formate une liste de str pour en faire une phrase sans ' , pour que l'insertion dans les bases de données se fasse sans casse.
    Entrée : 
        args : liste de mots qui forme une phrase
    Sortie :
        descip : la phrase reconstituée"""
    if type(text) in (list, tuple):
        text=" ".join(text)
    return text.replace("'","’")

