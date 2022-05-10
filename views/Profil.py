from math import inf
from time import strftime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companion.Getteurs import getAllInfos, getChannels, getGuildInfo

from ..outils import connectSQL, getGuilds, rankingClassic

tableauMois={"01":"Janvier","02":"Février","03":"Mars","04":"Avril","05":"Mai","06":"Juin","07":"Juillet","08":"Aout","09":"Septembre","10":"Octobre","11":"Novembre","12":"Décembre","TO":"Année","janvier":"01","février":"02","mars":"03","avril":"04","mai":"05","juin":"06","juillet":"07","aout":"08","septembre":"09","octobre":"10","novembre":"11","décembre":"12","glob":"GL","to":"TO"}

def getCommon(me,user,curseurGet):
    listeCom=[]
    connexionAll,curseurAll=connectSQL("OT","Users","Guild",None,None)
    myguilds=curseurAll.execute("SELECT * FROM user{0}".format(me)).fetchall()
    myguilds=list(map(lambda x:x["Guild"], myguilds))
    for i in curseurAll.execute("SELECT * FROM user{0}".format(user)).fetchall():
        if i["Guild"] in myguilds:
            guild=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(i["Guild"])).fetchone()
            if guild!=None:
                listeCom.append({"ID":i["Guild"],"Icon":guild["Icon"],"Nom":guild["Nom"]})
    connexionAll.close()
    return listeCom

@login_required(login_url="/login")
def viewProfilHome(request,user):
    connexion,curseur=connectSQL("OT","Titres","Titres",None,None)
    connexionUser,curseurUser=connectSQL("OT",user,"Titres",None,None)
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    infos=getAllInfos(curseur,curseurUser,connexionUser,user)

    if user!=request.user.id:
        user_avatar=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Avatar"]
        user_name=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Nom"]
        options=["home","titres"]
        listeCom=getCommon(request.user.id,user,curseurGet)
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
        full_guilds=getGuilds(request.user)
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


# /users/@me/relationships
#https://codepen.io/robmazan/pen/PwJbav


