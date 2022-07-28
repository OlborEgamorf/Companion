from companion.tools.Getteurs import *
from companion.tools.outils import connectSQL, createPhrase
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

@login_required(login_url="/login")
def viewGestionVoiceEphem(request,guild):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    pin=getPin(user,curseurGet,guild,"poll","ranks","")
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    connexionVoice,curseurVoice=connectSQL(guild,"VoiceEphem","Guild",None,None)

    etatVoice=curseurGuild.execute("SELECT * FROM etatModules WHERE Module='VoiceEphem'").fetchone()
    hubs=curseurVoice.execute("SELECT * FROM hub").fetchall()
    for i in hubs:
        nom=curseurGet.execute("SELECT * FROM salons WHERE ID={0}".format(i["ID"])).fetchone()
        if nom!=None:
            i["Nom"]=nom["Nom"]
    salons=curseurVoice.execute("SELECT * FROM salons").fetchall()

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "command":"VoiceEphemad","option":"outils","plus":"","etatVoice":etatVoice,"hubs":hubs,"salons":salons,
    "travel":False,"selector":True,"obj":None,"pageoutils":True,
    "pin":pin}
    
    return render(request, "companion/Outils/VoiceEphem.html", ctx) 

def toggleHub(request,guild,idhub):
    connexionVoice,curseurVoice=connectSQL(guild,"VoiceEphem","Guild",None,None)
    if request.GET.get("active")=="true":
        curseurVoice.execute("UPDATE hub SET Active=True WHERE Nombre={0}".format(idhub))
    else:
        curseurVoice.execute("UPDATE hub SET Active=False WHERE Nombre={0}".format(idhub))
    connexionVoice.commit()
    return JsonResponse(data={})

def toggleVoiceEphem(request,guild):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    if request.GET.get("active")=="true":
        curseurGuild.execute("UPDATE etatModules SET Active=True WHERE Module='VoiceEphem'")
    else:
        curseurGuild.execute("UPDATE etatModules SET Active=False WHERE Module='VoiceEphem'")
    connexionGuild.commit()
    return JsonResponse(data={})

def editHub(request,guild,idhub):
    connexionVoice,curseurVoice=connectSQL(guild,"VoiceEphem","Guild",None,None)
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    limite,pattern=request.GET.get("limite"),request.GET.get("pattern")
    curseurVoice.execute("UPDATE hub SET Limite={0}, Pattern='{1}' WHERE Nombre={2}".format(limite,pattern,idhub))
    connexionVoice.commit()
    return JsonResponse(data={})

def addHub(request,guild):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    connexionVoice,curseurVoice=connectSQL(guild,"VoiceEphem","Guild",None,None)
    count=curseurGuild.execute("SELECT Count FROM etatModules WHERE Module='VoiceEphem'").fetchone()["Count"]
    curseurGuild.execute("UPDATE etatModules SET Count=Count+1 WHERE Module='VoiceEphem'")
    limite,pattern,salon=request.GET.get("limite"),request.GET.get("pattern"),request.GET.get("salon")
    curseurVoice.execute("INSERT INTO hub VALUES ({0},{1},{2},'{3}',True)".format(count+1,salon,limite,pattern))
    connexionGuild.commit()
    connexionVoice.commit()
    return JsonResponse(data={"count":count+1})

def delHub(request,guild,idhub):
    connexionVoice,curseurVoice=connectSQL(guild,"VoiceEphem","Guild",None,None)
    curseurVoice.execute("DELETE FROM hub WHERE Nombre={0}".format(idhub))
    connexionVoice.commit()
    return JsonResponse(data={})
