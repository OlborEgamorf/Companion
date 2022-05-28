import calendar
from math import inf

import plotly.graph_objects as go
from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import (chooseGetteur, getChannels, getEmoteTable, getFreq, getNom,
                                getPin, getUserInfo, getUserJeux, getUserTable)
from companion.tools.outils import (connectSQL, dictOptions, getMoisAnnee,
                              getTablePerso, getTimes, listeOptions,
                              tableauMois)
from companion.templatetags.TagsCustom import formatCount
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from plotly.offline import plot


@login_required(login_url="/login")
@CompanionStats
def graphRanks(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user

    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()

    listeMois,listeAnnee=getTimes(guild,option,"Stats")

    div1,div2=barPlot(guild,option,user,curseur,curseurGet,moisDB,anneeDB,True)

    if moisDB=="glob":
        if option in ("messages","voice","mots"):
            div3=heatmapGlobal(guild,option,curseur)
        else:
            div3=None
        div4,div5,div6=None,None,None
        div7=None
    elif moisDB=="to":
        div4,div5=pointPlot(guild,option,curseur,curseurGet,moisDB,anneeDB)
        div3,div6,div7=None
    else:
        if option in ("messages","voice","mots"):
            div3=heatmapMois(guild,option,tableauMois[moisDB],anneeDB)
        else:
            div3=None
        div4,div5=pointPlot(guild,option,curseur,curseurGet,moisDB,anneeDB)
        div6=linePlot(guild,option,user,curseur,curseurGet,mois,annee,moisDB,anneeDB)

        div7=barAnim(guild,option,curseur,curseurGet,moisDB,anneeDB)

    connexion.close()
    ctx={"fig":div1,"fig2":div2,"fig3":div3,"fig4":div4,"fig5":div5,"fig6":div6,"fig7":div7,"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
    "command":"ranks","options":listeOptions,"option":option,"plus":"graphs","travel":True,"selector":True,"obj":None,"pagestats":True,
    "pin":getPin(user,curseurGet,guild,option,"ranks","graphs")}
    return render(request, "companion/Stats/Graphiques.html", ctx)

@login_required(login_url="/login")
def iFrameGraphRanks(request,guild,option):
    all=request.GET.get("data")
    mois,annee,obj=all.split("?")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)
    user=request.user
    if obj=="None":
        obj=""
    
    categ="Stats"
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)

    maxi=-inf
    stats=[]
    for i in curseur.execute("SELECT * FROM {0}{1}{2} ORDER BY Rank ASC LIMIT 150".format(moisDB,anneeDB,obj)).fetchall():
        stats.append(chooseGetteur(option,categ,i,guild,curseurGet))
        maxi=max(maxi,i["Count"])

    ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"option":option,"plus":"graph"}
    return render(request, "companion/Ranks/iFrameRanks_ranks.html", ctx)



def barPlot(guild,option,user,curseur,curseurGet,moisDB,anneeDB,circular):
    colors=[]
    counts=[]
    names=[]
    ids=[]

    table=curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC".format(moisDB,anneeDB)).fetchall()
    if len(table)>150:
        reste=sum(list(map(lambda x:x["Count"],table[150:])))
        table=table[:150]
    else:
        reste=None

    for i in table:

        if option in ("messages","voice","mots"):
            ligne=getUserTable(i,curseurGet,guild)

        elif option in ("emotes","reactions"):
            ligne=getEmoteTable(i,curseurGet)

        elif option in ("salons","voicechan"):
            ligne=getChannels(i,curseurGet)

        elif option=="freq":
            ligne=getFreq(i)

        if ligne["Nom"]=="Ancien membre" or option not in ("messages","voice","mots"):
            pass
        else:
            if len(ligne["Color"])<=6:
                colors.append("#"+"0"*(7-len(ligne["Color"]))+ligne["Color"][1:])
            else:
                colors.append(ligne["Color"])

        if len(ligne["Nom"])<15:
            names.append(ligne["Nom"])
        else:
            names.append(ligne["Nom"][:15]+"...")

        counts.append(i["Count"])
        ids.append(str(i["ID"]))
    
    fig=go.Figure(data=go.Bar(x=ids,y=counts,marker_color=colors,text=counts,textposition="auto"))

    fig.update_layout(
        
        paper_bgcolor="#111",
        plot_bgcolor="#333",
        font_family="Roboto",
        font_color="white",
        xaxis={
            'categoryorder':'total descending',
            "rangeslider":{"visible":True},
            "title":"Membres",
            "range":[-0.5,20.5 if len(table)>20 else len(table)+0.5]},
        yaxis_title="Messages",
        height=750,
        title="Messages envoyés sur la période globale - Top 150"
    )
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(ticktext=names,tickvals=ids)

    if circular:
        if reste!=None:
            counts.append(reste)
            ids.append("0")
            names.append("> Top 150")
            colors.append("rgb(110,200,250)")
        
        figCirc=go.Figure(data=go.Pie(labels=names,values=counts,ids=ids))
        figCirc.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",font_size=14,height=750,title="Proportions",
        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
        figCirc.update_traces(marker_colors=colors,textposition='inside')
        figCirc.update_yaxes(automargin=True)

        return plot(fig,output_type='div'), plot(figCirc,output_type='div')
    else:
        return plot(fig,output_type='div')


