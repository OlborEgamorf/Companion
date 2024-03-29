from companion.tools.outils import connectSQL,dictOptions,dictDivers
from companion.templatetags.TagsCustom import tempsVoice


def getUserTable(i,curseurGet,curseurGuild,guild):
    hide=curseurGuild.execute("SELECT * FROM users WHERE ID={0}".format(i["ID"])).fetchone()
    if hide==None or hide["Hide"]:
        return {"Count":0,"Rank":i["Rank"],"Nom":"Membre masqué","Color":None,"Avatar":None,"ID":0}
    infos=curseurGet.execute("SELECT * FROM users JOIN users_{0} ON users.ID = users_{0}.ID WHERE users.ID={1}".format(guild,i["ID"])).fetchone()
    if infos==None:
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":"Ancien membre","Color":None,"Avatar":None,"ID":i["ID"]}
    else:
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":infos["Nom"],"Color":formatColor(infos["Color"]),"Avatar":infos["Avatar"],"ID":i["ID"]}

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


def getChannels(i,curseurGet,curseurGuild):
    hide=curseurGuild.execute("SELECT * FROM chans WHERE ID={0}".format(i["ID"])).fetchone()
    if hide==None or hide["Hide"]:
        return {"Count":0,"Rank":i["Rank"],"Nom":"Salon masqué","ID":0}
    infos=curseurGet.execute("SELECT * FROM salons WHERE ID={0}".format(i["ID"])).fetchone()
    if infos!=None:
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":infos["Nom"],"ID":i["ID"]}
    else:
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":"Salon inconnu","ID":i["ID"]}


def getFreq(i):
    return {"Count":i["Count"],"Rank":i["Rank"],"Nom":"{0}h-{1}h".format(i["ID"],int(i["ID"])+1),"ID":i["ID"]}

def getDivers(i):
    if i["ID"]==11:
        return {"Count":tempsVoice(i["Count"]),"Rank":i["Rank"],"Nom":dictDivers[i["ID"]],"ID":i["ID"]}
    return {"Count":i["Count"],"Rank":i["Rank"],"Nom":dictDivers[i["ID"]],"ID":i["ID"]}


def getColor(id,guild,curseurGet):
    infos=curseurGet.execute("SELECT * FROM users_{0} WHERE ID={1}".format(guild,id)).fetchone()
    if infos!=None and infos["Color"]!=None:
        return formatColor(infos["Color"])
    return None

def getGuildInfo(id,curseurGet):
    return curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(id)).fetchone()

def getUserInfo(id,curseurGet,guild):
    infos=curseurGet.execute("SELECT * FROM users JOIN users_{0} ON users.ID = users_{0}.ID WHERE users.ID={1}".format(guild,id)).fetchone()
    if infos==None:
        return {"ID":id,"Nom":"Ancien membre","Color":"#239100","Avatar":None}
    if infos["Color"]!=None:
        infos["Color"]=formatColor(infos["Color"])
    if len(infos["Nom"])>15:
        infos["Nom"]=infos["Nom"][:15]+"..."
    return infos

def getUserInfoMix(id,guilds,curseurGet):
    infos=None
    for guild in guilds:
        infoGuild=getUserInfo(id,curseurGet,guild)
        if infoGuild["Nom"]!="Ancien membre":
            infos=infoGuild
    if infos==None:
        return {"ID":id,"Nom":"Ancien membre","Color":"#239100","Avatar":None}
    if infos["Color"]!=None:
        infos["Color"]=formatColor(infos["Color"])
    return infos

def getNom(id,option,curseurGet,obj):
    if option in ("messages","voice","mots") or obj:
        infos=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(id)).fetchone()
    elif option in ("emotes","reactions"):
        infos=curseurGet.execute("SELECT * FROM emotes WHERE ID={0}".format(id)).fetchone()
    elif option in ("salons","voicechan"):
        infos=curseurGet.execute("SELECT * FROM salons WHERE ID={0}".format(id)).fetchone()
    elif option=="freq":
        infos={"Nom":"{0}h-{1}h".format(id,int(id)+1)}
    if infos!=None:
        if len(infos["Nom"])>15:
            return infos["Nom"][:15]+"..."
        else:
            return infos["Nom"]
    return "Inconnu"

