import requests

from companion.outils import connectSQL,dictOptions


def getUserTable(i,curseurGet,guild):
    infos=curseurGet.execute("SELECT * FROM users JOIN users_{0} ON users.ID = users_{0}.ID WHERE users.ID={1}".format(guild,i["ID"])).fetchone()
    if infos==None:
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":"Ancien membre","Color":None,"Avatar":None,"ID":i["ID"]}
    else:
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":infos["Nom"],"Color":"#"+hex(infos["Color"])[2:],"Avatar":infos["Avatar"],"ID":i["ID"]}

def getEmoteTable(i,curseurGet):
    infos=curseurGet.execute("SELECT * FROM emotes WHERE ID={0}".format(i["ID"])).fetchone()
    if infos==None:
        try:
            chr(i["ID"])
            return {"Count":i["Count"],"Rank":i["Rank"],"Nom":"twemoji","ID":i["ID"]} 
        except:
            return {"Count":i["Count"],"Rank":i["Rank"],"Nom":"Emote inconnue","ID":i["ID"]}
    else:
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":infos["Nom"],"ID":i["ID"]}


def getChannels(i,curseurGet):
    infos=curseurGet.execute("SELECT * FROM salons WHERE ID={0}".format(i["ID"])).fetchone()
    if infos!=None:
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":infos["Nom"],"ID":i["ID"]}
    else:
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":"Salon inconnu","ID":i["ID"]}


def getFreq(i):
    return {"Count":i["Count"],"Rank":i["Rank"],"Nom":"{0}h-{1}h".format(i["ID"],i["ID"]+1),"ID":i["ID"]}


def getColor(id,guild,curseurGet):
    infos=curseurGet.execute("SELECT * FROM users_{0} WHERE ID={1}".format(guild,id)).fetchone()
    if infos!=None:
        return "#"+hex(infos["Color"])[2:]
    return None

def getGuildInfo(id,curseurGet):
    return curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(id)).fetchone()

def getUserInfo(id,curseurGet,guild):
    return curseurGet.execute("SELECT * FROM users JOIN users_{0} ON users.ID = users_{0}.ID WHERE users.ID={1}".format(guild,id)).fetchone()

def getNom(id,option,curseurGet,obj):
    if option in ("messages","voice","mots") or obj:
        infos=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(id)).fetchone()
    elif option in ("emotes","reactions"):
        infos=curseurGet.execute("SELECT * FROM emotes WHERE ID={0}".format(id)).fetchone()
    elif option in ("salons","voicechan"):
        infos=curseurGet.execute("SELECT * FROM salons WHERE ID={0}".format(id)).fetchone()
    elif option=="freq":
        infos={"Nom":"{0}h-{1}h".format(id,id+1)}
    if infos!=None:
        return infos["Nom"]
    return "Inconnu"

def getUserJeux(i,curseurGet,jeu):
    connexionUser,curseurUser=connectSQL("OT",i["ID"],"Titres",None,None)
    infos=getAllInfos(curseurGet,curseurUser,connexionUser,i["ID"])
    badgeJeu=curseurUser.execute("SELECT * FROM badges WHERE Type='{0}' ORDER BY Valeur DESC".format(dictOptions[jeu])).fetchone()
    if badgeJeu!=None:
        badgeJeu=badgeJeu["Valeur"]
    return {"Count":i["Count"],"Rank":i["Rank"],"Nom":infos["Full"],"Color":infos["Couleur"],"Emote":infos["Emote"],"ID":i["ID"],"VIP":infos["VIP"],"Testeur":infos["Testeur"],"BadgeJeu":badgeJeu}

def createAccount(connexion,curseur):
    curseur.execute("CREATE TABLE IF NOT EXISTS titresUser (ID INT, Nom TEXT, Rareté INT, PRIMARY KEY(ID))")
    curseur.execute("CREATE TABLE IF NOT EXISTS coins (Coins INT)")
    curseur.execute("CREATE TABLE IF NOT EXISTS badges (Type TEXT, Période TEXT, Rang INT, Valeur INT, PRIMARY KEY(Type,Période,Rang))")
    if curseur.execute("SELECT * FROM coins").fetchone()==None:
        curseur.execute("INSERT INTO coins VALUES(0)")
    connexion.commit()
def getAllInfos(curseur,curseurUser,connexionUser,user):
    try:
        coins=curseurUser.execute("SELECT * FROM coins").fetchone()["Coins"]
    except:
        createAccount(connexionUser,curseurUser)
        coins=0
    titre=curseur.execute("SELECT titres.Nom FROM active JOIN titres ON active.TitreID=titres.ID WHERE MembreID={0}".format(user)).fetchone()
    custom=curseur.execute("SELECT Custom FROM custom WHERE ID={0}".format(user)).fetchone()
    emote=curseur.execute("SELECT * FROM emotes WHERE ID={0}".format(user)).fetchone()
    couleur=curseur.execute("SELECT * FROM couleurs WHERE ID={0}".format(user)).fetchone()
    vip,test=False,False

    if titre!=None:
        titre=titre["Nom"]
    else:
        titre="Inconnu"
    full=titre
    if custom!=None:
        custom=custom["Custom"]
        full=custom+", "+titre
    if emote!=None:
        emote=emote["IDEmote"]
    if couleur!=None:
        couleur=int('%02x%02x%02x' % (couleur["R"], couleur["G"], couleur["B"]),base=16)
        couleur="#"+hex(couleur)[2:]

    if curseurUser.execute("SELECT * FROM badges WHERE Période='VIP'").fetchone()!=None:
        vip=True
    if curseurUser.execute("SELECT * FROM badges WHERE Période='Testeur'").fetchone()!=None:
        test=True

    return {"Coins":coins,"Titre":titre,"Custom":custom,"Full":full,"Emote":emote,"Couleur":couleur,"VIP":vip,"Testeur":test}