@login_required(login_url="/login")
def viewProfilTitres(request,user):
    dictValue={1:300,2:600,3:1000,5:2500}
    dictSell={0:"Inestimable",1:150,2:300,3:500,4:"Inestimable",5:"Inestimable",6:"Inestimable"}

    connexion,curseur=connectSQL("OT","Titres","Titres",None,None)
    connexionUser,curseurUser=connectSQL("OT",user,"Titres",None,None)
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    infos=getAllInfos(curseur,curseurUser,connexionUser,user)

    if user!=request.user.id:
        user_avatar_profil=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user)).fetchone()["Avatar"]
        user_name_profil=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user)).fetchone()["Nom"]
        user_avatar=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Avatar"]
        user_name=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Nom"]
        connexionUserCo,curseurUserCo=connectSQL("OT",request.user.id,"Titres",None,None)
        coins=curseurUserCo.execute("SELECT * FROM coins").fetchone()["Coins"]
        options=["home","titres"]
        listeCom=getCommon(request.user.id,user,curseurGet)
    else:
        user_avatar=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Avatar"]
        user_name=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Nom"]
        user_avatar_profil=user_avatar
        user_name_profil=user_name
        coins=infos["Coins"]
        options=["home","titres","custom","stats"]
        listeCom=[]

    mess,colorMess=None,None
    if request.method=="POST":
        for i in curseur.execute("SELECT marketplace.ID,marketplace.Stock,titres.Rareté,titres.Nom,marketplace.Known,titres.Description,titres.Collection FROM marketplace JOIN titres ON marketplace.ID=titres.ID").fetchall():
            if request.POST.get("achat{0}".format(i["ID"]))=="Confirmer":
                try:
                    assert i["Stock"]!=0, "il n'est plus en stock dans la boutique !"
                    assert coins>=dictValue[i["Rareté"]], "vous n'avez pas assez d'OT Coins !"
                    assert curseurUser.execute("SELECT * FROM titresUser WHERE ID={0}".format(i["ID"])).fetchone()==None, "vous le possèdez déjà !"
                    if i["Rareté"]==5:
                        assert curseurUser.execute("SELECT COUNT() AS Count FROM titresUser WHERE Rareté=5").fetchone()["Count"]==0, "vous possèdez déjà un titre Unique !"

                    curseur.execute("UPDATE marketplace SET Stock=Stock-1 WHERE ID={0}".format(i["ID"]))
                    curseurUser.execute("UPDATE coins SET Coins=Coins-{0}".format(dictValue[i["Rareté"]]))
                    curseurUser.execute("INSERT INTO titresUser VALUES({0},'{1}',{2})".format(i["ID"],i["Nom"],i["Rareté"]))
                    coins-=dictValue[i["Rareté"]]
                    mess,colorMess="Titre {0} acheté avec succès !".format(i["Nom"]),"green"

                except AssertionError as er:
                    mess,colorMess="Vous ne pouvez pas acheter ce titre : {0}".format(er),"red"
                break

            if request.POST.get("offrir{0}".format(i["ID"]))=="Confirmer":
                try:
                    assert i["Stock"]!=0, "il n'est plus en stock dans la boutique !"
                    assert coins>=dictValue[i["Rareté"]], "vous n'avez pas assez d'OT Coins !"
                    assert curseurUser.execute("SELECT * FROM titresUser WHERE ID={0}".format(i["ID"])).fetchone()==None, "cette personne possède déjà le titre !"
                    if i["Rareté"]==5:
                        assert curseurUser.execute("SELECT COUNT() AS Count FROM titresUser WHERE Rareté=5").fetchone()["Count"]==0, "cette personne possède déjà un titre Unique !"

                    curseur.execute("UPDATE marketplace SET Stock=Stock-1 WHERE ID={0}".format(i["ID"]))
                    curseurUserCo.execute("UPDATE coins SET Coins=Coins-{0}".format(dictValue[i["Rareté"]]))
                    curseurUser.execute("INSERT INTO titresUser VALUES({0},'{1}',{2})".format(i["ID"],i["Nom"],i["Rareté"]))
                    coins-=dictValue[i["Rareté"]]
                    mess,colorMess="Titre {0} offert avec succès !".format(i["Nom"]),"green"

                    connexionUserCo.commit()
                except AssertionError as er:
                    mess,colorMess="Vous ne pouvez pas offrir ce titre : {0}".format(er),"red"
                break
        
        for i in curseurUser.execute("SELECT * FROM titresUser").fetchall():
            if request.POST.get("vendre{0}".format(i["ID"]))=="Confirmer":
                try:
                    assert i["Rareté"] not in (0,4,5,6), "sa rareté vous empêche de le vendre !"
                    assert i["Nom"]!=infos["Titre"], "le titre que vous voulez vendre est celui qui est actuellement équipé pour vous."

                    if curseur.execute("SELECT * FROM marketplace WHERE ID={0}".format(i["ID"])).fetchone()==None:
                        curseur.execute("INSERT INTO marketplace VALUES({0},0,1)".format(i["ID"]))
                    curseur.execute("UPDATE marketplace SET Stock=Stock+1 WHERE ID={0}".format(i["ID"]))
                    curseurUser.execute("UPDATE coins SET Coins=Coins+{0}".format(dictSell[i["Rareté"]]))
                    curseurUser.execute("DELETE FROM titresUser WHERE ID={0}".format(i["ID"]))
                    coins+=dictSell[i["Rareté"]]
                    mess,colorMess="Titre {0} vendu avec succès !".format(i["Nom"]),"green"

                except AssertionError as er:
                    mess,colorMess="Vous ne pouvez pas vendre ce titre : {0}".format(er),"red"
                break

            if request.POST.get("set{0}".format(i["ID"]))=="Bien sûr !": 
                try:
                    assert curseurUser.execute("SELECT * FROM titresUser WHERE ID={0}".format(i["ID"])).fetchone(), "vous ne le possèdez pas."
                    if curseur.execute("SELECT * FROM active WHERE MembreID={0}".format(user)).fetchone()==None:
                        curseur.execute("INSERT INTO active VALUES({0},{1})".format(i["ID"],user))
                    else:
                        curseur.execute("UPDATE active SET TitreID={0} WHERE MembreID={1}".format(i["ID"],user))
                    mess,colorMess="Titre {0} équipé avec succès !".format(i["Nom"]),"green"
                    infos["Titre"]=i["Nom"]
                    if infos["Custom"]!=None:
                        infos["Full"]=infos["Custom"]+", "+infos["Titre"]

                except AssertionError as er:
                    mess,colorMess="Vous ne pouvez pas équiper ce titre : {0}".format(er),"red"
                break
        
        connexion.commit()
        connexionUser.commit()
    
    titresUser=curseurUser.execute("SELECT * FROM titresUser").fetchall()
    boutique=curseur.execute("SELECT marketplace.ID,marketplace.Stock,titres.Rareté,titres.Nom,marketplace.Known,titres.Description,titres.Collection FROM marketplace JOIN titres ON marketplace.ID=titres.ID ORDER BY Rareté DESC").fetchall()
    for i in titresUser:
        plus=curseur.execute("SELECT * FROM titres WHERE ID={0}".format(i["ID"])).fetchone()
        i["Description"]=plus["Description"]
        i["Collection"]=plus["Collection"]
    for i in boutique:
        if curseurUser.execute("SELECT * FROM titresUser WHERE ID={0}".format(i["ID"])).fetchone()!=None:
            i["Own"]=True
        else:
            i["Own"]=False

    ctx={"avatarprofil":user_avatar_profil,"idprofil":user,"nomprofil":user_name_profil,"guildscom":listeCom,
        "avatar":user_avatar,"id":request.user.id,"nom":user_name,
        "titre":infos["Full"],"color":infos["Couleur"],"emote":infos["Emote"],"custom":infos["Custom"],"coins":coins,"equip":infos["Titre"],
        "vip":infos["VIP"],"testeur":infos["Testeur"],
        "boutique":boutique,"titresUser":titresUser,"dictRarete":{0:"Spécial",1:"Basique",2:"Rare",3:"Légendaire",4:"Haut-Fait",5:"Unique",6:"Fabuleux"},"dictVente":{0:"♾️",1:150,2:300,3:500,4:"♾️",5:"♾️",6:"♾️"},"dictAchat":{0:"♾️",1:300,2:600,3:1000,4:"♾️",5:2500,6:"♾️"},
        "options":options,"dictOptions":{"home":"Accueil","titres":"Titres","custom":"Personnalisation","stats":"Stats"},"option":"titres",
        "mess":mess,"colormess":colorMess}

    return render(request, "companion/Profil/Titre.html", ctx)

