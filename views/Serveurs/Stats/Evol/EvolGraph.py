import plotly.graph_objects as go
from companion.templatetags.TagsCustom import enteteCount, enteteNom
from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import (getChannels, getEmoteTable, getFreq,
                                      getNom, getPin, getUserInfo)
from companion.tools.outils import (collapseEvol, connectSQL, dictOptions,
                                    getMoisAnnee, getTablePerso, getTimes,
                                    listeOptions, tableauMois, voiceAxe)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from plotly.offline import plot


@login_required(login_url="/login")
@CompanionStats
def graphEvol(request,guild,option):
    mois,annee,obj = request.GET.get("mois"),request.GET.get("annee"),request.GET.get("obj")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    listeMois,listeAnnee=getTimes(guild,option,"Stats")

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")
    listeObj=curseur.execute("SELECT * FROM glob ORDER BY Count DESC").fetchall()
    if option in ("emotes","reactions"):
        listeObj=list(map(lambda x:getEmoteTable(x,curseurGet),listeObj))
    elif option in ("salons","voicechan"):
        listeObj=list(map(lambda x:getChannels(x,curseurGet),listeObj))
    elif option=="freq":
        listeObj=list(map(lambda x:getFreq(x),listeObj))
    else:
        listeObj=None

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
    if option not in ("messages","voice","mots"):
        if obj==None:
            obj=listeObj[0]["ID"]

        if len(listeObj)>150:
            listeObj=listeObj[:150]

        div1,div2,div3,div4=linePlots(guild,option,curseur,curseurGet,obj,moisDB,anneeDB,False)
    else:
        div1,div2,div3,div4=linePlots(guild,option,curseur,curseurGet,user.id,moisDB,anneeDB,False)

    connexion.close()
    ctx={"fig":div1,"fig2":div2,"fig3":div3,"fig4":div4,"fig5":None,"fig6":None,"fig7":None,
    "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
    "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
    "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "command":"evol","options":listeOptions,"option":option,"plus":"graphs",
    "travel":True,"selector":True,"obj":obj,"listeObjs":listeObj,"pagestats":True,
    "pin":getPin(user,curseurGet,guild,option,"evol","graphs")}
    return render(request, "companion/Stats/Graphiques.html", ctx)


@login_required(login_url="/login")
def iFrameGraphEvol(request,guild,option):
    all=request.GET.get("data")
    mois,annee,obj=all.split("?")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user
    if obj=="None":
        obj=user.id
    
    categ="Stats"

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)

    table=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,obj)).fetchall()
    table=collapseEvol(table)  
    table.reverse() 
    table=list(filter(lambda x:not x["Collapse"],table))
    maxi=max(list(map(lambda x:x["Count"],table)))

    ctx={"rank":table,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"option":option,"plus":"graph"}
    return render(request, "companion/Stats/Ranks/iFrameRanks_evol.html", ctx)


