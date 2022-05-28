from math import inf

import plotly.graph_objects as go
from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import (chooseGetteur, getChannels, getEmoteTable, getFreq, getNom,
                                getPin, getUserInfo, getUserTable)
from companion.tools.outils import (connectSQL, dictOptions, getTablePerso,
                              listeOptions, tableauMois)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from plotly.offline import plot


@login_required(login_url="/login")
@CompanionStats
def graphFirst(request,guild,option):
    user=request.user

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    infos=getUserInfo(user.id,curseurGet,guild)
    hexa=hex(infos["Color"])[2:]
    if len(hexa)==6:
        hexa="#"+hexa
    else:
        hexa="#"+"0"*(6-len(hexa))+hexa
    
    div1,div2=linePlot(guild,option,user,hexa,curseur,curseurGet)

    #connexion.close()
    ctx={"fig":div1,"fig2":div2,"fig3":None,"fig4":None,"fig5":None,"fig6":None,"fig7":None,"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],"pagestats":True,
    "command":"first","options":listeOptions,"option":option,"plus":"graphs","travel":False,"selector":True,"obj":None,
    "pin":getPin(user,curseurGet,guild,option,"evol","graphs")}
    return render(request, "companion/Stats/Graphiques.html", ctx)


@login_required(login_url="/login")
def iFrameGraphFirst(request,guild,option):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats","GL","")

    stats=[]
    maxi=-inf
    for i in curseur.execute("SELECT * FROM firstM ORDER BY DateID DESC").fetchall():
        i["Rank"]=0

        ligne=chooseGetteur(option,"Stats",i,guild,curseurGet)

        ligne["Mois"]=i["Mois"]
        ligne["Annee"]=i["Annee"]
        stats.append(ligne)

        maxi=max(maxi,i["Count"])

    ctx={"rank":stats,"id":user.id,"max":maxi,"option":option,"plus":"graph"}
    return render(request, "companion/Stats/First/iFrameFirstGraph.html", ctx)

def linePlot(guild,option,user,color,curseur,curseurGet):
    first=curseur.execute("SELECT * FROM firstM ORDER BY DateID ASC").fetchall()
    
    moy=[]
    noms=[]
    ids=[]
    dictNoms={}
    dictColors={}

    for i in first:
        connexionMois,curseurMois=connectSQL(guild,dictOptions[option],"Stats",i["Mois"],i["Annee"])
        mois=curseurMois.execute("SELECT AVG(Count) AS Moy FROM {0}{1}".format(tableauMois[i["Mois"]],i["Annee"])).fetchone()
        if mois!=None:
            moy.append({"DateID":i["DateID"],"Mois":i["Mois"],"Annee":i["Annee"],"Count":mois["Moy"]})
        if option in ("messages","voice","mots"):
            infos=getUserInfo(i["ID"],curseurGet,guild)
            nom=infos["Nom"]
            hexa=hex(infos["Color"])[2:]
            if len(hexa)==6:
                hexa="#"+hexa
            else:
                hexa="#"+"0"*(6-len(hexa))+hexa
        else:
            nom=getNom(i["ID"],option,curseurGet,False)
            hexa="turquoise"

        noms.append(nom)
        ids.append(i["ID"])
        
        dictNoms[i["ID"]]=nom
        dictColors[i["ID"]]=hexa

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(map(lambda x:"20{1}-{0}".format(x["Mois"],x["Annee"]),first)), 
        y=list(map(lambda x:x["Count"],first)), 
        text=noms, 
        mode='lines+markers', 
        marker=dict(color="gold", size=10), 
        line=dict(color="gold"), 
        textposition="top center",
        hovertemplate = "%{y}<br>%{text}",
        name="Premiers"))
    
    if option in ("messages","voice","mots"):
        perso=getTablePerso(guild,dictOptions[option],user.id,False,"M","periodAsc")
        fig.add_trace(go.Scatter(
            x=list(map(lambda x:"20{1}-{0}".format(x["Mois"],x["Annee"]),perso)), 
            y=list(map(lambda x:x["Count"],perso)), 
            text=list(map(lambda x:x["Rank"],perso)), 
            mode='lines+markers', 
            marker=dict(color=color, size=10), 
            line=dict(color=color), 
            hovertemplate = "%{y}<br>%{text}e",
            name="Vous"))

    fig.add_trace(go.Scatter(
        x=list(map(lambda x:"20{1}-{0}".format(x["Mois"],x["Annee"]),moy)), 
        y=list(map(lambda x:x["Count"],moy)), 
        text=noms, 
        mode='lines+markers', 
        marker=dict(color="turquoise", size=10), 
        line=dict(color="turquoise"), 
        hovertemplate = "%{y}",
        name="Moyenne du serveur"))

    fig.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Périodes - Messages",xaxis_title="Dates",yaxis_title="Messages",hovermode="x")
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(showgrid=False, zeroline=False,rangeslider_visible=True,type="date",rangeselector=dict(font_color="#111",
            buttons=list([
                dict(count=3,
                     label="3 mois",
                     step="month",
                     stepmode="backward"),
                dict(count=6,
                     label="6 mois",
                     step="month",
                     stepmode="backward"),
                dict(count=1,
                     label="1 an",
                     step="year",
                     stepmode="backward"),
                dict(count=2,
                     label="2 ans",
                     step="year",
                     stepmode="backward"),
                dict(label="Tout",step="all")
            ])
        ),)

    idsDist=curseur.execute("SELECT DISTINCT ID FROM firstM").fetchall()
    nbfirst=[]
    colorsNb=[]
    nomsNb=[]
    for i in idsDist:
        nbfirst.append({"ID":i["ID"],"Count":curseur.execute("SELECT Count() AS Nombre FROM firstM WHERE ID={0}".format(i["ID"])).fetchone()["Nombre"]})
        nomsNb.append(dictNoms[i["ID"]])
        colorsNb.append(dictColors[i["ID"]])
    counts=list(map(lambda x:x["Count"],nbfirst))

    figNb=go.Figure(data=go.Bar(x=list(map(lambda x:str(x["ID"]),idsDist)),y=counts,marker_color=colorsNb,text=counts,textposition="auto"))

    figNb.update_layout(
        
        paper_bgcolor="#111",
        plot_bgcolor="#333",
        font_family="Roboto",
        font_color="white",
        xaxis={
            'categoryorder':'total descending',
            "rangeslider":{"visible":True},
            "title":"Membres",
            "range":[-0.5,20.5 if len(nbfirst)>20 else len(nbfirst)+0.5]},
        yaxis_title="Nombre de fois premier",
        height=750,
        title="Messages envoyés sur la période globale - Top 150"
    )
    figNb.update_yaxes(automargin=True)
    figNb.update_xaxes(ticktext=nomsNb,tickvals=list(map(lambda x:str(x["ID"]),idsDist)))

    return plot(fig,output_type='div'), plot(figNb,output_type='div')
