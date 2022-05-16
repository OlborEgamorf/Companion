
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..Getteurs import getGuildInfo
from ..outils import connectSQL, createPhrase

@login_required(login_url="/login")
def home(request):

    user=request.user
    mixalert=None

    bot_guilds=requests.get("https://discord.com/api/v9/users/@me/guilds",headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})
    bguild_json=bot_guilds.json()
    bot_ids=list(map(lambda x:x["id"], bguild_json))

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    user_guild=requests.get("https://discord.com/api/v9/users/@me/guilds",headers={"Authorization":"Bearer {0}".format(user.token)})
    uguild_json=user_guild.json()

    common=list(filter(lambda x: x["id"] in bot_ids, uguild_json))

    if len(common)==0:
        return render(request, "companion/homeNoGuild.html")

    final_guilds=[]
    connexion,curseur=connectSQL("OT","Mixes","Guild",None,None)
    
    if request.method=="POST":
        liste=[]
        for guild in common:
            final_guilds.append({"ID":guild["id"],"Nom":guild["name"],"Icon":guild["icon"]})
            if request.POST.get(str(guild["id"]))=="on":
                liste.append(guild["id"])
        if len(liste)>5 or len(liste)<2:
            mixalert=False
        else:
            liste+=["0" for i in range(5-len(liste))]
            mixalert=True
            curseur.execute("CREATE TABLE IF NOT EXISTS mixes_{0} (Nombre INT, Nom TEXT, Serveur1 BIGINT, Serveur2 BIGINT, Serveur3 BIGINT, Serveur4 BIGINT, Serveur5 BIGINT, PRIMARY KEY(Serveur1,Serveur2,Serveur3,Serveur4,Serveur5))".format(user.id))
            descip=",".join(liste)
            nb=curseur.execute("SELECT Count() AS Count FROM mixes_{0}".format(user.id)).fetchone()["Count"]
            nom=request.POST.get("name-mix")
            if nom=="":
                nom="Mix {0}".format(nb+1)
            else:
                nom=createPhrase([nom])
            try:
                curseur.execute("INSERT INTO mixes_{0} VALUES ({1},'{2}',{3})".format(user.id,nb+1,nom,descip))
            except Exception as er:
                mixalert=False
            connexion.commit()

    else:
        for guild in common:
            final_guilds.append({"ID":guild["id"],"Nom":guild["name"],"Icon":guild["icon"]})

    mixes_final=[]
    try:
        mixes=curseur.execute("SELECT * FROM mixes_{0}".format(user.id)).fetchall()
        for i in mixes:
            liste=[]
            for j in range(1,6):
                if i["Serveur{0}".format(j)]!=0:
                    liste.append({"ID":i["Serveur{0}".format(j)],"Icon":getGuildInfo(i["Serveur{0}".format(j)],curseurGet)["Icon"]})
            mixes_final.append({"Liste":liste.copy(),"Nom":i["Nom"],"ID":i["Nombre"]})
    except:
        pass

    final_guilds.sort(key=lambda x:x["Nom"])
    
    ctx={"guilds":final_guilds,"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"mixalert":mixalert,"mixes":mixes_final}
    return render(request, "companion/home.html", ctx)

#print(request.POST.get(str(guild["id"])))