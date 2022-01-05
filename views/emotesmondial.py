from math import inf
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..outils import avatarAnim, connectSQL, getGuild, getMoisAnnee, getUser, tableauMois,getGuilds


@login_required(login_url="/login")
def emotesMondial(request):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user
    guilds=getGuilds(user)
    if len(guilds)==0:
        pass # FAIRE CAS OU PAS DE GUILD EN COMMUN
    user_full=getUser(guilds[0]["ID"],user.id)
    user_avatar=user_full["user"]["avatar"]
    connexion,curseur=connectSQL("OT","Emotes","Stats","GL","")
    liste=[]
    for i in guilds:
        emotes=curseur.execute("SELECT * FROM glob WHERE IDGuild={0}".format(i["ID"])).fetchall()
        for j in emotes:
            j["Icon"]=i["Icon"]
        liste+=emotes
        
    liste.sort(key=lambda x:x["Rank"])
    maxi=liste[0]["Count"]
    ctx={"rank":liste,"avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar),"max":maxi,"mois":mois,"annee":annee,"guilds":getGuilds(user),"type":"Classements","categs":None,"hrefs":[],"sections":["Jeux","Emotes"],"section":"Emotes","guildid":0,"guildname":"Mondial","selector":False}
    return render(request, "companion/EmotesWW/emotesmondial.html", ctx)


@login_required(login_url="/login")
def iframeEmotes(request,emote):
    all=request.GET.get("data")
    mois,annee=all.split("?")

    if annee not in ("GL","Global"):
        annee="20"+annee
    mois,annee,moisDB,anneeDB=getMoisAnnee(tableauMois[mois],annee)
    user=request.user

    connexion,curseur=connectSQL("OT","Emotes","Stats","GL","")
    liste=[]
    guilds=getGuilds(user)
    guilds_id=list(map(lambda x:x["ID"],guilds))
    maxi=-inf
    for i in curseur.execute("SELECT * FROM glob_emote{0} ORDER BY Rank ASC".format(emote)).fetchall():
        if i["ID"] in guilds_id:
            guild=getGuild(i["ID"])
            liste.append({"Rank":i["Rank"],"Count":i["Count"],"Icon":guild["icon"],"ID":i["ID"],"Nom":guild["name"]})
        else:
            liste.append({"Rank":i["Rank"],"Count":i["Count"],"Icon":False,"ID":False,"Nom":"Autre serveur"})
        maxi=max(maxi,i["Count"])

    ctx={"rank":liste,"id":user.id,"max":maxi,"mois":mois,"annee":annee}
    return render(request, "companion/EmotesWW/iFrameEmotesWW.html", ctx)

