from math import inf

from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import *
from companion.tools.outils import (collapseEvol, connectSQL, dictOptions,
                                    getMoisAnnee, getTimes, listeOptions,
                                    listeOptionsJeux, tableauMois)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companion.views.Serveurs.Stats.Evol.EvolGraph import evolGraphCompare

def compareEvolJeux(request,option):
    return viewEvolCompare(request,"OT",option)

@login_required(login_url="/login")
@CompanionStats
def viewEvolCompare(request,guild,option):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        pin=getPin(user,curseurGet,"jeux",option,"ranks","")
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
    else:
        pin=getPin(user,curseurGet,guild,option,"ranks","")
        categ="Stats"
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    if option in ("messages","voice","mots") or categ=="Jeux":
        obj1 = user.id
        obj2 = request.GET.get("obj")
    else:
        obj1 = request.GET.get("obj")
        obj2 = request.GET.get("obj2")

    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    listeMois,listeAnnee=getTimes(guild,option,categ)

    listeObj=objSelector(guild,option,categ,user,curseurGet,curseurGuild)

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

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)
    
    table=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,obj1)).fetchall()
    table=collapseEvol(table)  
    table.reverse() 

    table2=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,obj2)).fetchall()
    table2=collapseEvol(table2)  

    for i in range(len(table)):
        period=list(filter(lambda x:x["Mois"]==table[i]["Mois"] and x["Annee"]==table[i]["Annee"] and x["Jour"]==table[i]["Jour"],table2))
        if period!=[]:
            table[i]["Count2"]=period[0]["Count"]
            table[i]["Rank2"]=period[0]["Rank"]
            table[i]["Evol2"]=period[0]["Evol"]
            if not period[0]["Collapse"]:
                table[i]["Collapse"]=False

    if categ=="Jeux":
        maxi=max(max(list(map(lambda x:x["Count"],table))),max(list(map(lambda x:x["Count"],table2))))
        ctx={"rank":table,"max":maxi,"pagestats":True,"ot":True,
        "id":user.id,"color":None,"nom":user_full["Nom"],"avatar":user_full["Avatar"],
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "guildname":"Classement jeux","guildid":"ot/jeux",
        "command":"evol","options":listeOptionsJeux,"option":option,"plus":"compare",
        "travel":True,"selector":True,"listeObjs":listeObj,"obj":int(obj2),
        "user1ID":int(obj1),"user2ID":int(obj2),
        "pin":getPin(user,curseurGet,"ot/jeux",option,"evol","compare")}
    else:
        maxi=max(max(list(map(lambda x:x["Count"],table))),max(list(map(lambda x:x["Count"],table2))))
        ctx={"rank":table,"max":maxi,"pagestats":True,
        "id":user.id,"color":None,"nom":user_full["Nom"],"avatar":user_full["Avatar"],
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "command":"evol","options":listeOptions,"option":option,"plus":"compare",
        "travel":True,"selector":True,"listeObjs":listeObj,"obj":int(obj2),
        "user1ID":int(obj1),"user2ID":int(obj2),
        "pin":getPin(user,curseurGet,guild,option,"evol","compare")}

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
    else:
        ctx["user1Nom"]=getNom(obj1,option,curseurGet,False)
        ctx["user2Nom"]=getNom(obj2,option,curseurGet,False)
        color=getColor(user.id,guild,curseurGet)
        ctx["user1Color"]=color
        ctx["user2Color"]=color
        ctx["travel"]=False
        ctx["doubleObj"]=True

    ctx["graph"]=evolGraphCompare(option,curseur,obj1,obj2,moisDB,anneeDB,ctx["user1Nom"],ctx["user2Nom"],ctx["user1Color"],ctx["user2Color"])

    connexion.close()
    return render(request, "companion/Stats/Evol/evolCompare.html", ctx)
