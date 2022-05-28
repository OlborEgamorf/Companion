import plotly.graph_objects as go
from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import getPin
from companion.tools.outils import (connectSQL, dictOptions, getMoisAnnee,
                              getTableDay, getTimes, listeOptions, tableauMois)
from companion.views.Serveurs.Stats.Evol.EvolGraph import xaxeEvol
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from plotly.offline import plot


@login_required(login_url="/login")
@CompanionStats
def graphJours(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    listeMois,listeAnnee=getTimes(guild,option,"Stats")

    div1=graphLineJours(curseur,moisDB,anneeDB)

    connexion.close()
    ctx={"fig":div1,"fig2":None,"fig3":None,"fig4":None,"fig5":None,"fig6":None,"fig7":None,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"pagestats":True,
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "command":"jours","options":listeOptions,"option":option,"plus":"graphs",
    "travel":True,"selector":True,"obj":None,
    "pin":getPin(user,curseurGet,guild,option,"jours","graphs")}
    return render(request, "companion/Stats/Graphiques.html", ctx)


@login_required(login_url="/login")
def iFrameGraphJours(request,guild,option):
    return render(request, "companion/Blank/Empty.html")



def graphLineJours(curseur,moisDB,anneeDB):
    table=getTableDay(curseur,tableauMois[moisDB],anneeDB)
    table.sort(key=lambda x:x["DateID"])

    listeLabels=list(map(lambda x:"20{0}-{1}-{2}".format(x["Annee"],x["Mois"],x["Jour"]),table))
    listeCount=list(map(lambda x:x["Count"], table))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=listeLabels, y=listeCount, text=listeCount, mode='lines', marker=dict(color="turquoise", size=12), line=dict(color="turquoise"), textposition="top center",hovertemplate = "%{y}",name="Jours"))

    fig.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Périodes - Messages",xaxis_title="Dates",yaxis_title="Messages",hovermode="x")
    fig.update_yaxes(automargin=True)
    xaxeEvol(moisDB,fig)

    return plot(fig,output_type='div')
