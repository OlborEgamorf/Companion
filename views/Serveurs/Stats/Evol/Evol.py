from math import inf

from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import *
from companion.tools.outils import (collapseEvol, connectSQL, dictOptions,
                              getMoisAnnee, getTimes, listeOptions,
                              listeOptionsJeux, tableauMois)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def evolJeux(request,option):
    return viewEvol(request,"OT",option)

@login_required(login_url="/login")
@CompanionStats
def viewEvol(request,guild,option):
    mois,annee,obj = request.GET.get("mois"),request.GET.get("annee"),request.GET.get("obj")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        pin=getPin(user,curseurGet,"jeux",option,"evol","")
        categ="Jeux"
        listeMois,listeAnnee=getTimes(guild,option,"Jeux")
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)

        ctx={"rank":None,"max":None,"pagestats":True,"ot":True,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "guildname":"Olbor Track - Mondial","guildid":"ot/jeux",
        "command":"evol","options":listeOptionsJeux,"option":option,"plus":"",
        "travel":True,"selector":True,
        "pin":pin}
    else:
        pin=getPin(user,curseurGet,guild,option,"evol","")
        categ="Stats"
        listeMois,listeAnnee=getTimes(guild,option,"Stats")
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

        ctx={"rank":None,"max":None,"pagestats":True,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "command":"evol","options":listeOptions,"option":option,"plus":"","travel":True,"selector":True,"pin":pin}

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)
    if option in ("messages","voice","mots"):
        ctx["obj"]=None
        obj=user.id
        ctx["color"]=getColor(user.id,guild,curseurGet)
    elif categ=="Jeux":
        ctx["obj"]=None
        obj=user.id
        color=curseurGet.execute("SELECT * FROM couleurs WHERE ID={0}".format(user.id)).fetchone()
        if color!=None:
            ctx["color"]="#"+hex(int('%02x%02x%02x' % (color["R"], color["G"], color["B"]),base=16))[2:]
    else:
        listeObj=objSelector(guild,option,categ,user,curseurGet,curseurGuild)

        if obj==None:
            obj=listeObj[0]["ID"]
        elif option in ("salons","voicechan"):
            hide=curseurGuild.execute("SELECT * FROM chans WHERE ID={0}".format(obj)).fetchone()
            assert hide!=None and not hide["Hide"]
        
        ctx["obj"]=int(obj)
        ctx["listeObjs"]=listeObj
    
    table=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,obj)).fetchall()
    table=collapseEvol(table)
    table.reverse() 
    ctx["rank"]=table
    ctx["max"]=max(list(map(lambda x:x["Count"],table)))

    connexion.close()
    return render(request,"companion/Stats/Evol/evol.html",ctx)


@login_required(login_url="/login")
def iFrameEvol(request,guild,option):
    all=request.GET.get("data")
    jour,mois,annee,obj=all.split("?")
    if annee!="GL":
        annee="20"+annee
    mois,annee,moisDB,anneeDB=getMoisAnnee(tableauMois[mois],annee)
    user=request.user

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    
    if option!="freq":
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    connexion,curseur=connectSQL(guild,"Rapports","Stats","GL","")
    tabMois=curseur.execute("SELECT * FROM archives WHERE DateID={0}{1}{2} AND Type='{3}' AND Periode='Mois'".format(anneeDB,tableauMois[moisDB],jour,dictOptions[option])).fetchall()
    tabAnnee=curseur.execute("SELECT * FROM archives WHERE DateID={0}{1}{2} AND Type='{3}' AND Periode='Annee'".format(anneeDB,tableauMois[moisDB],jour,dictOptions[option])).fetchall()
    tabGlob=curseur.execute("SELECT * FROM archives WHERE DateID={0}{1}{2} AND Type='{3}' AND Periode='Global'".format(anneeDB,tableauMois[moisDB],jour,dictOptions[option])).fetchall()

    maxi=-inf
    dictUsers={}
    ctx={"id":user.id,"mois":mois,"annee":annee,"jour":jour,"option":option}
    liste={"moisTab":tabMois,"anneeTab":tabAnnee,"globTab":tabGlob}

    if obj!="None":
        ctx["id"]=int(obj)

    for table in liste:
        stats=[]
        if option in ("messages","voice","mots"):
            for i in liste[table]:
                if i["ID"] not in dictUsers:
                    userTable=getUserTable(i,curseurGet,curseurGuild,guild)
                    if userTable["Nom"]!="Ancien membre" and userTable["Nom"]!="Membre masqué":
                        dictUsers[i["ID"]]=[userTable["Color"],userTable["Nom"],userTable["Avatar"]]
                    else:
                        dictUsers[i["ID"]]=[None,userTable["Nom"],None]
                    stats.append(userTable)
                else:
                    stats.append({"Count":i["Count"],"Rank":i["Rank"],"Nom":dictUsers[i["ID"]][1],"Color":dictUsers[i["ID"]][0],"Avatar":dictUsers[i["ID"]][2],"ID":i["ID"]})
                maxi=max(maxi,i["Count"])

        elif option in ("emotes","reactions"):
            for i in liste[table]:
                if i["ID"] not in dictUsers:
                    emote=getEmoteTable(i,curseurGet)
                    dictUsers[i["ID"]]=[emote["Nom"],emote["Animated"]]
                    stats.append(emote)
                else:
                    stats.append({"Count":i["Count"],"Rank":i["Rank"],"Nom":dictUsers[i["ID"]][0],"Animated":dictUsers[i["ID"]][1],"ID":i["ID"]})

                maxi=max(maxi,i["Count"])

        elif option in ("salons","voicechan"):
            for i in liste[table]:
                if i["ID"] not in dictUsers:
                    chan=getChannels(i,curseurGet)
                    dictUsers[i["ID"]]=chan["Nom"]
                    stats.append(chan)
                else:
                    stats.append({"Count":i["Count"],"Rank":i["Rank"],"Nom":dictUsers[i["ID"]],"ID":i["ID"]})
                
                maxi=max(maxi,i["Count"])
        
        elif option=="freq":
            for i in liste[table]:
                if i["ID"] not in dictUsers:
                    freq=getFreq(i)
                    dictUsers[i["ID"]]=freq["Nom"]
                    stats.append(freq)
                else:
                    stats.append({"Count":i["Count"],"Rank":i["Rank"],"Nom":dictUsers[i["ID"]],"ID":i["ID"]})
                
                maxi=max(maxi,i["Count"])
    
        ctx[table]=stats.copy()
        ctx[table+"Maxi"]=maxi

    connexion.close()
    return render(request, "companion/Stats/Evol/iFrameEvol_archives.html", ctx)
