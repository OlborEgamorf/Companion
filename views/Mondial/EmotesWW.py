from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companion.outils import (connectSQL, dictRefCommands, dictRefOptions,
                      getCommands, listeOptions)


@login_required(login_url="/login")
def emotesMondialGuild(request,guild):

    user=request.user
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    connexion,curseur=connectSQL("OT","Emotes","Stats","GL","")
    stats=curseur.execute("SELECT * FROM glob WHERE IDGuild={0} ORDER BY Rank ASC".format(guild)).fetchall()
    for j in stats:
        j["Icon"]=guild_full["icon"]
        
    maxi=stats[0]["Count"]
    
    ctx={"rank":stats,"max":maxi,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["name"],"guildid":guild,"guildicon":guild_full["icon"],
    "commands":getCommands("emotes"),"dictCommands":dictRefCommands,"command":"mondial",
    "options":listeOptions,"dictOptions":dictRefOptions,"option":"emotes","selector":False,
    "mois":"Total","annee":"Global"}

    return render(request, "companion/EmotesWW/emotesmondial.html", ctx)
