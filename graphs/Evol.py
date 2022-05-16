import plotly.graph_objects as go
from companion.Getteurs import getUserInfo
from companion.outils import connectSQL, getTablePerso,dictOptions,tableauMois
from plotly.offline import plot

def graphLineEvol(guild,option,curseur,curseurGet,user,moisDB,anneeDB):
    infosUser=getUserInfo(user.id,curseurGet,guild)
    table=curseur.execute("SELECT * FROM evol{0}{1}{2} ORDER BY DateID ASC".format(moisDB,anneeDB,user.id)).fetchall()
    listeRanks=list(map(lambda x:x["Rank"], table))
    listeLabels=list(map(lambda x:"20{0}-{1}-{2}".format(x["Annee"],x["Mois"],x["Jour"]),table))
    listeCountBase=list(map(lambda x:x["Count"], table))
    rank=table[-1]["Rank"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=listeLabels, y=listeCountBase, mode='lines', line=dict(color="#"+hex(infosUser["Color"])[2:],width=3)))
    fig.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Evolution",xaxis_title="Dates",                  yaxis_title="Messages",hovermode="x")
    fig.update_yaxes(automargin=True)
    xaxeEvol(moisDB,fig)


    figRank = go.Figure()
    figRank.add_trace(go.Scatter(x=listeLabels, y=listeRanks, mode='lines', line=dict(color="#"+hex(infosUser["Color"])[2:],width=3.5)))
    figRank.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Evolution",xaxis_title="Dates",yaxis_title="Rang",hovermode="x")
    figRank.update_yaxes(automargin=True,autorange="reversed")
    xaxeEvol(moisDB,figRank)


    figAutour = go.Figure()
    figAutour.add_trace(go.Scatter(x=listeLabels, y=listeCountBase, mode='lines', name=infosUser["Nom"], line=dict(color="#"+hex(infosUser["Color"])[2:],width=3.5)))
    for i in curseur.execute("SELECT * FROM {0}{1} WHERE Rank>={2} AND Rank<={3} AND ID<>{4}".format(moisDB,anneeDB,rank-2,rank+2,user.id)).fetchall():
        evol=curseur.execute("SELECT * FROM evol{0}{1}{2} ORDER BY DateID ASC".format(moisDB,anneeDB,i["ID"])).fetchall()
        infos=getUserInfo(i["ID"],curseurGet,guild)
        hexa=hex(infos["Color"])[2:]
        if len(hexa)==6:
            hexa="#"+hexa
        else:
            hexa="#0"+hexa
        listeLabels=list(map(lambda x:"20{0}-{1}-{2}".format(x["Annee"],x["Mois"],x["Jour"]),evol))
        listeCount=list(map(lambda x:x["Count"], evol))
        figAutour.add_trace(go.Scatter(x=listeLabels, y=listeCount, mode='lines', name=infos["Nom"], line=dict(color=hexa)))

    figAutour.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Evolution",xaxis_title="Dates",yaxis_title="Messages",hovermode="x unified")
    figAutour.update_yaxes(automargin=True)
    xaxeEvol(moisDB,figAutour)

    figAvAp = go.Figure()
    if moisDB!="glob":
        if moisDB=="to":
            perso=getTablePerso(guild,dictOptions[option],user.id,False,"A","periodAsc")
        else:
            perso=getTablePerso(guild,dictOptions[option],user.id,False,"M","periodAsc")

        i=0
        while perso[i]["Mois"]!=tableauMois[moisDB] or perso[i]["Annee"]!=anneeDB:
            i+=1

        if i!=0:
            connexionAvAp,curseurAvAp=connectSQL(guild,dictOptions[option],"Stats",perso[i-1]["Mois"],perso[i-1]["Annee"])
            avant=curseurAvAp.execute("SELECT * FROM evol{0}{1}{2} ORDER BY DateID ASC".format(tableauMois[perso[i-1]["Mois"]].lower(),perso[i-1]["Annee"],user.id)).fetchall()
            if moisDB=="to":
                listeLabels=list(map(lambda x:"{0}/{1}".format(x["Jour"],x["Mois"]),avant))
            else:
                listeLabels=list(map(lambda x:"{0}".format(x["Jour"]),avant))
            listeCount=list(map(lambda x:x["Count"], avant))
            figAvAp.add_trace(go.Scatter(x=listeLabels, y=listeCount, mode='lines', name="{0}/{1}<br>Période précedente".format(perso[i-1]["Mois"],perso[i-1]["Annee"]), line=dict(color="turquoise")))
        
        if moisDB=="to":
            listeLabels=list(map(lambda x:"{0}/{1}".format(x["Jour"],x["Mois"]),table))
        else:
            listeLabels=list(map(lambda x:"{0}".format(x["Jour"]),table))
        figAvAp.add_trace(go.Scatter(x=listeLabels, y=listeCountBase, mode='lines', name="{0}/{1}<br>Maintenant".format(tableauMois[moisDB],anneeDB), line=dict(color="#"+hex(infosUser["Color"])[2:],width=3.5)))

        if i!=len(perso)-1:
            connexionAvAp,curseurAvAp=connectSQL(guild,dictOptions[option],"Stats",perso[i+1]["Mois"],perso[i+1]["Annee"])
            apres=curseurAvAp.execute("SELECT * FROM evol{0}{1}{2} ORDER BY DateID ASC".format(tableauMois[perso[i+1]["Mois"]],perso[i+1]["Annee"],user.id)).fetchall()
            if moisDB=="to":
                listeLabels=list(map(lambda x:"{0}/{1}".format(x["Jour"],x["Mois"]),apres))
            else:
                listeLabels=list(map(lambda x:"{0}".format(x["Jour"]),apres))
            listeCount=list(map(lambda x:x["Count"], apres))
            figAvAp.add_trace(go.Scatter(x=listeLabels, y=listeCount, mode='lines', name="{0}/{1}<br>Période suivante".format(perso[i+1]["Mois"],perso[i+1]["Annee"]), line=dict(color="gold")))
        
        figAvAp.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Evolution",xaxis_title="Dates",yaxis_title="Messages",hovermode="x unified")
        figAvAp.update_yaxes(automargin=True)
        figAvAp.update_xaxes(showgrid=False, zeroline=False,rangeslider_visible=True,rangeselector=dict(font_color="#111"))
        #xaxeEvol(moisDB,figAvAp)  
    if moisDB!="glob":
        return plot(fig,output_type='div'),plot(figRank,output_type='div'),plot(figAutour,output_type='div'),plot(figAvAp,output_type='div')
    else:
        return plot(fig,output_type='div'),plot(figRank,output_type='div'),plot(figAutour,output_type='div'),None

