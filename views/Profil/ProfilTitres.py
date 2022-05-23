from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companion.Getteurs import getAllInfos
from companion.outils import connectSQL, getCommon, getGuilds

@login_required(login_url="/login")
def viewProfilTitres(request,user):
    dictValue={1:300,2:600,3:1000,5:2500}
    dictSell={0:"Inestimable",1:150,2:300,3:500,4:"Inestimable",5:"Inestimable",6:"Inestimable"}

    connexion,curseur=connectSQL("OT","Titres","Titres",None,None)
    connexionUser,curseurUser=connectSQL("OT",user,"Titres",None,None)
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    infos=getAllInfos(curseur,curseurUser,connexionUser,user)

    if user!=request.user.id:
        user_avatar=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Avatar"]
        user_name=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Nom"]
        full_guilds=getGuilds(request.user,curseurGet)
        listeCom=getCommon(full_guilds,user,curseurGet)
        if len(listeCom)==0:
            user_avatar_profil=None
            user_name_profil=infos["Full"]
        else:
            user_avatar_profil=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user)).fetchone()["Avatar"]
            user_name_profil=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user)).fetchone()["Nom"]
        connexionUserCo,curseurUserCo=connectSQL("OT",request.user.id,"Titres",None,None)
        coins=curseurUserCo.execute("SELECT * FROM coins").fetchone()["Coins"]
        options=["home","titres"]
    else:
        user_avatar=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Avatar"]
        user_name=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Nom"]
        user_avatar_profil=user_avatar
        user_name_profil=user_name
        coins=infos["Coins"]
        options=["home","titres",]#"custom","stats"]
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
    
    titresUser=curseurUser.execute("SELECT * FROM titresUser ORDER BY Rareté ASC").fetchall()
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