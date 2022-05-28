from companion.tools.outils import connectSQL
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
def viewOTTitres(request):
    user=request.user
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    connexion,curseur=connectSQL("OT","Titres","Titres",None,None)
    boutique=curseur.execute("SELECT marketplace.ID,marketplace.Stock,titres.Rareté,titres.Nom,marketplace.Known,titres.Description,titres.Collection FROM marketplace JOIN titres ON marketplace.ID=titres.ID ORDER BY Rareté DESC").fetchall()
    titres=curseur.execute("SELECT * FROM titres ORDER BY ID").fetchall()

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"ot":True,
        "boutique":boutique,"titresInfos":titres,"dictRarete":{0:"Spécial",1:"Basique",2:"Rare",3:"Légendaire",4:"Haut-Fait",5:"Unique",6:"Fabuleux"},"dictVente":{0:"♾️",1:150,2:300,3:500,4:"♾️",5:"♾️",6:"♾️"},"dictAchat":{0:"♾️",1:300,2:600,3:1000,4:"♾️",5:2500,6:"♾️"},
        "options":["stats","titres","support"],"dictOptions":{"home":"Accueil","titres":"Titres","support":"Soutenir le projet","stats":"Stats"},"option":"titres"}

    return render(request, "companion/OT/Titres.html", ctx)
