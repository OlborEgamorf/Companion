from random import randint
from time import strftime
from companion.tools.Getteurs import *
from companion.tools.outils import (connectSQL, createPhrase, static)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect


@login_required(login_url="/login")
def viewSVRandom(request,guild):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    pin=getPin(user,curseurGet,guild,"poll","ranks","")
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)

    aleatoire=curseurGuild.execute("SELECT * FROM savezvous ORDER BY RANDOM() LIMIT 1").fetchone()
    if aleatoire!=None:
        
        if aleatoire["Image"]!="None" and aleatoire["Image"].startswith("static"):
            aleatoire["Image"]="/static/companion/sv/{0}".format(aleatoire["Image"][7:])
        
        auteur=getUserInfo(aleatoire["ID"],curseurGet,guild)
    else:
        auteur=None

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "command":"sv","option":"sv","plus":"",
    "travel":False,"selector":True,"obj":None,"pagesv":True,
    "pin":pin,"aleatoire":aleatoire,"auteur":auteur}
    
    return render(request, "companion/SV/Random.html", ctx)

@login_required(login_url="/login")
def viewAddSV(request,guild):
    user=request.user
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    pin=getPin(user,curseurGet,guild,"poll","ranks","")
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "command":"svadd","option":"sv","plus":"",
    "travel":False,"selector":True,"obj":None,"pagesv":True,
    "pin":pin}
    
    return render(request, "companion/SV/Add.html", ctx)

@login_required(login_url="/login")
def viewPersoSV(request,guild):
    user=request.user
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    pin=getPin(user,curseurGet,guild,"poll","ranks","")
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    perso=curseurGuild.execute("SELECT * FROM savezvous WHERE ID={0}".format(user.id)).fetchall()
    for i in perso:
        if i["Image"]!="None" and i["Image"].startswith("static"):
            i["Image"]="/static/companion/sv/{0}".format(i["Image"][7:])
    auteur=getUserInfo(user.id,curseurGet,guild)

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "command":"svperso","option":"sv","plus":"","perso":perso,"auteur":auteur,
    "travel":False,"selector":True,"obj":None,"pagesv":True,
    "pin":pin}

    return render(request, "companion/SV/Perso.html", ctx)

@login_required(login_url="/login")
def viewModoSV(request,guild):
    user=request.user
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    pin=getPin(user,curseurGet,guild,"poll","ranks","")
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    all=curseurGuild.execute("SELECT * FROM savezvous ORDER BY Count ASC".format(user.id)).fetchall()
    for i in all:
        if i["Image"]!="None" and i["Image"].startswith("static"):
            i["Image"]="/static/companion/sv/{0}".format(i["Image"][7:])
        infos=getUserInfo(i["ID"],curseurGet,guild)
        i["Avatar"]=infos["Avatar"]
        i["Nom"]=infos["Nom"]
        i["Color"]=infos["Color"]

    auteur=getUserInfo(user.id,curseurGet,guild)

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "command":"svmodo","option":"sv","plus":"","all":all,"auteur":auteur,
    "travel":False,"selector":True,"obj":None,"pagesv":True,
    "pin":pin}

    return render(request, "companion/SV/Modo.html", ctx)


def addSV(request,guild):
    user=request.user
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    count=curseurGuild.execute("SELECT MAX(Count) AS Max FROM savezvous").fetchone()
    if count==None:
        count=0
    else:
        count=count["Max"]

    sv=request.POST.get("sv")

    source=request.POST.get("source")
    if source=="":
        source=None
    else:
        source=createPhrase(source)

    if len(request.FILES)!=0:
        image=request.FILES["image"]
        filename=str(count)+str(randint(1,10000))+image.name
        with open(static+"/sv/"+filename, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        filesv="static "+filename
    else:
        filesv=None
    
    assert len(sv)>1 and len(sv)<2000
    sv=createPhrase(sv)
    
    curseurGuild.execute("INSERT INTO savezvous VALUES('{0}',{1},'{2}',{3},'{4}')".format(sv,user.id,filesv,count+1,source))
    connexionGuild.commit()

    return redirect("/companion/{0}/sv/perso".format(guild))

def editSV(request,guild,idsv):
    user=request.user
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    phrase=curseurGuild.execute("SELECT * FROM savezvous WHERE Count={0}".format(idsv)).fetchone()
    assert phrase!=None, "Le numéro donné ne correspond à aucune phrase."

    if request.POST.get("del")!=None:
        assert user.id==phrase["ID"]
        curseurGuild.execute("DELETE FROM savezvous WHERE Count={0}".format(idsv))
    elif request.POST.get("edit")!=None:
        assert user.id==phrase["ID"]
        newphrase=request.POST.get("sv")
        newsource=request.POST.get("source")
        if newsource=="":
            newsource=None
        curseurGuild.execute("UPDATE savezvous SET Texte='{0}', Source='{1}' WHERE Count={2}".format(newphrase,newsource,idsv))
    else:
        for i in curseurGuild.execute("SELECT * FROM svcomment WHERE Count={0}".format(idsv)).fetchall():
            if request.POST.get("del-{0}".format(i["ID"]))!=None:
                curseurGuild.execute("DELETE FROM svcomment WHERE Count={0} AND ID={1}".format(idsv,i["ID"]))
    
    connexionGuild.commit()
    return redirect("/companion{0}".format(request.META["HTTP_REFERER"].split("companion")[1]))