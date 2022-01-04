import requests


def getAllEmotes(full_guilds):
    full_emotes=[]
    for i in full_guilds:
        emotes=requests.get("https://discord.com/api/v9/guilds/{0}/emojis".format(i["ID"]),headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})
        if emotes.status_code==200:
            full_emotes+=emotes.json()
    return full_emotes


def getUserTable(i,guild,roles_position,roles_color):
    user_search=requests.get("https://discord.com/api/v9/guilds/{0}/members/{1}".format(guild,i["ID"]),headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})
    if user_search.status_code==200:
        user_search=user_search.json()
        user_search["roles"].sort(key=lambda x:roles_position[x], reverse=True)
        if len(user_search["roles"])==0:
            color=None
        else:
            color="#{0}".format(hex(roles_color[user_search["roles"][0]])[2:])
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":user_search["user"]["username"],"Color":color,"Avatar":user_search["user"]["avatar"],"ID":i["ID"]}
    else:
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":"Ancien membre","Color":None}


def getEmoteTable(i,full_emotes):
    find=list(filter(lambda x:int(x["id"])==i["ID"],full_emotes))
    if find==[]:
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":"Emote inconnue","ID":i["ID"],"Animated":False}
    else:
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":find[0]["name"],"ID":i["ID"],"Animated":find[0]["animated"]}


def getChannels(i):
    channel=requests.get("https://discord.com/api/v9/channels/{0}".format(i["ID"]),headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})
    if channel.status_code==200:
        channel=channel.json()
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":channel["name"],"ID":i["ID"]}
    else:
        return {"Count":i["Count"],"Rank":i["Rank"],"Nom":"Salon inconnu","ID":i["ID"]}


def getFreq(i):
    return {"Count":i["Count"],"Rank":i["Rank"],"Nom":"{0}h-{1}h".format(i["ID"],i["ID"]+1),"ID":i["ID"]}