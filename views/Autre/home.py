
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companion.Getteurs import getGuildInfo
from companion.outils import connectSQL, createPhrase, dictRefCommands, dictRefOptions, dictRefPlus, dictRefOptionsJeux, getGuilds

@login_required(login_url="/login")
def home(request):

    user=request.user
    mixalert=None

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    common=getGuilds(user,curseurGet)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    if len(common)==0:
        return render(request, "companion/homeNoGuild.html")

    connexionMix,curseurMix=connectSQL("OT","Mixes","Guild",None,None)
    
    if request.method=="POST":
        liste=[]
        for guild in common:
            if request.POST.get(str(guild["ID"]))=="on":
                liste.append(guild["ID"])
        if len(liste)>5 or len(liste)<2:
            mixalert=False
        else:
            liste+=["0" for i in range(5-len(liste))]
            mixalert=True
            curseurMix.execute("CREATE TABLE IF NOT EXISTS mixes_{0} (Nombre INT, Nom TEXT, Serveur1 BIGINT, Serveur2 BIGINT, Serveur3 BIGINT, Serveur4 BIGINT, Serveur5 BIGINT, PRIMARY KEY(Serveur1,Serveur2,Serveur3,Serveur4,Serveur5))".format(user.id))
            descip=",".join(liste)
            nb=curseurMix.execute("SELECT Count() AS Count FROM mixes_{0}".format(user.id)).fetchone()["Count"]
            nom=request.POST.get("name-mix")
            if nom=="":
                nom="Mix {0}".format(nb+1)
            else:
                nom=createPhrase([nom])
            try:
                curseurMix.execute("INSERT INTO mixes_{0} VALUES ({1},'{2}',{3})".format(user.id,nb+1,nom,descip))
            except Exception as er:
                mixalert=False
            connexionMix.commit()

    mixes_final=[]
    try:
        mixes=curseurMix.execute("SELECT * FROM mixes_{0}".format(user.id)).fetchall()
        for i in mixes:
            liste=[]
            for j in range(1,6):
                if i["Serveur{0}".format(j)]!=0:
                    infos=getGuildInfo(i["Serveur{0}".format(j)],curseurGet)
                    if infos==None:
                        curseurMix.execute("UPDATE mixes_{0} SET Serveur{1}=0 WHERE Nombre={2}".format(user.id,j,i["Nombre"]))
                    liste.append({"ID":i["Serveur{0}".format(j)],"Icon":infos["Icon"]})
            if liste!=[]:
                mixes_final.append({"Liste":liste.copy(),"Nom":i["Nom"],"ID":i["Nombre"]})
        connexionMix.commit()
    except:
        pass

    try:
        connexionPin,curseurPin=connectSQL("OT","Pin","Guild",None,None)
        pins=curseurPin.execute("SELECT * FROM pin_{0}".format(user.id)).fetchall()
        for i in pins:
            if i["Guild"][:5]=="mixes":
                mix=curseurMix.execute("SELECT * FROM mixes_{0} WHERE Nombre={1}".format(user.id,i["Guild"][6:])).fetchone()
                i["Nom"]="Mix {0}".format(mix["Nom"])
                i["Mix"]=True
            elif i["Guild"]=="jeux":
                i["Nom"]="Jeux"
            else:
                infos=getGuildInfo(i["Guild"],curseurGet)
                i["Nom"]=infos["Nom"]
                i["Icon"]=infos["Icon"]
    except:
        pins=None
    
    ctx={"guilds":common,"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"mixalert":mixalert,"mixes":mixes_final,
    "userpin":pins,"dictCommands":dictRefCommands,"dictOptions":dictRefOptions,"dictPlus":dictRefPlus,"dictOptionsJeux":dictRefOptionsJeux}
    return render(request, "companion/home.html", ctx)
