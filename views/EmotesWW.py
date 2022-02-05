from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..outils import (avatarAnim, connectSQL, dictRefCommands, dictRefOptions,
                      getCommands, getGuild, getGuilds, getUser, listeOptions)


@login_required(login_url="/login")
def emotesMondialGuild(request,guild):

    user=request.user
    guild_full=getGuild(guild)
    user_full=getUser(guild,user.id)
    full_guilds=getGuilds(user)

    user_avatar=user_full["user"]["avatar"]
    connexion,curseur=connectSQL("OT","Emotes","Stats","GL","")
    stats=curseur.execute("SELECT * FROM glob WHERE IDGuild={0} ORDER BY Rank ASC".format(guild)).fetchall()
    for j in stats:
        j["Icon"]=guild_full["icon"]
        
    maxi=stats[0]["Count"]
    
    ctx={"rank":stats,"max":maxi,
    "avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],"guilds":full_guilds,
    "commands":getCommands("emotes"),"dictCommands":dictRefCommands,"command":"mondial",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":"emotes","selector":False,
    "mois":"Total","annee":"Global"}

    return render(request, "companion/EmotesWW/emotesmondial.html", ctx)