@login_required(login_url="/login")
def viewProfilPerso(request,user):

    connexion,curseur=connectSQL("OT","Titres","Titres",None,None)
    connexionUser,curseurUser=connectSQL("OT",user,"Titres",None,None)
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    infos=getAllInfos(curseur,curseurUser,connexionUser,user)

    if user!=request.user.id:
        user_avatar_profil=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user)).fetchone()["Avatar"]
        user_name_profil=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user)).fetchone()["Nom"]
        user_avatar=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Avatar"]
        user_name=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Nom"]
        connexionUserCo,curseurUserCo=connectSQL("OT",request.user.id,"Titres",None,None)
        coins=curseurUserCo.execute("SELECT * FROM coins").fetchone()["Coins"]
    else:
        user_avatar=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Avatar"]
        user_name=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Nom"]
        user_avatar_profil=user_avatar
        user_name_profil=user_name
        coins=infos["Coins"]

    ctx={"avatarprofil":user_avatar_profil,"idprofil":user,"nomprofil":user_name_profil,
        "avatar":user_avatar,"id":request.user.id,"nom":user_name,
        "titre":infos["Full"],"color":infos["Couleur"],"emote":infos["Emote"],"custom":infos["Custom"],"coins":coins,"equip":infos["Titre"],
        "vip":infos["VIP"],"testeur":infos["Testeur"],
        "options":["home","titres","custom","stats"],"dictOptions":{"home":"Accueil","titres":"Titres","custom":"Personnalisation","stats":"Stats"},"option":"custom"}

    return render(request, "companion/Profil/Personnalisation.html", ctx)