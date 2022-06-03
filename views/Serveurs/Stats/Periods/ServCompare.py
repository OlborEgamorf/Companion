from math import inf

from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, dictOptions, getTablePerso,
                              listeOptions)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
def viewServCompare(request,guild,option):
    user=request.user
    obj1 = request.GET.get("obj")
    obj2 = request.GET.get("obj2")

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    listeObj=objSelector(guild,option,"Stats",user,curseurGet,curseurGuild)

    if obj1==None:
        obj1=listeObj[1]["ID"]
    if obj2==None:
        obj2=listeObj[0]["ID"]

    rankMois1=getTablePerso(guild,dictOptions[option],obj1,False,"M","countDesc")
    rankAnnee1=getTablePerso(guild,dictOptions[option],obj1,False,"A","countDesc")
    rankMois2=getTablePerso(guild,dictOptions[option],obj2,False,"M","countDesc")
    rankAnnee2=getTablePerso(guild,dictOptions[option],obj2,False,"A","countDesc")

    maxiM=max(list(map(lambda x:x["Count"],rankMois1))+list(map(lambda x:x["Count"],rankMois2)))
    maxiA=max(list(map(lambda x:x["Count"],rankAnnee1))+list(map(lambda x:x["Count"],rankAnnee2)))

    for i in range(len(rankMois1)):
        period=list(filter(lambda x:x["Mois"]==rankMois1[i]["Mois"] and x["Annee"]==rankMois1[i]["Annee"],rankMois2))
        if period!=[]:
            rankMois1[i]["Count2"]=period[0]["Count"]
            rankMois1[i]["Rank2"]=period[0]["Rank"]
    for i in range(len(rankAnnee1)):
        period=list(filter(lambda x:x["Annee"]==rankAnnee1[i]["Annee"],rankAnnee2))
        if period!=[]:
            rankAnnee1[i]["Count2"]=period[0]["Count"]
            rankAnnee1[i]["Rank2"]=period[0]["Rank"]

    ctx={"rankMois":rankMois1,"rankAnnee":rankAnnee1,"maxM":maxiM,"maxA":maxiA,"pagestats":True,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"color":None,
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "command":"periods","options":listeOptions,"option":option,"plus":"compare",
    "travel":False,"selector":True,"listeObjs":listeObj,"obj":int(obj2),
    "user1ID":int(obj1),"user2ID":int(obj2),
    "pin":getPin(user,curseurGet,guild,option,"periods","compare")}

    ctx["user1Nom"]=getNom(obj1,option,curseurGet,False)
    ctx["user2Nom"]=getNom(obj2,option,curseurGet,False)
    ctx["doubleObj"]=True

    return render(request, "companion/Stats/Periods/periodsCompare.html", ctx)
