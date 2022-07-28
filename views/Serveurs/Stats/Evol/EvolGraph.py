import plotly.graph_objects as go
from companion.templatetags.TagsCustom import enteteCount, enteteNom
from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import (getAllInfos, getNom, getPin, getUserInfo,
                                      objSelector)
from companion.tools.outils import (collapseEvol, connectSQL, dictOptions,
                                    getMoisAnnee, getTablePerso, getTimes,
                                    listeOptions, listeOptionsJeux,
                                    tableauMois, voiceAxe)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from plotly.offline import plot


def graphEvolJeux(request,option):
    return graphEvol(request,"OT",option)

def iFrameGraphEvolJeux(request,option):
    return iFrameGraphEvol(request,"OT",option)

@login_required(login_url="/login")
@CompanionStats
def graphEvol(request,guild,option):
    mois,annee,obj = request.GET.get("mois"),request.GET.get("annee"),request.GET.get("obj")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
    else:
        categ="Stats"
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    listeMois,listeAnnee=getTimes(guild,option,categ)
    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)

    if option not in ("messages","voice","mots") and categ!="Jeux": 
        listeObj=objSelector(guild,option,categ,user,curseurGet,curseurGuild)
    
        if obj==None:
            obj=listeObj[0]["ID"]
        elif option in ("salons","voicechan"):
            hide=curseurGuild.execute("SELECT * FROM chans WHERE ID={0}".format(obj)).fetchone()
            assert hide!=None and not hide["Hide"]

        div1,div2,div3,div4=linePlots(guild,option,curseur,curseurGet,curseurGuild,obj,moisDB,anneeDB,False,categ)
    else:
        div1,div2,div3,div4=linePlots(guild,option,curseur,curseurGet,curseurGuild,user.id,moisDB,anneeDB,False,categ)
        listeObj=None

    connexion.close()
    if categ=="Jeux":
        ctx={"fig":div1,"fig2":div2,"fig3":div3,"fig4":div4,"fig5":None,"fig6":None,"fig7":None,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":"Classement jeux","guildid":"ot/jeux",
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "command":"evol","options":listeOptionsJeux,"option":option,"plus":"graphs",
        "travel":True,"selector":True,"obj":obj,"listeObjs":listeObj,"pagestats":True,"ot":True,
        "pin":getPin(user,curseurGet,"ot/jeux",option,"evol","graphs")}
    else:
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
    
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
    else:
        categ="Stats"

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)

    table=curseur.execute("SELECT * FROM evol{0}{1}{2}".format(moisDB,anneeDB,obj)).fetchall()
    table=collapseEvol(table)  
    table.reverse() 
    table=list(filter(lambda x:not x["Collapse"],table))
    maxi=max(list(map(lambda x:x["Count"],table)))

    ctx={"rank":table,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"option":option,"plus":"graph"}
    return render(request, "companion/Stats/Ranks/iFrameRanks_evol.html", ctx)