def getUserJeux(i,curseurGet,jeu):
    connexionUser,curseurUser=connectSQL("OT",i["ID"],"Titres",None,None)
    infos=getAllInfos(curseurGet,curseurUser,connexionUser,i["ID"])
    badgeJeu=curseurUser.execute("SELECT * FROM badges WHERE Type='{0}' ORDER BY Valeur DESC".format(dictOptions[jeu])).fetchone()
    if badgeJeu!=None:
        badgeJeu=badgeJeu["Valeur"]
    return {"Count":i["Count"],"Rank":i["Rank"],"Nom":infos["Full"],"Color":infos["Color"],"Emote":infos["Emote"],"ID":i["ID"],"VIP":infos["VIP"],"Testeur":infos["Testeur"],"BadgeJeu":badgeJeu,"Win":i["W"],"Lose":i["L"]}

def createAccount(connexion,curseur):
    curseur.execute("CREATE TABLE IF NOT EXISTS titresUser (ID INT, Nom TEXT, Rareté INT, PRIMARY KEY(ID))")
    curseur.execute("CREATE TABLE IF NOT EXISTS coins (Coins INT)")
    curseur.execute("CREATE TABLE IF NOT EXISTS badges (Type TEXT, Période TEXT, Rang INT, Valeur INT, PRIMARY KEY(Type,Période,Rang))")
    if curseur.execute("SELECT * FROM coins").fetchone()==None:
        curseur.execute("INSERT INTO coins VALUES(0)")
    connexion.commit()
def getAllInfos(curseur,curseurUser,connexionUser,user):
    createAccount(connexionUser,curseurUser)
    coins=curseurUser.execute("SELECT * FROM coins").fetchone()["Coins"]
    titre=curseur.execute("SELECT titres.Nom FROM active JOIN titres ON active.TitreID=titres.ID WHERE MembreID={0}".format(user)).fetchone()
    custom=curseur.execute("SELECT Custom FROM custom WHERE ID={0}".format(user)).fetchone()
    emote=curseur.execute("SELECT * FROM emotes WHERE ID={0}".format(user)).fetchone()
    couleur=curseur.execute("SELECT * FROM couleurs WHERE ID={0}".format(user)).fetchone()
    vip,test=False,False

    carte=curseur.execute("SELECT * FROM cartes WHERE ID={0}".format(user)).fetchone()
    if carte==None:
        fond="defaut"
        phrase=""
    else:
        fond=carte["Fond"]
        if carte["Texte"]=="None":
            phrase=""
        else:
            phrase=carte["Texte"]

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
        couleur=formatColor(couleur)

    if curseurUser.execute("SELECT * FROM badges WHERE Période='VIP'").fetchone()!=None:
        vip=True
    if curseurUser.execute("SELECT * FROM badges WHERE Période='Testeur'").fetchone()!=None:
        test=True

    return {"Coins":coins,"Titre":titre,"Custom":custom,"Full":full,"Emote":emote,"Color":couleur,"VIP":vip,"Testeur":test,"Fond":fond,"Phrase":phrase}

def formatColor(color):
    hexa=hex(int(color))[2:]
    return "#"+"0"*(6-len(hexa))+hexa

