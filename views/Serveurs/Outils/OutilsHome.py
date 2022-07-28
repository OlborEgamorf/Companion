from companion.tools.Getteurs import *
from companion.tools.outils import connectSQL
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render


@login_required(login_url="/login")
def viewOutils(request,guild):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    pin=getPin(user,curseurGet,guild,"poll","ranks","")
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "command":"outils","option":"outils","plus":"",
    "travel":False,"selector":True,"obj":None,"pageoutils":True,
    "pin":pin,"listeOutils":["Alertes Twitch","Alertes YouTube","Alertes Twitter","Messages de Bienvenue","Messages d'Adieu","Roles","Tableaux","Voice Ephem","Icones Dynamiques","Commandes Auto","Commandes Personnalisées","Anniversaires"]}
    
    return render(request, "companion/Outils/OutilsHome.html", ctx)