def linePlots(guild,option,curseur,curseurGet,curseurGuild,user,moisDB,anneeDB,recap,categ):
    if option in ("messages","voice","mots"):
        infosUser=getUserInfo(user,curseurGet,guild)
    elif categ=="Jeux":
        connexionUser,curseurUser=connectSQL("OT",user,"Titres",None,None)
        infosUser=getAllInfos(curseurGet,curseurUser,connexionUser,user)
        infosUser["Nom"]=infosUser["Full"]
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
    fig.update_layout(paper_bgcolor="#222",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Évolution {0} sur toute la période".format(enteteCount(option).lower()),xaxis_title="Date",yaxis_title=enteteCount(option)+plus,hovermode="x")
    fig.update_yaxes(automargin=True)
    xaxeEvol(moisDB,fig)

    if recap:
        fig.update_layout(height=None)
        fig.update_xaxes(rangeslider_visible=False)
        return plot(fig,output_type='div')


    figRank = go.Figure()
    figRank.add_trace(go.Scatter(x=listeLabels, y=listeRanks, mode='lines', line=dict(color=infosUser["Color"],width=3.5)))
    figRank.update_layout(paper_bgcolor="#222",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Évolution du rang dans le classement sur toute la période",xaxis_title="Date",yaxis_title="Rang",hovermode="x")
    figRank.update_yaxes(automargin=True,autorange="reversed")
    xaxeEvol(moisDB,figRank)


    figAutour = go.Figure()
    figAutour.add_trace(go.Scatter(x=listeLabels, y=listeCountBase, mode='lines', name=infosUser["Nom"], line=dict(color=infosUser["Color"],width=3.5)))
    for i in curseur.execute("SELECT * FROM {0}{1} WHERE Rank>={2} AND Rank<={3} AND ID<>{4}".format(moisDB,anneeDB,rank-2,rank+2,user)).fetchall():
        evol=curseur.execute("SELECT * FROM evol{0}{1}{2} ORDER BY DateID ASC".format(moisDB,anneeDB,i["ID"])).fetchall()
        if option in ("messages","voice","mots"):
            hide=curseurGuild.execute("SELECT * FROM users WHERE ID={0}".format(i["ID"])).fetchone()
            if hide==None or hide["Hide"]:
                continue
            infos=getUserInfo(i["ID"],curseurGet,guild)
            color=infos["Color"]
            nom=infos["Nom"]
        elif categ=="Jeux":
            connexionUser,curseurUser=connectSQL("OT",i["ID"],"Titres",None,None)
            infos=getAllInfos(curseurGet,curseurUser,connexionUser,i["ID"])
            nom=infos["Full"]
            color=infos["Color"]
        else:
            if option in ("salons","voicechan"):
                hide=curseurGuild.execute("SELECT * FROM chans WHERE ID={0}".format(i["ID"])).fetchone()
                if hide==None or hide["Hide"]:
                    continue
            nom=getNom(i["ID"],option,curseurGet,False)
            color=None
        listeLabels=list(map(lambda x:"20{0}-{1}-{2}".format(x["Annee"],x["Mois"],x["Jour"]),evol))
        listeCount=list(map(lambda x:x["Count"], evol))
        for i in range(len(listeCount)):
            listeCount[i]=round(listeCount[i]/div,2)
        figAutour.add_trace(go.Scatter(x=listeLabels, y=listeCount, mode='lines', name=nom, line=dict(color=color)))

    figAutour.update_layout(paper_bgcolor="#222",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Évolution {0} comparée avec les {1}s autour dans le classement".format(enteteCount(option).lower(),enteteNom(option).lower()),xaxis_title="Date",yaxis_title=enteteCount(option)+plus,hovermode="x unified")
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
            connexionAvAp,curseurAvAp=connectSQL(guild,dictOptions[option],categ,perso[i-1]["Mois"],perso[i-1]["Annee"])
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
            connexionAvAp,curseurAvAp=connectSQL(guild,dictOptions[option],categ,perso[i+1]["Mois"],perso[i+1]["Annee"])
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
            figAvAp.update_layout(paper_bgcolor="#222",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Évolution {0} sur la période, comparé à l'année précédente et suivante".format(enteteCount(option).lower()),xaxis_title="Dates",yaxis_title=enteteCount(option),hovermode="x unified",xaxis_tickformat = '%d / %m')
        else:
            figAvAp.update_layout(paper_bgcolor="#222",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Évolution {0} sur la période, comparé au mois précédent et suivant".format(enteteCount(option).lower()),xaxis_title="Date",yaxis_title=enteteCount(option),hovermode="x unified",xaxis_tickformat = "%d")
        figAvAp.update_yaxes(automargin=True)
        figAvAp.update_xaxes(showgrid=False, zeroline=False,rangeslider_visible=True,rangeselector=dict(font_color="#222"),type="date")
        #xaxeEvol(moisDB,figAvAp)  
    if moisDB!="glob":
        return plot(fig,output_type='div'),plot(figRank,output_type='div'),plot(figAutour,output_type='div'),plot(figAvAp,output_type='div')
    else:
        return plot(fig,output_type='div'),plot(figRank,output_type='div'),plot(figAutour,output_type='div'),None

def xaxeEvol(moisDB,fig):
    if moisDB=="glob":
        fig.update_xaxes(showgrid=False, zeroline=False,rangeslider_visible=True,type="date",rangeselector=dict(font_color="#222",
        buttons=list([
            dict(count=3,label="3 mois",step="month",stepmode="backward"),
            dict(count=6,label="6 mois",step="month",stepmode="backward"),
            dict(count=1,label="1 an",step="year",stepmode="backward"),
            dict(count=2,label="2 ans",step="year",stepmode="backward"),
            dict(label="Tout",step="all")])))
    elif moisDB=="to":
        fig.update_xaxes(showgrid=False, zeroline=False,rangeslider_visible=True,type="date",rangeselector=dict(font_color="#222",
        buttons=list([
            dict(count=1,label="1 mois",step="month",stepmode="backward"),
            dict(count=2,label="2 mois",step="month",stepmode="backward"),
            dict(count=3,label="3 mois",step="month",stepmode="backward"),
            dict(count=6,label="6 mois",step="month",stepmode="backward"),
            dict(label="Tout",step="all")])))
    else:
        fig.update_xaxes(showgrid=False, zeroline=False,rangeslider_visible=True,type="date",rangeselector=dict(font_color="#222",
        buttons=list([
            dict(count=7,label="7 jours",step="day",stepmode="backward"),
            dict(count=10,label="10 jours",step="day",stepmode="backward"),
            dict(count=15,label="15 jours",step="day",stepmode="backward"),
            dict(count=20,label="20 jours",step="day",stepmode="backward"),
            dict(label="Tout",step="all")])))



def evolGraphCompare(option,curseur,user,compare,moisDB,anneeDB,nom1,nom2,color1,color2):
    
    fig = go.Figure()
    tableCompare=curseur.execute("SELECT * FROM evol{0}{1}{2} ORDER BY DateID ASC".format(moisDB,anneeDB,compare)).fetchall()

    if option in ("messages","voice"):
        table=curseur.execute("SELECT * FROM evol{0}{1}{2} ORDER BY DateID ASC".format(moisDB,anneeDB,user)).fetchall()
        listeLabels=list(map(lambda x:"20{0}-{1}-{2}".format(x["Annee"],x["Mois"],x["Jour"]),table))
        listeCountBase=list(map(lambda x:x["Count"], table))
        plus,div=voiceAxe(option,listeCountBase)
        fig.add_trace(go.Scatter(x=listeLabels, y=listeCountBase, mode='lines', name=nom1, line=dict(color=color1,width=3.5)))
    else:
        div,plus=1,""

    listeLabels=list(map(lambda x:"20{0}-{1}-{2}".format(x["Annee"],x["Mois"],x["Jour"]),tableCompare))
    listeCountBase=list(map(lambda x:x["Count"], tableCompare))
    for i in range(len(listeCountBase)):
        listeCountBase[i]=round(listeCountBase[i]/div,2)
    fig.add_trace(go.Scatter(x=listeLabels, y=listeCountBase, mode='lines', name=nom2, line=dict(color=color2,width=3.5)))

    if option in ("messages","voice"): 
        fig.update_layout(paper_bgcolor="#222",plot_bgcolor="#333",font_family="Roboto",font_color="white",title="Évolution {0} comparée".format(enteteCount(option).lower()),xaxis_title="Date",yaxis_title=enteteCount(option)+plus,hovermode="x unified")
    else:
        fig.update_layout(paper_bgcolor="#222",plot_bgcolor="#333",font_family="Roboto",font_color="white",title="Évolution {0} - {1}".format(enteteCount(option).lower(),nom2),xaxis_title="Date",yaxis_title=enteteCount(option)+plus,hovermode="x unified")
    fig.update_yaxes(automargin=True)
    xaxeEvol(moisDB,fig)
    fig.update_xaxes(rangeslider_visible=False)

    return plot(fig,output_type='div')