def addInfos(table,dictInfos,option,guild,curseurGet):
    for i in table:
        if i["ID"] in dictInfos:
            if option in ("messages","voice","mots"):
                i["Nom"]=dictInfos[i["ID"]]["Nom"]
                i["Avatar"]=dictInfos[i["ID"]]["Avatar"]
                i["Color"]=dictInfos[i["ID"]]["Color"]
            else:
                i["Nom"]=dictInfos[i["ID"]]
        else:
            if option in ("messages","voice","mots"):
                infos=getUserInfo(i["ID"],curseurGet,guild)
                i["Nom"]=infos["Nom"]
                i["Avatar"]=infos["Avatar"]
                i["Color"]=infos["Color"]
            else:
                infos=getNom(i["ID"],option,curseurGet,False)
                i["Nom"]=infos

def getInfoMix(user,mix,curseurGet):
    connexionMix,curseurMix=connectSQL("OT","Mixes","Guild",None,None)
    infosMix=curseurMix.execute("SELECT * FROM mixes_{0} WHERE Nombre={1}".format(user.id,mix)).fetchone()
    assert infosMix!=None
    listeMixs=[]
    mix_ids=[]
    for j in range(1,6):
        if infosMix["Serveur{0}".format(j)]!=0:
            mix_ids.append(infosMix["Serveur{0}".format(j)])
            infosGuild=getGuildInfo(infosMix["Serveur{0}".format(j)],curseurGet)
            listeMixs.append({"ID":infosMix["Serveur{0}".format(j)],"Icon":infosGuild["Icon"],"Nom":infosGuild["Nom"]})
    return mix_ids,infosMix,listeMixs

def getPin(user,curseurGet,guild,option,command,plus):
    try:
        pin=curseurGet.execute("SELECT * FROM pin_{0} WHERE Guild='{1}' AND Option='{2}' AND Command='{3}' AND Plus='{4}'".format(user.id,guild,option,command,plus)).fetchone()
        if pin!=None:
            return True
        else:
            return False
    except:
        return False


def chooseGetteur(option,categ,ligne,guild,curseurGet,curseurGuild):
    if option in ("messages","voice","mots"):
        return getUserTable(ligne,curseurGet,curseurGuild,guild)

    elif option in ("emotes","reactions"):
        return getEmoteTable(ligne,curseurGet)

    elif option in ("salons","voicechan"):
        return getChannels(ligne,curseurGet,curseurGuild)

    elif option=="freq":
        return getFreq(ligne)

    elif option=="divers":
        return getDivers(ligne)
    
    elif categ=="Jeux":
        return getUserJeux(ligne,curseurGet,option)


def objSelector(guild,option,categ,user,curseurGet,curseurGuild,perso=False):
    connexion,curseur=connectSQL(guild,dictOptions[option],categ,"GL","")
    if option in ("messages","voice","mots") or categ=="Jeux" or not perso:
        listeObj=curseur.execute("SELECT * FROM glob ORDER BY Count DESC LIMIT 150").fetchall()
    else:
        listeObj=curseur.execute("SELECT * FROM persoTOGL{0} ORDER BY Count DESC LIMIT 150".format(user.id)).fetchall()
    if option in ("emotes","reactions"):
        listeObj=list(map(lambda x:getEmoteTable(x,curseurGet),listeObj))
    elif option in ("salons","voicechan"):
        listeObj=list(map(lambda x:getChannels(x,curseurGet,curseurGuild),listeObj))
    elif option=="freq":
        listeObj=list(map(lambda x:getFreq(x),listeObj))
    elif option in ("messages","voice","mots"):
        listeObj=list(map(lambda x:getUserTable(x,curseurGet,curseurGuild,guild),listeObj))
    elif categ=="Jeux":
        listeObj=list(map(lambda x:getUserJeux(x,curseurGet,option),listeObj))
    elif option=="divers":
        listeObj=list(map(lambda x:getDivers(x),listeObj))

    listeObj=list(filter(lambda x:x["ID"]!=user.id,listeObj))
    listeObj=list(filter(lambda x:x["Nom"]!="Ancien membre",listeObj))
    listeObj=list(filter(lambda x:x["Nom"]!="Membre masqué",listeObj))
    listeObj=list(filter(lambda x:x["Nom"]!="Salon masqué",listeObj))
    return listeObj