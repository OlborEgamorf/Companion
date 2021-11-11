
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..outils import avatarAnim

from discord_login.views import refresh

@login_required(login_url="/login")
def home(request):
    user=request.user

    bot_guilds=requests.get("https://discord.com/api/v9/users/@me/guilds",headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})
    bguild_json=bot_guilds.json()
    bot_ids=list(map(lambda x:x["id"], bguild_json))

    user_avatar=requests.get("https://discord.com/api/v9/users/@me",headers={"Authorization":"Bearer {0}".format(user.token)})
    if user_avatar.status_code==401:
        user.token=refresh(user.refresh)
        return home(request)
    user_avatar=user_avatar.json()
    
    user_avatar=user_avatar["avatar"]

    user_guild=requests.get("https://discord.com/api/v9/users/@me/guilds",headers={"Authorization":"Bearer {0}".format(user.token)})
    uguild_json=user_guild.json()

    common=list(filter(lambda x: x["id"] in bot_ids, uguild_json))
    final_guilds=[]

    for guild in common:
        if guild["icon"]!=None:
            end=avatarAnim(guild["icon"][0:2])
        final_guilds.append({"ID":guild["id"],"Nom":guild["name"],"Icon":guild["icon"],"Anim":end})

    final_guilds.sort(key=lambda x:x["Nom"])
    
    ctx={"guilds":final_guilds,"avatar":user_avatar,"id":user.id,"anim":avatarAnim(user_avatar)}
    return render(request, "companion/home.html", ctx)