def barAnim(guild,option,curseur,curseurGet,moisDB,anneeDB):
    ids=[]
    table=curseur.execute("SELECT * FROM {0}{1} WHERE Rank<150 ORDER BY Rank ASC".format(moisDB,anneeDB)).fetchall()
    for i in table:
        if curseur.execute("SELECT * FROM evol{0}{1}{2} WHERE Rank<30".format(moisDB,anneeDB,i["ID"])).fetchone()!=None:
            ids.append(i["ID"])

    dictInfos={}
    for i in ids:
        if option in ("messages","voice","mots"):
            infos=getUserInfo(i,curseurGet,guild)
            hexa=hex(infos["Color"])[2:]
            if len(hexa)==6:
                infos["Color"]="#"+hexa
            else:
                infos["Color"]="#"+"0"*(6-len(hexa))+hexa
        else:
            nom=getNom(i,option,curseurGet,False)
            infos={"ID":i,"Nom":nom,"Color":None}
        dictInfos[i]=infos
    connexionRap,curseurRap=connectSQL(guild,"Rapports","Stats","GL","")
    dates=curseurRap.execute("SELECT DISTINCT Jour FROM ranks WHERE Mois='{0}' AND Annee='{1}' AND Type='{2}' ORDER BY Jour ASC".format(tableauMois[moisDB],anneeDB,dictOptions[option])).fetchall()
    
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }
    fig_dict["layout"]["xaxis"] = {'categoryorder':'total descending', "title": "Rang", "automargin":True,"range":[0,15.5 if len(table)>15 else len(table)+0.5], "showgrid":False}
    fig_dict["layout"]["yaxis"] = {"title": "Messages","range":[0,table[0]["Count"]*1.1]}
    fig_dict["layout"]["hovermode"] = "closest"
    fig_dict["layout"]["showlegend"] = False
    fig_dict["layout"]["paper_bgcolor"] = "#111"
    fig_dict["layout"]["plot_bgcolor"] = "#333"
    fig_dict["layout"]["font_family"] = "Roboto"
    fig_dict["layout"]["font_color"] = "white"
    fig_dict["layout"]["font_size"] = 14
    fig_dict["layout"]["height"] = 750
    fig_dict["layout"]["title"] = "Graphique animé de l'évolution du classement"
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 500, "redraw": False},
                                    "fromcurrent": True, "transition": {"duration": 300,
                                                                        "easing": "quadratic-in-out"}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }
    ]

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Jour : ",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": 300, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    jour = dates[0]["Jour"]
    for membre in ids:
        evol=curseur.execute("SELECT * FROM evol{0}{1}{2} WHERE Jour='{3}'".format(moisDB,anneeDB,membre,jour)).fetchone()
        if evol==None:
            data_dict = {
                "x": [None,None],
                "y": [None,None],
                "name": membre,
                "mode": "lines+text",
                "text": [None,dictInfos[membre]["Nom"]],
                "textposition":"top center",
                "line":{"color":dictInfos[membre]["Color"],"width":14}
            }
        else:
            data_dict = {
                "x": [evol["Rank"],evol["Rank"]],
                "y": [0,evol["Count"]],
                "name": membre,
                "mode": "lines+text",
                "text": [evol["Count"],dictInfos[membre]["Nom"]],
                "textposition":"top center",
                "line":{"color":dictInfos[membre]["Color"],"width":14}
            }
        fig_dict["data"].append(data_dict)

    
    for jour in dates:
        formatDate="{0}/{1}/20{2}".format(jour["Jour"],tableauMois[moisDB],anneeDB)
        frame = {"data": [], "name":formatDate }
        for membre in ids:
            evol=curseur.execute("SELECT * FROM evol{0}{1}{2} WHERE Jour='{3}'".format(moisDB,anneeDB,membre,jour["Jour"])).fetchone()

            if evol==None:
                data_dict = {
                    "x": [None,None],
                    "y": [None,None],
                    "name": membre,
                    "mode": "lines+text",
                    "text": [None,dictInfos[membre]["Nom"]],
                    "textposition":"top center",
                    "line":{"color":dictInfos[membre]["Color"],"width":14}
                }
            else:
                data_dict = {
                    "x": [evol["Rank"],evol["Rank"]],
                    "y": [0,evol["Count"]],
                    "name": membre,
                    "mode": "lines+text",
                    "text": [evol["Count"],dictInfos[membre]["Nom"]],
                    "textposition":"top center",
                    "line":{"color":dictInfos[membre]["Color"],"width":14}
                }
            frame["data"].append(data_dict)

        fig_dict["frames"].append(frame)
        slider_step = {"args": [
            [formatDate],
            {"frame": {"duration": 300, "redraw": False},
            "mode": "immediate",
            "transition": {"duration": 300}}
        ],
            "label": formatDate,
            "method": "animate"}
        sliders_dict["steps"].append(slider_step)


    fig_dict["layout"]["sliders"] = [sliders_dict]

    fig = go.Figure(fig_dict)
    return plot(fig,output_type='div')


