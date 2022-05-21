from time import strftime

from companion.Getteurs import getAllInfos, getChannels, getGuildInfo
from companion.outils import (connectSQL, getCommon, getGuilds, rankingClassic,
                              tableauMois)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
def viewProfilHome(request,user):
    connexion,curseur=connectSQL("OT","Titres","Titres",None,None)
    connexionUser,curseurUser=connectSQL("OT",user,"Titres",None,None)
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    infos=getAllInfos(curseur,curseurUser,connexionUser,user)
    full_guilds=getGuilds(request.user,curseurGet)

    if user!=request.user.id:
        user_avatar=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Avatar"]
        user_name=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Nom"]
        options=["home","titres"]
        listeCom=getCommon(full_guilds,user,curseurGet)
        if len(listeCom)==0:
            user_avatar_profil=None
            user_name_profil=infos["Full"]
        else:
            user_avatar_profil=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user)).fetchone()["Avatar"]
            user_name_profil=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user)).fetchone()["Nom"]
    else:
        user_avatar=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Avatar"]
        user_name=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Nom"]
        user_avatar_profil=user_avatar
        user_name_profil=user_name
        options=["home","titres","custom","stats"]
        listeCom=[]

    liste=["P4","Tortues","TortuesDuo","TrivialVersus","TrivialParty","TrivialBR","Matrice","Morpion"]
    dictBadges={i:[] for i in liste}
    dictJeux={i:[] for i in liste}
    for i in liste:
        for j in curseurUser.execute("SELECT * FROM badges WHERE Type='{0}' ORDER BY Valeur DESC".format(i)).fetchall():
            dictBadges[i].append(j["Valeur"])
        
        try:
            connexion,curseur=connectSQL("OT",i,"Jeux","GL","")
            add=curseur.execute("SELECT * FROM glob WHERE ID={0}".format(user)).fetchone()
            if add!=None:
                dictJeux[i].append(add)
        except:
            pass

        try:
            connexion,curseur=connectSQL("OT",i,"Jeux","TO",strftime("%y"))
            add=curseur.execute("SELECT * FROM to{0} WHERE ID={1}".format(strftime("%y"),user)).fetchone()
            if add!=None:
                dictJeux[i].append(add)
        except:
            pass

        try:
            connexion,curseur=connectSQL("OT",i,"Jeux",strftime("%m"),strftime("%y"))
            add=curseur.execute("SELECT * FROM {0}{1} WHERE ID={2}".format(tableauMois[strftime("%m")].lower(),strftime("%y"),user)).fetchone()
            if add!=None:
                dictJeux[i].append(add)
        except:
            pass
        
        if dictJeux[i]==[]:
            del dictJeux[i]
            del dictBadges[i]
    
    liste=list(filter(lambda x:x in dictJeux, liste))
    dictMessages,dictSalons,dictEmotes,dictVoc,dictFreq=[],[],{},[],{}
    if user==request.user.id:
        for i in full_guilds:
            guild=getGuildInfo(i["ID"],curseurGet)
            try:
                connexion,curseur=connectSQL(i["ID"],"Messages","Stats","GL","")
                mess=curseur.execute("SELECT Rank,Count FROM glob WHERE ID={0}".format(user)).fetchone()
                if mess!=None:
                    if guild!=None:
                        dictMessages.append({"Rank":0,"Count":mess["Count"],"Icon":guild["Icon"],"ID":i["ID"],"Nom":guild["Nom"],"RankIntern":mess["Rank"]})
                    else:
                        dictMessages.append({"Rank":0,"Count":mess["Count"],"Icon":False,"ID":False,"Nom":"Autre serveur","RankIntern":mess["Rank"]})

                curseur.close()
                connexion.close()
            except:
                pass
            
            try:
                connexion,curseur=connectSQL(i["ID"],"Voice","Stats","GL","")
                voc=curseur.execute("SELECT Rank,Count FROM glob WHERE ID={0}".format(user)).fetchone()
                if voc!=None:
                    if guild!=None:
                        dictVoc.append({"Rank":0,"Count":voc["Count"],"Icon":guild["Icon"],"ID":i["ID"],"Nom":guild["Nom"],"RankIntern":voc["Rank"]})
                    else:
                        dictVoc.append({"Rank":0,"Count":voc["Count"],"Icon":False,"ID":False,"Nom":"Autre serveur","RankIntern":voc["Rank"]})
                curseur.close()
                connexion.close()
            except:
                pass

            try:
                connexion,curseur=connectSQL(i["ID"],"Salons","Stats","GL","")
                chan=curseur.execute("SELECT Rank,Count,ID FROM persoTOGL{0}".format(user)).fetchall()
                if chan!=[]:
                    if guild!=None:
                        for j in chan:
                            info=getChannels(j,curseurGet)
                            info["RankIntern"]=j["Rank"]
                            info["Icon"]=guild["Icon"]
                            info["IDGuild"]=guild["ID"]
                            dictSalons.append(info)
                    else:
                        for j in chan:
                            dictSalons.append({"ID":j["ID"],"Count":j["Count"],"RankIntern":j["Rank"],"Rank":0,"Icon":False,"IDGuild":False})
                curseur.close()
                connexion.close()
            except:
                pass

            try:
                connexion,curseur=connectSQL(i["ID"],"Freq","Stats","GL","")
                freq=curseur.execute("SELECT Rank,Count,ID FROM persoTOGL{0}".format(user)).fetchall()
                if freq!=[]:
                    for j in freq:
                        if j["ID"] not in dictFreq:
                            dictFreq[j["ID"]]=j["Count"]
                        else:
                            dictFreq[j["ID"]]+=j["Count"]
                curseur.close()
                connexion.close()
            except:
                pass

            try:
                connexion,curseur=connectSQL(i["ID"],"Emotes","Stats","GL","")
                emotes=curseur.execute("SELECT Rank,Count,ID FROM persoTOGL{0}".format(user)).fetchall()
                if emotes!=[]:
                    for j in emotes:
                        if j["ID"] not in dictEmotes:
                            dictEmotes[j["ID"]]=j["Count"]
                        else:
                            dictEmotes[j["ID"]]+=j["Count"]
                curseur.close()
                connexion.close()
            except:
                pass

    listeFreq=list(map(lambda x:{"ID":x,"Count":dictFreq[x],"Rank":0},dictFreq))
    listeEmotes=list(map(lambda x:{"ID":x,"Count":dictEmotes[x],"Rank":0},dictEmotes))
            
    rankingClassic(dictMessages)
    rankingClassic(dictSalons)
    rankingClassic(listeEmotes)
    rankingClassic(dictVoc)
    rankingClassic(listeFreq)

    dictMessages=list(filter(lambda x:x["Rank"]<=10, dictMessages))
    dictSalons=list(filter(lambda x:x["Rank"]<=10, dictSalons))
    listeEmotes=list(filter(lambda x:x["Rank"]<=10, listeEmotes))
    dictVoc=list(filter(lambda x:x["Rank"]<=10, dictVoc))
    listeFreq=list(filter(lambda x:x["Rank"]<=10, listeFreq))

    if dictMessages!=[]:
        maxiMess=max(dictMessages, key=lambda x:x["Count"])["Count"]
    else:
        maxiMess=0
    if dictSalons!=[]:
        maxiChan=max(dictSalons, key=lambda x:x["Count"])["Count"]
    else:
        maxiChan=0
    if listeEmotes!=[]:
        maxiEmote=max(listeEmotes, key=lambda x:x["Count"])["Count"]
    else:
        maxiEmote=0
    if dictVoc!=[]:
        maxiVoc=max(dictVoc, key=lambda x:x["Count"])["Count"]
    else:
        maxiVoc=0
    if listeFreq!=[]:
        maxiFreq=max(listeFreq, key=lambda x:x["Count"])["Count"]
    else:
        maxiFreq=0


    ctx={"badges":dictBadges,"stats":dictJeux,"jeux":liste,"guildscom":listeCom,
        "avatarprofil":user_avatar_profil,"idprofil":user,"nomprofil":user_name_profil,
        "avatar":user_avatar,"id":request.user.id,"nom":user_name,
        "titre":infos["Full"],"color":infos["Couleur"],"emote":infos["Emote"],"custom":infos["Custom"],"coins":infos["Coins"],
        "vip":infos["VIP"],"testeur":infos["Testeur"],
        "messages":dictMessages,"salons":dictSalons,"emotes":listeEmotes,"vocal":dictVoc,"freq":listeFreq,
        "maxMess":maxiMess,"maxChan":maxiChan,"maxEmote":maxiEmote,"maxVoc":maxiVoc,"maxFreq":maxiFreq,
        "options":options,"dictOptions":{"home":"Accueil","titres":"Titres","custom":"Personnalisation","stats":"Stats"},"option":"home"}

    return render(request, "companion/Profil/Profil.html", ctx)