def linePlots(guild,option,curseur,curseurGet,user,moisDB,anneeDB,recap):
    if option in ("messages","voice","mots"):
        infosUser=getUserInfo(user,curseurGet,guild)
        hexa=hex(infosUser["Color"])[2:]
        if len(hexa)==6:
            infosUser["Color"]="#"+hexa
        else:
            infosUser["Color"]="#"+"0"*(6-len(hexa))+hexa
    else:
        nom=getNom(user,option,curseurGet,False)
        infosUser={"Color":"turquoise","Nom":nom}

    table=curseur.execute("SELECT * FROM evol{0}{1}{2} ORDER BY DateID ASC".format(moisDB,anneeDB,user)).fetchall()
    listeRanks=list(map(lambda x:x["Rank"], table))
    listeLabels=list(map(lambda x:"20{0}-{1}-{2}".format(x["Annee"],x["Mois"],x["Jour"]),table))
    listeCountBase=list(map(lambda x:x["Count"], table))
    rank=table[-1]["Rank"]

    plus,div=voiceAxe(option,listeCountBase)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=listeLabels, y=listeCountBase, mode='lines', line=dict(color=infosUser["Color"],width=3)))
    fig.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Évolution {0} sur toute la période".format(enteteCount(option).lower()),xaxis_title="Date",yaxis_title=enteteCount(option)+plus,hovermode="x")
    fig.update_yaxes(automargin=True)
    xaxeEvol(moisDB,fig)

    if recap:
        return plot(fig,output_type='div')


    figRank = go.Figure()
    figRank.add_trace(go.Scatter(x=listeLabels, y=listeRanks, mode='lines', line=dict(color=infosUser["Color"],width=3.5)))
    figRank.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Évolution du rang dans le classement sur toute la période",xaxis_title="Date",yaxis_title="Rang",hovermode="x")
    figRank.update_yaxes(automargin=True,autorange="reversed")
    xaxeEvol(moisDB,figRank)


    figAutour = go.Figure()
    figAutour.add_trace(go.Scatter(x=listeLabels, y=listeCountBase, mode='lines', name=infosUser["Nom"], line=dict(color=infosUser["Color"],width=3.5)))
    for i in curseur.execute("SELECT * FROM {0}{1} WHERE Rank>={2} AND Rank<={3} AND ID<>{4}".format(moisDB,anneeDB,rank-2,rank+2,user)).fetchall():
        evol=curseur.execute("SELECT * FROM evol{0}{1}{2} ORDER BY DateID ASC".format(moisDB,anneeDB,i["ID"])).fetchall()
        if option in ("messages","voice","mots"):
            infos=getUserInfo(i["ID"],curseurGet,guild)
            hexa=hex(infos["Color"])[2:]
            if len(hexa)==6:
                hexa="#"+hexa
            else:
                hexa="#"+"0"*(6-len(hexa))+hexa
            nom=infos["Nom"]
        else:
            nom=getNom(i["ID"],option,curseurGet,False)
            hexa=None
        listeLabels=list(map(lambda x:"20{0}-{1}-{2}".format(x["Annee"],x["Mois"],x["Jour"]),evol))
        listeCount=list(map(lambda x:x["Count"], evol))
        for i in range(len(listeCount)):
            listeCount[i]=round(listeCount[i]/div,2)
        figAutour.add_trace(go.Scatter(x=listeLabels, y=listeCount, mode='lines', name=nom, line=dict(color=hexa)))

    figAutour.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Évolution {0} comparée avec les {1}s autour dans le classement".format(enteteCount(option).lower(),enteteNom(option).lower()),xaxis_title="Date",yaxis_title=enteteCount(option)+plus,hovermode="x unified")
    figAutour.update_yaxes(automargin=True)
    xaxeEvol(moisDB,figAutour)

    figAvAp = go.Figure()
    if moisDB!="glob":
        if moisDB=="to":
            perso=getTablePerso(guild,dictOptions[option],user,False,"A","periodAsc")
        else:
            perso=getTablePerso(guild,dictOptions[option],user,False,"M","periodAsc")

        i=0
        while perso[i]["Mois"]!=tableauMois[moisDB] or perso[i]["Annee"]!=anneeDB:
            i+=1

        if i!=0:
            connexionAvAp,curseurAvAp=connectSQL(guild,dictOptions[option],"Stats",perso[i-1]["Mois"],perso[i-1]["Annee"])
            avant=curseurAvAp.execute("SELECT * FROM evol{0}{1}{2} ORDER BY DateID ASC".format(tableauMois[perso[i-1]["Mois"]].lower(),perso[i-1]["Annee"],user)).fetchall()
            if moisDB=="to":
                listeLabels=list(map(lambda x:"2020-{0}-{1}".format(x["Mois"],x["Jour"]),avant))
            else:
                listeLabels=list(map(lambda x:"2020-01-{0}".format(x["Jour"]),avant))
            listeCount=list(map(lambda x:x["Count"], avant))
            for j in range(len(listeCount)):
                listeCount[j]=round(listeCount[j]/div,2)
            figAvAp.add_trace(go.Scatter(x=listeLabels, y=listeCount, mode='lines', name="{0}/{1}<br>Période précedente".format(perso[i-1]["Mois"],perso[i-1]["Annee"]), line=dict(color="turquoise")))
        
        if moisDB=="to":
            listeLabels=list(map(lambda x:"2020-{0}-{1}".format(x["Mois"],x["Jour"]),table))
        else:
            listeLabels=list(map(lambda x:"2020-01-{0}".format(x["Jour"]),table))
        figAvAp.add_trace(go.Scatter(x=listeLabels, y=listeCountBase, mode='lines', name="{0}/{1}<br>Maintenant".format(tableauMois[moisDB],anneeDB), line=dict(color=infosUser["Color"],width=3.5)))

        if i!=len(perso)-1:
            connexionAvAp,curseurAvAp=connectSQL(guild,dictOptions[option],"Stats",perso[i+1]["Mois"],perso[i+1]["Annee"])
            apres=curseurAvAp.execute("SELECT * FROM evol{0}{1}{2} ORDER BY DateID ASC".format(tableauMois[perso[i+1]["Mois"]],perso[i+1]["Annee"],user)).fetchall()
            if moisDB=="to":
                listeLabels=list(map(lambda x:"2020-{0}-{1}".format(x["Mois"],x["Jour"]),apres))
            else:
                listeLabels=list(map(lambda x:"2020-01-{0}".format(x["Jour"]),apres))
            listeCount=list(map(lambda x:x["Count"], apres))
            for j in range(len(listeCount)):
                listeCount[j]=round(listeCount[j]/div,2)
            figAvAp.add_trace(go.Scatter(x=listeLabels, y=listeCount, mode='lines', name="{0}/{1}<br>Période suivante".format(perso[i+1]["Mois"],perso[i+1]["Annee"]), line=dict(color="gold")))
        
        if moisDB=="to":
            figAvAp.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Évolution {0} sur la période, comparé à l'année précédente et suivante".format(enteteCount(option).lower()),xaxis_title="Dates",yaxis_title=enteteCount(option),hovermode="x unified",xaxis_tickformat = '%d / %m')
        else:
            figAvAp.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Évolution {0} sur la période, comparé au mois précédent et suivant".format(enteteCount(option).lower()),xaxis_title="Date",yaxis_title=enteteCount(option),hovermode="x unified",xaxis_tickformat = "%d")
        figAvAp.update_yaxes(automargin=True)
        figAvAp.update_xaxes(showgrid=False, zeroline=False,rangeslider_visible=True,rangeselector=dict(font_color="#111"),type="date")
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