def xaxeEvol(moisDB,fig):
    if moisDB=="glob":
        fig.update_xaxes(showgrid=False, zeroline=False,rangeslider_visible=True,type="date",rangeselector=dict(font_color="#111",
        buttons=list([
            dict(count=3,label="3 mois",step="month",stepmode="backward"),
            dict(count=6,label="6 mois",step="month",stepmode="backward"),
            dict(count=1,label="1 an",step="year",stepmode="backward"),
            dict(count=2,label="2 ans",step="year",stepmode="backward"),
            dict(label="Tout",step="all")])))
    elif moisDB=="to":
        fig.update_xaxes(showgrid=False, zeroline=False,rangeslider_visible=True,type="date",rangeselector=dict(font_color="#111",
        buttons=list([
            dict(count=1,label="1 mois",step="month",stepmode="backward"),
            dict(count=2,label="2 mois",step="month",stepmode="backward"),
            dict(count=3,label="3 mois",step="month",stepmode="backward"),
            dict(count=6,label="6 mois",step="month",stepmode="backward"),
            dict(label="Tout",step="all")])))
    else:
        fig.update_xaxes(showgrid=False, zeroline=False,rangeslider_visible=True,type="date",rangeselector=dict(font_color="#111",
        buttons=list([
            dict(count=7,label="7 jours",step="day",stepmode="backward"),
            dict(count=10,label="10 jours",step="day",stepmode="backward"),
            dict(count=15,label="15 jours",step="day",stepmode="backward"),
            dict(count=20,label="20 jours",step="day",stepmode="backward"),
            dict(label="Tout",step="all")])))
