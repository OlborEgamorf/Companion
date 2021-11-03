from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..outils import collapseEvol, colorRoles, connectSQL, getGuild, getMoisAnnee, getUser, tableauMois, listeAnnee, listeMois


@login_required(login_url="/login")
def iFrameEvol(request,guild):
    all=request.GET.get("data")
    mois,annee,id=all.split("?")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user
    if id==None:
        id=user.id

    guild_full=getGuild(guild)

    user_full=getUser(guild,id)
    
    roles_position,roles_color,roles_name=colorRoles(guild_full)
    
    connexion,curseur=connectSQL(guild,"Messages","Stats",tableauMois[moisDB],anneeDB)

    table=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,id)).fetchall()
    table=collapseEvol(table)


    user_full["roles"].sort(key=lambda x:roles_position[x], reverse=True)
    if len(user_full["roles"])==0:
        color=None
    else:
        color="#{0}".format(hex(roles_color[user_full["roles"][0]])[2:])

    maxi=max(list(map(lambda x:x["Count"],table)))

    ctx={"rank":table,"id":user.id,"color":color,"max":maxi,"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,"nom":user_full["user"]["username"]}
    connexion.close()
    return render(request,"companion/evolIFrame.html",ctx)