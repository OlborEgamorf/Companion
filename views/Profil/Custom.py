from companion.tools.Getteurs import getAllInfos
from companion.tools.outils import connectSQL, createPhrase, getGuilds
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
def viewProfilPerso(request,user):

    connexion,curseur=connectSQL("OT","Titres","Titres",None,None)
    connexionUser,curseurUser=connectSQL("OT",user,"Titres",None,None)
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    infos=getAllInfos(curseur,curseurUser,connexionUser,user)

    if user!=request.user.id:
        raise AssertionError("Grosse bite")
    
    userProfil=request.user

    user_avatar=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Avatar"]
    user_name=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(request.user.id)).fetchone()["Nom"]
    user_avatar_profil=user_avatar
    user_name_profil=user_name
    coins=infos["Coins"]
    if request.method=="POST":
        assert curseur.execute("SELECT * FROM custombans WHERE ID={0}".format(userProfil.id)).fetchone()==None, "Vous êtes banni des outils de personnalisation."
        surnom,emote,color,phrase,fond=request.POST.get("surnom"),request.POST.get("emote"),request.POST.get("color"),request.POST.get("phrase"),request.POST.get("fond")
        print(fond)
        if surnom!=None and surnom!=infos["Custom"]:
            assert coins>=1500, "Vous n'avez pas assez d'OT Coins !"
            assert len(surnom)<=8, "Le surnom que vous avez donné est trop long !"
            if curseur.execute("SELECT * FROM custom WHERE ID={0}".format(userProfil.id)).fetchone()==None:
                curseur.execute("INSERT INTO custom VALUES({0},'{1}')".format(userProfil.id,createPhrase(surnom)))
            else:
                curseur.execute("UPDATE custom SET Custom='{0}' WHERE ID={1}".format(surnom,userProfil.id))
            curseurUser.execute("UPDATE coins SET Coins=Coins-{0}".format(1500))
            infos["Custom"]=surnom
            infos["Full"]=surnom+", "+infos["Titre"]
            coins-=1500
        
        if emote!=None:
            assert coins>=50, "Vous n'avez pas assez d'OT Coins !"
            fullemote=curseurGet.execute("SELECT * FROM emotes WHERE ID={0}".format(emote)).fetchone()
            assert fullemote!=None, "Je ne connais pas cette emote."
            if curseur.execute("SELECT * FROM emotes WHERE ID={0}".format(userProfil.id)).fetchone()==None:
                curseur.execute("INSERT INTO emotes VALUES({0},'{1}',{2})".format(userProfil.id,fullemote["Nom"],emote))
            else:
                curseur.execute("UPDATE emotes SET Nom='{0}', IDEmote={1} WHERE ID={2}".format(fullemote["Full"],emote,userProfil.id))
            curseurUser.execute("UPDATE coins SET Coins=Coins-{0}".format(50))
            infos["Emote"]=emote

        if color!=None and color!=infos["Color"]:
            assert coins>=50, "Vous n'avez pas assez d'OT Coins !"
            r,g,b=tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
            if curseur.execute("SELECT * FROM couleurs WHERE ID={0}".format(userProfil.id)).fetchone()==None:
                curseur.execute("INSERT INTO couleurs VALUES({0},{1},{2},{3})".format(userProfil.id,r,g,b))
            else:
                curseur.execute("UPDATE couleurs SET R={0}, G={1}, B={2} WHERE ID={3}".format(r,g,b,userProfil.id))
            curseurUser.execute("UPDATE coins SET Coins=Coins-{0}".format(50))
            infos["Color"]=color

        if phrase!=None and phrase!=infos["Phrase"]:
            assert coins>=50, "Vous n'avez pas assez d'OT Coins !"
            assert len(phrase)<=35, "Votre phrase ne doit pas dépasser les 35 caractères !"
            if curseur.execute("SELECT * FROM cartes WHERE ID={0}".format(userProfil.id)).fetchone()==None:
                curseur.execute("INSERT INTO cartes VALUES({0},'defaut','{1}')".format(userProfil.id,createPhrase(phrase)))
            else:
                curseur.execute("UPDATE cartes SET Texte='{0}' WHERE ID={1}".format(createPhrase(phrase),userProfil.id))
            curseurUser.execute("UPDATE coins SET Coins=Coins-{0}".format(50))
            infos["Phrase"]=phrase

        if fond!=None and fond!=infos["Fond"]:
            assert coins>=250, "Vous n'avez pas assez d'OT Coins !"
            if curseur.execute("SELECT * FROM cartes WHERE ID={0}".format(userProfil.id)).fetchone()==None:
                curseur.execute("INSERT INTO cartes VALUES({0},'{1}','None')".format(userProfil.id,fond))
            else:
                curseur.execute("UPDATE cartes SET Fond='{0}' WHERE ID={1}".format(fond,userProfil.id))
            curseurUser.execute("UPDATE coins SET Coins=Coins-{0}".format(250))
            infos["Fond"]=fond

        connexion.commit()
        connexionUser.commit()

    full_guilds=getGuilds(request.user,curseurGet)
    listeEmotes=[]
    for i in full_guilds:
        listeEmotes+=curseurGet.execute("SELECT * FROM emotes WHERE GuildID={0}".format(i["ID"])).fetchall()
    listeEmotes.sort(key=lambda x:x["Nom"])

    listeFonds=curseur.execute("SELECT * FROM fonds").fetchall()

    ctx={"avatarprofil":user_avatar_profil,"idprofil":user,"nomprofil":user_name_profil,"profil":True,
        "avatar":user_avatar,"id":request.user.id,"nom":user_name,"guildname":user_name_profil,
        "titre":infos["Full"],"color":infos["Color"],"emote":infos["Emote"],"custom":infos["Custom"],"coins":coins,"equip":infos["Titre"],
        "vip":infos["VIP"],"testeur":infos["Testeur"],"listeEmotes":listeEmotes,"phrase":infos["Phrase"],"fond":infos["Fond"],"listeFonds":listeFonds,
        "options":["home","titres","custom","stats"],"dictOptions":{"home":"Accueil","titres":"Titres","custom":"Personnalisation","stats":"Stats"},"option":"custom"}

    return render(request, "companion/Profil/Personnalisation.html", ctx)
