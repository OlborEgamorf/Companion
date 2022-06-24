import datetime
import time
from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, sendAndWait)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect


@login_required(login_url="/login")
def viewPetitions(request,guild):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    pin=getPin(user,curseurGet,guild,"poll","ranks","")
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)

    data={"ot":"channels","function":"get","user":user.id,"guild":guild}
    data=sendAndWait(data)

    channels=data["channels"]
    ids=list(map(lambda x:x["id"],channels))

    active=curseurGuild.execute("SELECT * FROM petitions WHERE Active=True ORDER BY ID DESC").fetchall()
    for i in active:
        if i["Channel"] not in ids:
            i["Hide"]=True
        else:
            i["Hide"]=False
        data={
            "ot":"petition",
            "function":"results",
            "id":i["ID"],
            "user":user.id,
            "guild":guild,
        }
        data=sendAndWait(data)
        if data["status"]=="error":
            continue
        i["Final"]=data["total"]
        i["User"]=data["user"]

    all=curseurGuild.execute("SELECT * FROM petitions WHERE Active=False ORDER BY ID DESC").fetchall()
    for i in all:
        if i["Channel"] not in ids:
            i["Hide"]=True
        else:
            i["Hide"]=False

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "command":"petitions","option":"petitions","plus":"",
    "travel":False,"selector":True,"obj":None,"pagepolls":True,
    "pin":pin,"active":active,"allpolls":all,"allchans":channels,"time":datetime.datetime.fromtimestamp(time.time()+1800).strftime('%Y-%m-%dT%H:%M'),"min":datetime.datetime.fromtimestamp(time.time()+60).strftime('%Y-%m-%dT%H:%M'),"max":datetime.datetime.fromtimestamp(time.time()+7776000).strftime('%Y-%m-%dT%H:%M')}
    
    return render(request, "companion/Polls/Petitions.html", ctx)


def createPetition(request,guild):
    user=request.user
    try:
        question=request.POST.get("question")
        salon=request.POST.get("channel")
        temps=request.POST.get("time")
        signatures=request.POST.get("signatures")
        descip=request.POST.get("description")
        assert question!="" and temps!="" and salon!="" and signatures!="" and len(descip)<400

        epoch = datetime.datetime(int(temps[:4]), int(temps[5:7]), int(temps[8:10]), int(temps[11:13]), int(temps[14:16])).timestamp()
        secondes=int(epoch)-time.time()
        assert secondes>60 and secondes<7776000

        data={
            "ot":"petition",
            "function":"create",
            "question":question,
            "seconds":int(secondes),
            "signatures":int(signatures),
            "description":descip,
            "salon":int(salon),
            "auteur":user.id,
            "guild":guild,
        }
        data=sendAndWait(data)

        if data["status"]=="error":
            mess="Une erreur s'est produite au moment de l'envoi."
    except:
        mess="Le sondage a mal été rempli."
    
    return redirect("/companion/{0}/polls/petitions/".format(guild))

def votePetition(request,guild,pollid):
    user=request.user
    data={
        "ot":"petition",
        "function":"vote",
        "id":pollid,
        "user":user.id,
        "guild":guild,
    }
    data=sendAndWait(data)
    return redirect("/companion/{0}/polls/petitions".format(guild))

