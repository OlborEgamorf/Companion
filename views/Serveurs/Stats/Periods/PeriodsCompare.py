from math import inf

from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, dictOptions, getTablePerso,
                              listeOptions,listeOptionsJeux)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companion.views.Serveurs.Stats.Periods.PeriodsGraph import linePlotCompare

def comparePeriodsJeux(request,option):
    return viewPeriodsCompare(request,"OT",option)

@login_required(login_url="/login")
def viewPeriodsCompare(request,guild,option):
    user=request.user
    
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
    else:
        categ="Stats"
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    if option in ("messages","voice","mots") or categ=="Jeux":
        obj1=user.id
        obj2 = request.GET.get("obj")
    else:
        obj1 = request.GET.get("obj")
        obj2 = request.GET.get("obj2")

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    listeObj=objSelector(guild,option,categ,user,curseurGet,curseurGuild,perso=True)

    if obj1==None:
        obj1=listeObj[1]["ID"]
    elif option in ("salons","voicechan"):
        hide=curseurGuild.execute("SELECT * FROM chans WHERE ID={0}".format(obj1)).fetchone()
        assert hide!=None and not hide["Hide"]
    if obj2==None:
        obj2=listeObj[0]["ID"]
    elif option in ("salons","voicechan"):
        hide=curseurGuild.execute("SELECT * FROM chans WHERE ID={0}".format(obj2)).fetchone()
        assert hide!=None and not hide["Hide"]

    if option in ("messages","voice","mots") or categ=="Jeux": 
        rankMois1=getTablePerso(guild,dictOptions[option],user.id,False,"M","countDesc")
        rankAnnee1=getTablePerso(guild,dictOptions[option],user.id,False,"A","countDesc")
        rankMois2=getTablePerso(guild,dictOptions[option],obj2,False,"M","countDesc")
        rankAnnee2=getTablePerso(guild,dictOptions[option],obj2,False,"A","countDesc")
    else:
        rankMois1=getTablePerso(guild,dictOptions[option],user.id,obj1,"M","countDesc")
        rankAnnee1=getTablePerso(guild,dictOptions[option],user.id,obj1,"A","countDesc")
        rankMois2=getTablePerso(guild,dictOptions[option],user.id,obj2,"M","countDesc")
        rankAnnee2=getTablePerso(guild,dictOptions[option],user.id,obj2,"A","countDesc")

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

    if categ=="Jeux":
        ctx={"rankMois":rankMois1,"rankAnnee":rankAnnee1,"maxM":maxiM,"maxA":maxiA,"pagestats":True,"ot":True,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"color":None,
        "guildname":"Classement jeux","guildid":"ot/jeux",
        "command":"periods","options":listeOptionsJeux,"option":option,"plus":"compareperso",
        "travel":False,"selector":True,"listeObjs":listeObj,"obj":int(obj2),
        "user1ID":int(obj1),"user2ID":int(obj2),
        "pin":getPin(user,curseurGet,guild,option,"periods","compareperso")}
    else:
        ctx={"rankMois":rankMois1,"rankAnnee":rankAnnee1,"maxM":maxiM,"maxA":maxiA,"pagestats":True,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"color":None,
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "command":"periods","options":listeOptions,"option":option,"plus":"compareperso",
        "travel":False,"selector":True,"listeObjs":listeObj,"obj":int(obj2),
        "user1ID":int(obj1),"user2ID":int(obj2),
        "pin":getPin(user,curseurGet,"ot/jeux",option,"periods","compareperso")}

    if option in ("messages","voice","mots"):
        infos1=getUserInfo(obj1,curseurGet,guild)
        if infos1!=None:
            ctx["user1Color"]=infos1["Color"]
            ctx["user1Avatar"]=infos1["Avatar"]
            ctx["user1Nom"]=infos1["Nom"]
        else:
            ctx["user1Nom"]="Vous"
    
        infos2=getUserInfo(obj2,curseurGet,guild)
        if infos2!=None:
            ctx["user2Color"]=infos2["Color"]
            ctx["user2Avatar"]=infos2["Avatar"]
            ctx["user2Nom"]=infos2["Nom"]
        else:
            ctx["user2Nom"]="Ancien membre"
        
        ctx["graph"]=linePlotCompare(guild,option,obj1,False,obj2,True,"M",infos1["Color"],infos2["Color"],infos1["Nom"],infos2["Nom"])
    elif categ=="Jeux":
        connexionUser,curseurUser=connectSQL("OT",obj1,"Titres",None,None)
        infos1=getAllInfos(curseurGet,curseurUser,connexionUser,obj1)
        if infos1!=None:
            ctx["user1Color"]=infos1["Color"]
            ctx["user1Emote"]=infos1["Emote"]
            ctx["user1Nom"]=infos1["Full"]
        else:
            ctx["user1Nom"]="Vous"
    
        connexionUser,curseurUser=connectSQL("OT",obj2,"Titres",None,None)
        infos2=getAllInfos(curseurGet,curseurUser,connexionUser,obj2)
        if infos2!=None:
            ctx["user2Color"]=infos2["Color"]
            ctx["user2Emote"]=infos2["Emote"]
            ctx["user2Nom"]=infos2["Full"]
        else:
            ctx["user2Nom"]="Inconnu"
        
        ctx["graph"]=linePlotCompare(guild,option,obj1,False,obj2,True,"M",infos1["Color"],infos2["Color"],infos1["Full"],infos2["Full"])
    else:
        ctx["user1Nom"]=getNom(obj1,option,curseurGet,False)
        ctx["user2Nom"]=getNom(obj2,option,curseurGet,False)
        color=getColor(user.id,guild,curseurGet)
        ctx["user1Color"]=color
        ctx["user2Color"]=color
        ctx["doubleObj"]=True

        ctx["graph"]=linePlotCompare(guild,option,user.id,obj1,obj2,True,"M","turquoise","gold",ctx["user1Nom"],ctx["user2Nom"])

    return render(request, "companion/Stats/Periods/periodsCompare.html", ctx)
