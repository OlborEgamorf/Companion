import requests


def getUserTable(i,curseurGet,guild):
    infos=curseurGet.execute("SELECT * FROM users JOIN users_{0} ON users.ID = users_{0}.ID WHERE users.ID={1}".format(guild,i["ID"])).fetchone()
    if infos==None:
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":"Ancien membre","Color":None,"Avatar":None,"ID":None}
    else:
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":infos["Nom"],"Color":"#"+hex(infos["Color"])[2:],"Avatar":infos["Avatar"],"ID":i["ID"]}

def getEmoteTable(i,curseurGet):
    infos=curseurGet.execute("SELECT * FROM emotes WHERE ID={0}".format(i["ID"])).fetchone()
    if infos==None:
        try:
            chr(i["ID"])
            return {"Count":i["Count"],"Rank":i["Rank"],"Nom":"twemoji","ID":i["ID"],"Animated":False} 
        except:
            return {"Count":i["Count"],"Rank":i["Rank"],"Nom":"Emote inconnue","ID":i["ID"],"Animated":False}
    else:
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":infos["Nom"],"ID":i["ID"],"Animated":infos["Animated"]}


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