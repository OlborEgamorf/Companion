from companion.tools.Getteurs import getDivers
from companion.tools.outils import connectSQL
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


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
            
    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"rank":realStats,"ot":True,
        "options":["stats","titres","support"],"dictOptions":{"home":"Accueil","titres":"Titres","support":"Soutenir le projet","stats":"Stats"},"option":"stats"}

    return render(request, "companion/OT/Stats.html", ctx)
