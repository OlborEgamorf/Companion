from companion.Getteurs import getAllInfos
from companion.outils import connectSQL
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


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
