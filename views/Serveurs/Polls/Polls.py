import datetime
import time
from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, sendAndWait)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect


@login_required(login_url="/login")
def viewPolls(request,guild):
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

    active=curseurGuild.execute("SELECT * FROM polls WHERE Active=True ORDER BY ID DESC").fetchall()
    for i in active:
        if i["Channel"] not in ids:
            i["Hide"]=True
        else:
            i["Hide"]=False
        if i["Type"]!="polltime":
            data={
                "ot":"poll",
                "function":"results",
                "id":i["ID"],
                "user":user.id,
                "guild":guild,
            }
            data=sendAndWait(data)
            if data["status"]=="error":
                continue
            i["Results"]=data["results"]
            i["Total"]=data["total"]
            i["User"]=data["user"]
        if i["Total"]==0:
            i["Total"]=1

    all=curseurGuild.execute("SELECT * FROM polls WHERE Active=False ORDER BY ID DESC").fetchall()
    for i in all:
        if i["Channel"] not in ids:
            i["Hide"]=True
        else:
            i["Hide"]=False

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "command":"poll","option":"poll","plus":"",
    "travel":False,"selector":True,"obj":None,"pagepolls":True,
    "pin":pin,"active":active,"allpolls":all,"allchans":channels,"time":datetime.datetime.fromtimestamp(time.time()+1800).strftime('%Y-%m-%dT%H:%M'),"min":datetime.datetime.fromtimestamp(time.time()+60).strftime('%Y-%m-%dT%H:%M'),"max":datetime.datetime.fromtimestamp(time.time()+7776000).strftime('%Y-%m-%dT%H:%M')}
    
    return render(request, "companion/Polls/Polls.html", ctx)


def createPoll(request,guild):
    user=request.user
    try:
        question=request.POST.get("question")
        salon=request.POST.get("channel")
        temps=request.POST.get("time")
        option=request.POST.get("option")
        if option==None:
            option="polltime"
        assert question!="" and temps!="" and salon!=""

        epoch = datetime.datetime(int(temps[:4]), int(temps[5:7]), int(temps[8:10]), int(temps[11:13]), int(temps[14:16])).timestamp()
        secondes=int(epoch)-time.time()
        assert secondes>60 and secondes<7776000

        liste=[]
        for i in range(1,11):
            prop=request.POST.get("prop{0}".format(i))
            if prop not in (None,""):
                liste.append(prop)
        
        assert len(liste)>=2

        data={
            "ot":"poll",
            "function":"create",
            "question":question,
            "props":liste,
            "seconds":int(secondes),
            "salon":int(salon),
            "option":option,
            "auteur":user.id,
            "guild":guild,
        }
        data=sendAndWait(data)

        if data["status"]=="error":
            mess="Une erreur s'est produite au moment de l'envoi."
    except:
        mess="Le sondage a mal été rempli."
    
    return redirect("/companion/{0}/polls".format(guild))

def answerPoll(request,guild,pollid):
    user=request.user
    for i in range(1,11):
        if request.POST.get("vote{0}_{1}".format(pollid,i))=="Confirmer":
            data={
                "ot":"poll",
                "function":"vote",
                "id":pollid,
                "prop":i,
                "user":user.id,
                "guild":guild,
            }

            data=sendAndWait(data)

    return redirect("/companion/{0}/polls".format(guild))

def deletePoll(request,guild,pollid):
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    curseurGuild.execute("DELETE FROM polls WHERE ID={0}".format(pollid))
    connexionGuild.commit()
    return redirect("/companion/{0}/polls".format(guild))