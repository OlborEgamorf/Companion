from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companion.Getteurs import getAllInfos, getDivers
from companion.outils import connectSQL, getCommon, getGuilds

@login_required(login_url="/login")
def viewOTTitres(request):
    user=request.user
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    connexion,curseur=connectSQL("OT","Titres","Titres",None,None)
    boutique=curseur.execute("SELECT marketplace.ID,marketplace.Stock,titres.Rareté,titres.Nom,marketplace.Known,titres.Description,titres.Collection FROM marketplace JOIN titres ON marketplace.ID=titres.ID ORDER BY Rareté DESC").fetchall()
    titres=curseur.execute("SELECT * FROM titres ORDER BY ID").fetchall()

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "boutique":boutique,"titresInfos":titres,"dictRarete":{0:"Spécial",1:"Basique",2:"Rare",3:"Légendaire",4:"Haut-Fait",5:"Unique",6:"Fabuleux"},"dictVente":{0:"♾️",1:150,2:300,3:500,4:"♾️",5:"♾️",6:"♾️"},"dictAchat":{0:"♾️",1:300,2:600,3:1000,4:"♾️",5:2500,6:"♾️"},
        "options":["stats","titres","support"],"dictOptions":{"home":"Accueil","titres":"Titres","support":"Soutenir le projet","stats":"Stats"},"option":"titres"}

    return render(request, "companion/OT/Titres.html", ctx)


@login_required(login_url="/login")
def viewOTStats(request):
    user=request.user
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    bot_guilds=curseurGet.execute("SELECT ID FROM guilds").fetchall()
    stats=[]
    for guild in bot_guilds:
        try:
            connexion,curseur=connectSQL(guild["ID"],"Divers","Stats","GL","")
            for i in curseur.execute("SELECT * FROM glob ORDER BY Rank ASC").fetchall():
                it=0
                while it<len(stats) and it!=-1:
                    if stats[it]["ID"]==i["ID"]:
                        stats[it]["Count"]+=i["Count"]
                        it=-1
                    else:
                        it+=1
                if it!=-1:
                    stats.append(i)
        except:
            pass

    assert stats!=[]
    stats.sort(key=lambda x:x["Count"],reverse=True)

    realStats=[]
    realStats.append({"Count":curseurGet.execute("SELECT Count() AS Count FROM guilds").fetchone()["Count"],"Rank":0,"Nom":"Nombre de serveurs","ID":0})
    realStats.append({"Count":curseurGet.execute("SELECT Count() AS Count FROM users").fetchone()["Count"],"Rank":0,"Nom":"Nombre d'utilisateurs","ID":0})

    for i in stats:
        realStats.append(getDivers(i))
            
    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"rank":realStats,
        "options":["stats","titres","support"],"dictOptions":{"home":"Accueil","titres":"Titres","support":"Soutenir le projet","stats":"Stats"},"option":"stats"}

    return render(request, "companion/OT/Stats.html", ctx)


@login_required(login_url="/login")
def viewOTSupport(request):
    user=request.user
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "options":["stats","titres","support"],"dictOptions":{"home":"Accueil","titres":"Titres","support":"Soutenir le projet","stats":"Stats"},"option":"support"}

    return render(request, "companion/OT/Support.html", ctx)