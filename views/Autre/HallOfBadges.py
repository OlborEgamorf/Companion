from math import inf

from companion.Getteurs import *
from companion.outils import (connectSQL, dictOptions, dictRefCommands,
                              dictRefOptionsJeux, dictRefPlus, getPlus,
                              listeOptionsJeux)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
def viewBadges(request,option):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_avatar=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()["Avatar"]
    user_name=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()["Nom"]
    pin=getPin(user,curseurGet,"jeux",option,"badges","")

    connexion,curseur=connectSQL("OT","Titres","Titres",None,None)
    connexionRank,curseurRank=connectSQL("OT",dictOptions[option],"Jeux","GL","")

    badges={1:[],2:[],3:[],11:[],12:[],13:[],101:[],102:[],103:[]}
    for i in curseurRank.execute("SELECT * FROM glob").fetchall():
        connexionUser,curseurUser=connectSQL("OT",i["ID"],"Titres",None,None)
        badgesUser=curseurUser.execute("SELECT * FROM badges WHERE Type='{0}'".format(dictOptions[option])).fetchall()
        if len(badgesUser)!=0:
            titre=curseur.execute("SELECT titres.Nom FROM active JOIN titres ON active.TitreID=titres.ID WHERE MembreID={0}".format(i["ID"])).fetchone()
            custom=curseur.execute("SELECT Custom FROM custom WHERE ID={0}".format(i["ID"])).fetchone()
            emote=curseur.execute("SELECT * FROM emotes WHERE ID={0}".format(i["ID"])).fetchone()
            if titre!=None:
                titre=titre["Nom"]
            else:
                titre="Inconnu"
            if custom!=None:
                custom=custom["Custom"]
                full=custom+", "+titre
            else:
                full=titre
            if emote!=None:
                emote=emote["IDEmote"]
            
            for j in badgesUser:
                badges[j["Valeur"]].append({"ID":i["ID"],"Titre":full,"Emote":emote})
        
    ctx={"badges":badges,"levels":(103,102,101,13,12,11,3,2,1),
        "avatar":user_avatar,"id":user.id,"nom":user_name,
        "guildname":"Olbor Track - Mondial","guildid":"jeux",
        "commands":["ranks","periods","evol","first","badges"],"dictCommands":dictRefCommands,"command":"badges",
        "options":listeOptionsJeux,"dictOptions":dictRefOptionsJeux,"option":option,
        "lisPlus":getPlus("periods",option),"dictPlus":dictRefPlus,"plus":"",
        "travel":False,"selector":True}    

    return render(request, "companion/Badges.html", ctx)
