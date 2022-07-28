from companion.tools.Getteurs import *
from companion.tools.outils import connectSQL, createPhrase
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

@login_required(login_url="/login")
def viewGestionTableaux(request,guild):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    emotes=curseurGet.execute("SELECT * FROM emotes WHERE GuildID={0} ORDER BY Nom ASC".format(guild)).fetchall()
    emotes.insert(0,{"ID":"all","Nom":"N'importe quelle emote"})


    pin=getPin(user,curseurGet,guild,"poll","ranks","")
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)

    etatTab=curseurGuild.execute("SELECT * FROM etatModules WHERE Module='Tableaux'").fetchone()
    tableaux=curseurGuild.execute("SELECT * FROM sb").fetchall()

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "command":"Tableauxad","option":"outils","plus":"","etatTab":etatTab,"tableaux":tableaux,"emotes":emotes,
    "travel":False,"selector":True,"obj":None,"pageoutils":True,
    "pin":pin}
    
    return render(request, "companion/Outils/Tableaux.html", ctx) 

def toggleTab(request,guild,idtab):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    if request.GET.get("active")=="true":
        curseurGuild.execute("UPDATE sb SET Active=True WHERE Nombre={0}".format(idtab))
    else:
        curseurGuild.execute("UPDATE sb SET Active=False WHERE Nombre={0}".format(idtab))
    connexionGuild.commit()
    return JsonResponse(data={})

def toggleTableaux(request,guild):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    if request.GET.get("active")=="true":
        curseurGuild.execute("UPDATE etatModules SET Active=True WHERE Module='Tableaux'")
    else:
        curseurGuild.execute("UPDATE etatModules SET Active=False WHERE Module='Tableaux'")
    connexionGuild.commit()
    return JsonResponse(data={})

def editTab(request,guild,idtab):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    salon,react=request.GET.get("emote"),request.GET.get("salon"),request.GET.get("react")
    curseurGuild.execute("UPDATE sb SET Salon={0}, Count={1} WHERE Nombre={2}".format(salon,react,idtab))
    connexionGuild.commit()
    return JsonResponse(data={})

def addTab(request,guild):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    count=curseurGuild.execute("SELECT Count FROM etatModules WHERE Module='Tableaux'").fetchone()["Count"]
    curseurGuild.execute("UPDATE etatModules SET Count=Count+1 WHERE Module='Tableaux'")
    if emote=="all":
        emote,emoteID="all",0
    else:
        fullemote=curseurGet.execute("SELECT * FROM emotes WHERE ID={0}".format(emote)).fetchone()
        emote,emoteID=fullemote["Full"],emote
    salon,react=request.GET.get("emote"),request.GET.get("salon"),request.GET.get("react")
    curseurGuild.execute("INSERT INTO sb VALUES ({0},{1},'{2}',{3},{4},True)".format(count+1,salon,emote,emoteID,react))
    connexionGuild.commit()
    return JsonResponse(data={"count":count+1})

def delTab(request,guild,idtab):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    curseurGuild.execute("DELETE FROM sb WHERE Nombre={0}".format(idtab))
    connexionGuild.commit()
    return JsonResponse(data={})