def pointPlot(guild,option,curseur,curseurGet,moisDB,anneeDB):
    listeNow,listeMed,listeMax,listeMoy,listeNoms=[],[],[],[],[]
    listeRankNow,listeRankMed,listeRankMax,listeRankMoy=[],[],[],[]
    listeIDs=[]
    moisPoint=curseur.execute("SELECT * FROM {0}{1} WHERE Rank<=15 ORDER BY Rank DESC".format(moisDB,anneeDB)).fetchall()
    
    for i in moisPoint:
        if option in ("messages","voice","mots"):
            infos=getUserInfo(i["ID"],curseurGet,guild)
            listeNoms.append(infos["Nom"])
        else:
            listeNoms.append(getNom(i["ID"],option,curseurGet,False))

        if moisDB=="to":
            table=getTablePerso(guild,dictOptions[option],i["ID"],False,"A","countDesc")
        else:
            table=getTablePerso(guild,dictOptions[option],i["ID"],False,"M","countDesc")

        listeNow.append(i["Count"])
        listeMax.append(table[0]["Count"])
        listeMed.append((table[len(table)//2]["Count"]))
        listeMoy.append(sum(list(map(lambda x:x["Count"],table)))/len(table))

        table.sort(key=lambda x:x["Rank"])
        listeRankNow.append(i["Rank"])
        listeRankMax.append(table[0]["Rank"])
        listeRankMed.append((table[len(table)//2]["Rank"]))
        listeRankMoy.append(sum(list(map(lambda x:x["Rank"],table)))/len(table))

        listeIDs.append(str(i["ID"]))

    figCount = go.Figure()   
    figRank = go.Figure() 
    
    if moisDB=="to": 
        figCount.add_trace(go.Scatter(x=listeNow,y=listeIDs,marker=dict(color="crimson", size=12),mode="markers",name="Cette année"))
        figRank.add_trace(go.Scatter(x=listeRankNow,y=listeIDs,marker=dict(color="crimson", size=12),mode="markers",name="Cette année"))
    else:
        figCount.add_trace(go.Scatter(x=listeNow,y=listeIDs,marker=dict(color="crimson", size=12),mode="markers",name="Ce mois-ci"))
        figRank.add_trace(go.Scatter(x=listeRankNow,y=listeIDs,marker=dict(color="crimson", size=12),mode="markers",name="Ce mois-ci"))

    figCount.add_trace(go.Scatter(x=listeMed,y=listeIDs,marker=dict(color="gold", size=8),mode="markers",name="Médiane"))
    figCount.add_trace(go.Scatter(x=listeMoy,y=listeIDs,marker=dict(color="cyan", size=8),mode="markers",name="Moyenne"))
    figCount.add_trace(go.Scatter(x=listeMax,y=listeIDs,marker=dict(color="yellowgreen", size=8),mode="markers",name="Maximum"))
    figCount.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=600,title="Indicateurs sur le nombre de messages envoyés",xaxis_title="Messages",yaxis_title="Membres",legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
    figCount.update_yaxes(automargin=True,ticktext=listeNoms,tickvals=listeIDs)
    figCount.update_xaxes(showgrid=False, zeroline=False)

    figRank.add_trace(go.Scatter(x=listeRankMed,y=listeIDs,marker=dict(color="gold", size=8),mode="markers",name="Médiane"))
    figRank.add_trace(go.Scatter(x=listeRankMoy,y=listeIDs,marker=dict(color="turquoise", size=8),mode="markers",name="Moyenne"))
    figRank.add_trace(go.Scatter(x=listeRankMax,y=listeIDs,marker=dict(color="yellowgreen", size=8),mode="markers",name="Minimum"))
    figRank.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=600,title="Indicateurs sur les rangs",xaxis_title="Rang",yaxis_title="Membres",legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
    figRank.update_yaxes(automargin=True,ticktext=listeNoms,tickvals=listeIDs)
    figRank.update_xaxes(showgrid=False, zeroline=False,autorange="reversed")

    return plot(figCount,output_type='div'), plot(figRank,output_type='div')


def heatmapMois(guild,option,mois,annee):
    listeHeat=[]
    labels=[]
    
    anneeDate="20{0}".format(annee)
    
    connexion,curseur=connectSQL(guild,"Rapports","Stats","GL","")
    dates=curseur.execute("SELECT DISTINCT Jour FROM ranks WHERE Mois='{0}' AND Annee='{1}' AND Type='{2}'".format(mois,annee,dictOptions[option])).fetchall()
    calendrier=calendar.monthrange(int(anneeDate),int(mois))

    if calendrier[1]+calendrier[0]==36:
        stop=calendrier[1]+calendrier[0]+7
    else:
        stop=calendrier[1]+calendrier[0]
    for i in range(1,stop,7):
        listeHeat.append([None]*7)
        labels.append([""]*7)
        if i==1:
            for j in range(calendrier[0]):
                listeHeat[0][j]=None
    
    if (calendrier[0]+calendrier[1])%7!=0:
        for i in range((calendrier[0]+calendrier[1])%7,7):
            listeHeat[len(listeHeat)-1][i]=None

    for i in dates:
        somme=curseur.execute("SELECT SUM(Count) AS Total FROM ranks WHERE Jour='{0}' AND Mois='{1}' AND Annee='{2}' AND Type='{3}'".format(i["Jour"],mois,annee,dictOptions[option])).fetchone()["Total"]
        jour=calendar.weekday(int(anneeDate),int(mois),int(i["Jour"]))
        if calendrier[0]==0:
            semaine=(int(i["Jour"])+6-jour)//7-1
        else:
            semaine=(int(i["Jour"])+6-jour)//7
        listeHeat[semaine][jour]=somme
        labels[semaine][jour]="{0}/{1}/{2} - {3}".format(i["Jour"],mois,annee,formatCount(somme,option))

    listeHeat.reverse()
    labels.reverse()
    fig = go.Figure(data=go.Heatmap(
                    x=["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"],
                    z=listeHeat,
                    text=labels,
                    texttemplate="%{text}",
                    textfont={"size":11},
                    colorscale="YlGnBu"))
                    
    fig.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=500,title="Calendrier des messages envoyés")
    fig.update_yaxes(automargin=True, showgrid=False, zeroline=False)
    fig.update_xaxes(showgrid=False, zeroline=False)
    return plot(fig,output_type='div')



def heatmapGlobal(guild,option,curseur):
    connexionRap,curseurRap=connectSQL(guild,"Rapports","Stats","GL","")

    dates=curseur.execute("SELECT DISTINCT Annee FROM firstA WHERE Annee<>'GL' ORDER BY Annee DESC").fetchall()
    listeHeat=[[0]*12 for i in range(len(dates))]
    labels=[[""]*12 for i in range(len(dates))]
    listeMoisHeat=["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Aout","Septembre","Octobre","Novembre","Décembre"]
    
    for i in range(len(dates)):
        for j in range(12):
            moisHeat=tableauMois[listeMoisHeat[j].lower()]
            try:
                assert curseur.execute("SELECT * FROM firstM WHERE Mois='{0}' AND Annee='{1}'".format(moisHeat,dates[i]["Annee"])).fetchone()!=None
                somme=curseurRap.execute("SELECT SUM(Count) AS Total FROM ranks WHERE Mois='{0}' AND Annee='{1}' AND Type='{2}'".format(moisHeat,dates[i]["Annee"],dictOptions[option])).fetchone()["Total"]
                if somme==None:
                    listeHeat[i][j]=0
                else:
                    listeHeat[i][j]=somme
                    labels[i][j]=formatCount(somme,option)
                if option in ("Voice","Voicechan"):
                    if len(labels[i][j].split(" "))>=3:
                        descip=""
                        for z in range(len(labels[i][j].split(" "))):
                            if z==2:
                                descip+="\n"
                            descip+=labels[i][j].split(" ")[z]+" "
                        labels[i][j]=descip
            except AssertionError:
                listeHeat[i][j]=0

    fig = go.Figure(data=go.Heatmap(
                    x=listeMoisHeat,
                    y=["20{0}".format(dates[i]["Annee"]) for i in range(len(dates))],
                    z=listeHeat,
                    text=labels,
                    texttemplate="%{text}",
                    textfont={"size":14},
                    colorscale="YlGnBu"))
                    
    fig.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",title="Calendrier des messages envoyés")
    fig.update_yaxes(automargin=True)
    return plot(fig,output_type='div')


def linePlot(guild,option,user,curseur,curseurGet,mois,annee,moisDB,anneeDB):
    table=curseur.execute("SELECT ID FROM {0}{1} ORDER BY Rank ASC".format(moisDB,anneeDB)).fetchall()

    connexionGL,curseurGL=connectSQL(guild,dictOptions[option],"Stats","GL","")

    old10=curseurGL.execute("SELECT * FROM firstM WHERE DateID<={0}{1} ORDER BY DateID DESC".format(anneeDB,tableauMois[moisDB],)).fetchall()
    old10=old10[0:10] if len(old10)>10 else old10

    listeDates=[]
    listeX,listeY,listeR=[[],[],[],[]],[[],[],[],[]],[[],[],[],[]]
    mini=inf

    stop=3 if len(table)>3 else len(table)
    ids=list(map(lambda x:x["ID"],table))[:stop]
    if user.id not in ids and option in ("messages","voice","mots"):
        ids.append(user.id)
        stop+=1
    ids.reverse()

    for i in range(stop-1,-1,-1):
        for j in range(len(old10)-1,-1,-1):
            connexionMois,curseurMois=connectSQL(guild,dictOptions[option],"Stats",old10[j]["Mois"],old10[j]["Annee"])
            count=curseurMois.execute("SELECT Count,Rank FROM {0}{1} WHERE ID={2}".format(tableauMois[old10[j]["Mois"]],old10[j]["Annee"],ids[i])).fetchone()
            if count!=None:
                if old10[j]["DateID"] not in listeDates:
                    listeDates.append(old10[j]["DateID"])
                listeX[i].append("{0}/{1}".format(old10[j]["Mois"],old10[j]["Annee"]))
                listeY[i].append(count["Count"])
                listeR[i].append("{0}e".format(count["Rank"]))
                mini=min(count["Count"],mini)

    listeDates.sort()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=["{0}/{1}".format(str(i)[2:4],str(i)[0:2]) for i in listeDates], y=[mini//1.5 for i in range(len(listeDates))],mode='none',name=""))

    dictLine={2:"dash",3:"dot"}
    colors=[]

    for i in range(stop):
        if option in ("messages","voice","mots"):
            infos=getUserInfo(ids[i],curseurGet,guild)
            hexa=hex(infos["Color"])[2:]
            if len(hexa)==6:
                color="#"+hexa
            else:
                color="#"+"0"*(6-len(hexa))+hexa
            nom=infos["Nom"]
        else:
            nom=getNom(ids[i],option,curseurGet,False)
            color=None
        
        colors.append(color)
        count=colors.count(color)
        if count==1:
            fig.add_trace(go.Scatter(x=listeX[i], y=listeY[i],mode='lines+markers+text',name=nom,marker=dict(color=color, size=12),line=dict(color=color),text=listeR[i],textposition="top center"))
        else:
            fig.add_trace(go.Scatter(x=listeX[i], y=listeY[i],mode='lines+markers+text',name=nom,marker=dict(color=color, size=12),line=dict(color=color,dash=dictLine[count]),text=listeR[i],textposition="top center"))

    fig.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=600,title="Evolution des trois premiers sur les 10 derniers mois",xaxis_title="Dates",yaxis_title="Messages",hovermode="x unified",legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(showgrid=False, zeroline=False)
    return plot(fig,output_type='div')
