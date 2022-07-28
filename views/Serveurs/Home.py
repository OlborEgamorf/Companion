from math import inf

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from companion.tools.outils import connectSQL



@login_required(login_url="/login")
def viewGuildHome(request,guild):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    try:
        hideblind=curseurGuild.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
        assert not hideblind["Blind"]
        assert not hideblind["Leave"]
        assert curseurGuild.execute("SELECT * FROM stats").fetchone()["Active"]
        stats=True
    except:
        stats=False

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "stats":stats,"outils":True,"sv":True,"polls":True,"admin":True,"anniv":True,"timeline":True,
    "travel":False,"selector":False}
    
    return render(request, "companion/GuildHome.html", ctx)