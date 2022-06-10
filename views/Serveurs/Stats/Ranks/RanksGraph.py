import calendar
from math import inf

import plotly.graph_objects as go
from companion.templatetags.TagsCustom import enteteCount, enteteNom, formatCount
from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import chooseGetteur, getAllInfos, getNom, getPin, getUserInfo
from companion.tools.outils import (connectSQL, dictOptions, getMoisAnnee,
                                    getTablePerso, getTimes, listeOptions,
                                    tableauMois, voiceAxe,listeOptionsJeux)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from plotly.offline import plot


def graphRanksJeux(request,option):
    return graphRanks(request,"OT",option)

def iFrameGraphRanksJeux(request,option):
    return iFrameGraphRanks(request,"OT",option)

@login_required(login_url="/login")
@CompanionStats
def graphRanks(request,guild,option):
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
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

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)
    
    listeMois,listeAnnee=getTimes(guild,option,categ)

    if categ=="Jeux":
        div1=barPlot(guild,option,categ,curseur,curseurGet,curseurGuild,moisDB,anneeDB,False)
        if moisDB!="glob":
            if moisDB!="to":
                div2=linePlot(guild,option,user,curseur,curseurGet,curseurGuild,categ,moisDB,anneeDB)
            else:
                div2=None
            div3,div4=pointPlot(guild,option,curseur,curseurGet,curseurGuild,moisDB,anneeDB,categ)
        else:
            div2,div3,div4=None,None,None
        div5,div6=None,None
            
    else:
        div1=barPlot(guild,option,user,curseur,curseurGet,curseurGuild,moisDB,anneeDB,False)
        div2=barAnim(guild,option,curseur,curseurGet,curseurGuild,moisDB,anneeDB)

        if moisDB=="glob":
            if option in ("messages","voice","mots"):
                div3=heatmapGlobal(guild,option,curseur)
            else:
                div3=None
            div4,div5,div6=None,None,None
        elif moisDB=="to":
            div3=heatmapAnnee(guild,option,annee)
            div4,div5=pointPlot(guild,option,curseur,curseurGet,curseurGuild,moisDB,anneeDB,categ)
            div6=None
        else:
            div3=linePlot(guild,option,user,curseur,curseurGet,curseurGuild,categ,moisDB,anneeDB)
            if option in ("messages","voice","mots"):
                div4=heatmapMois(guild,option,tableauMois[moisDB],anneeDB)
            else:
                div4=None
            div5,div6=pointPlot(guild,option,curseur,curseurGet,curseurGuild,moisDB,anneeDB,categ)

    connexion.close()
    if categ=="Jeux":
        ctx={"fig":div1,"fig2":div2,"fig3":div3,"fig4":div4,"fig5":div5,"fig6":div6,"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"guildname":"Classements jeux","guildid":"ot/jeux","mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "command":"ranks","options":listeOptionsJeux,"option":option,"plus":"graphs","travel":True,"selector":True,"obj":None,"pagestats":True,"ot":True,
        "pin":getPin(user,curseurGet,"ot/jeux",option,"ranks","graphs")}
    else:
        ctx={"fig":div1,"fig2":div2,"fig3":div3,"fig4":div4,"fig5":div5,"fig6":div6,"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],"mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
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
    
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
    else:
        categ="Stats"
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,tableauMois[moisDB],anneeDB)
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)

    maxi=-inf
    stats=[]
    for i in curseur.execute("SELECT * FROM {0}{1}{2} ORDER BY Rank ASC LIMIT 150".format(moisDB,anneeDB,obj)).fetchall():
        stats.append(chooseGetteur(option,categ,i,guild,curseurGet,curseurGuild))
        maxi=max(maxi,i["Count"])

    ctx={"rank":stats,"id":user.id,"max":maxi,"mois":mois,"annee":annee,"option":option,"plus":"graph"}
    return render(request, "companion/Stats/Ranks/iFrameRanks_ranks.html", ctx)



def barPlot(guild,option,categ,curseur,curseurGet,curseurGuild,moisDB,anneeDB,circular):
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
        ligne=chooseGetteur(option,categ,i,guild,curseurGet,curseurGuild)
        if ligne["Nom"]=="Membre masqué" or ligne["Nom"]=="Salon masqué":
            continue

        if categ=="Jeux":
            if ligne["Color"]!=None:
                colors.append(ligne["Color"])
            else:
                colors.append("turquoise")
        elif ligne["Nom"]=="Ancien membre" or option not in ("messages","voice","mots"):
            pass
        else:
            colors.append(ligne["Color"])

        if len(ligne["Nom"])<15:
            names.append(ligne["Nom"])
        else:
            names.append(ligne["Nom"][:15]+"...")

        counts.append(i["Count"])
        ids.append(str(i["ID"]))
    
    plus=voiceAxe(option,counts)[0]
    
    fig=go.Figure(data=go.Bar(x=ids,y=counts,marker_color=colors,text=counts,textposition="auto"))

    fig.update_layout(
        
        paper_bgcolor="#111",
        plot_bgcolor="#333",
        font_family="Roboto",
        font_color="white",
        xaxis={
            'categoryorder':'total descending',
            "rangeslider":{"visible":True},
            "title":enteteNom(option),
            "range":[-0.5,20.5 if len(table)>20 else len(table)+0.5]},
        yaxis_title=enteteCount(option)+plus,
        height=750,
        title="{0} sur la période - Top 150".format(enteteCount(option))
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

def collapseAnim(table:list) -> list:
    temp=(table[0]["Mois"],table[0]["Annee"])
    dates=[]
    if len(table)>31:
        dates.append(table[0])
        for i in range(1,len(table)-1):
            if temp!=(table[i]["Mois"],table[i]["Annee"]):
                dates.append(table[i])
                temp=(table[i]["Mois"],table[i]["Annee"])
        dates.append(table[-1])
    else:
        dates=table.copy()
    return dates


def barAnim(guild,option,curseur,curseurGet,curseurGuild,moisDB,anneeDB):
    ids=[]
    table=curseur.execute("SELECT * FROM {0}{1} WHERE Rank<150 ORDER BY Rank ASC".format(moisDB,anneeDB)).fetchall()
    for i in table:
        if option in ("messages","voice"):
            hide=curseurGuild.execute("SELECT * FROM users WHERE ID={0}".format(i["ID"])).fetchone()
            if curseur.execute("SELECT * FROM evol{0}{1}{2} WHERE Rank<30".format(moisDB,anneeDB,i["ID"])).fetchone()!=None and hide!=None and not hide["Hide"]:
                ids.append(i["ID"])
        elif option in ("salons","voicechan"):
            hide=curseurGuild.execute("SELECT * FROM chans WHERE ID={0}".format(i["ID"])).fetchone()
            if curseur.execute("SELECT * FROM evol{0}{1}{2} WHERE Rank<30".format(moisDB,anneeDB,i["ID"])).fetchone()!=None and hide!=None and not hide["Hide"]:
                ids.append(i["ID"])
        else:
            if curseur.execute("SELECT * FROM evol{0}{1}{2} WHERE Rank<30".format(moisDB,anneeDB,i["ID"])).fetchone()!=None:
                ids.append(i["ID"])

    dictInfos={}
    for i in ids:
        if option in ("messages","voice","mots"):
            infos=getUserInfo(i,curseurGet,guild)
        else:
            nom=getNom(i,option,curseurGet,False)
            infos={"ID":i,"Nom":nom,"Color":None}
        dictInfos[i]=infos
    connexionRap,curseurRap=connectSQL(guild,"Rapports","Stats","GL","")
    if moisDB=="glob":
        dates=curseurRap.execute("SELECT DISTINCT Jour,Mois,Annee FROM ranks WHERE Type='{0}' ORDER BY DateID ASC".format(dictOptions[option])).fetchall()
        dates=collapseAnim(dates)
    elif moisDB=="to":
        dates=curseurRap.execute("SELECT DISTINCT Jour,Mois,Annee FROM ranks WHERE Annee='{0}' AND Type='{1}' ORDER BY DateID ASC".format(anneeDB,dictOptions[option])).fetchall()
        dates=collapseAnim(dates)
    else:
        dates=curseurRap.execute("SELECT DISTINCT Jour FROM ranks WHERE Mois='{0}' AND Annee='{1}' AND Type='{2}' ORDER BY Jour ASC".format(tableauMois[moisDB],anneeDB,dictOptions[option])).fetchall()

    maxi=table[0]["Count"]
    plus,div=voiceAxe(option,[maxi])
    
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }
    fig_dict["layout"]["xaxis"] = {'categoryorder':'total descending', "title": "Rang", "automargin":True,"range":[0,15.5 if len(table)>15 else len(table)+0.5], "showgrid":False}
    fig_dict["layout"]["yaxis"] = {"title": enteteCount(option)+plus,"range":[0,round(maxi/div,2)*1.1]}
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

    jour = dates[0]
    for membre in ids:
        if moisDB=="glob":
            evol=curseur.execute("SELECT * FROM evol{0}{1}{2} WHERE Jour='{3}' AND Mois='{4}' AND Annee='{5}'".format(moisDB,anneeDB,membre,jour["Jour"],jour["Mois"],jour["Annee"])).fetchone()
        elif moisDB=="to":
            evol=curseur.execute("SELECT * FROM evol{0}{1}{2} WHERE Jour='{3}' AND Mois='{4}'".format(moisDB,anneeDB,membre,jour["Jour"],jour["Mois"])).fetchone()
        else:
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
                "y": [0,round(evol["Count"]/div,2)],
                "name": membre,
                "mode": "lines+text",
                "text": [round(evol["Count"]/div,2),dictInfos[membre]["Nom"]],
                "textposition":"top center",
                "line":{"color":dictInfos[membre]["Color"],"width":14}
            }
        fig_dict["data"].append(data_dict)

    
    for jour in dates:
        if moisDB=="glob":
            formatDate="{0}/{1}/20{2}".format(jour["Jour"],jour["Mois"],jour["Annee"])
        elif moisDB=="to":
            formatDate="{0}/{1}/20{2}".format(jour["Jour"],jour["Mois"],anneeDB)
        else:
            formatDate="{0}/{1}/20{2}".format(jour["Jour"],tableauMois[moisDB],anneeDB)
        frame = {"data": [], "name":formatDate }
        for membre in ids:
            if moisDB=="glob":
                evol=curseur.execute("SELECT * FROM evol{0}{1}{2} WHERE Jour='{3}' AND Mois='{4}' AND Annee='{5}'".format(moisDB,anneeDB,membre,jour["Jour"],jour["Mois"],jour["Annee"])).fetchone()
            elif moisDB=="to":
                evol=curseur.execute("SELECT * FROM evol{0}{1}{2} WHERE Jour='{3}' AND Mois='{4}'".format(moisDB,anneeDB,membre,jour["Jour"],jour["Mois"])).fetchone()
            else:
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
                    "y": [0,round(evol["Count"]/div,2)],
                    "name": membre,
                    "mode": "lines+text",
                    "text": [round(evol["Count"]/div,2),dictInfos[membre]["Nom"]],
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


def pointPlot(guild,option,curseur,curseurGet,curseurGuild,moisDB,anneeDB,categ):
    listeNow,listeMed,listeMax,listeMoy,listeNoms=[],[],[],[],[]
    listeRankNow,listeRankMed,listeRankMax,listeRankMoy=[],[],[],[]
    listeIDs=[]
    moisPoint=curseur.execute("SELECT * FROM {0}{1} WHERE Rank<=15 ORDER BY Rank DESC".format(moisDB,anneeDB)).fetchall()
    
    for i in moisPoint:
        if option in ("messages","voice","mots"):
            hide=curseurGuild.execute("SELECT * FROM users WHERE ID={0}".format(i["ID"])).fetchone()
            if hide==None or hide["Hide"]:
                continue
            infos=getUserInfo(i["ID"],curseurGet,guild)
            listeNoms.append(infos["Nom"])
        elif categ=="Jeux":
            connexionUser,curseurUser=connectSQL("OT",i["ID"],"Titres",None,None)
            infos=getAllInfos(curseurGet,curseurUser,connexionUser,i["ID"])
            listeNoms.append(infos["Full"])
        else:
            if option in ("salons","voicechan"):
                hide=curseurGuild.execute("SELECT * FROM chans WHERE ID={0}".format(i["ID"])).fetchone()
                if hide==None or hide["Hide"]:
                    continue
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

    plus,div=voiceAxe(option,listeMax)
    for i in range(len(listeNow)):
        listeNow[i]=round(listeNow[i]/div,2)
    for i in range(len(listeMed)):
        listeMed[i]=round(listeMed[i]/div,2)
    for i in range(len(listeMoy)):
        listeMoy[i]=round(listeMoy[i]/div,2)
    
    if moisDB=="to": 
        figCount.add_trace(go.Scatter(x=listeNow,y=listeIDs,marker=dict(color="crimson", size=12),mode="markers",name="Cette année"))
        figRank.add_trace(go.Scatter(x=listeRankNow,y=listeIDs,marker=dict(color="crimson", size=12),mode="markers",name="Cette année"))
    else:
        figCount.add_trace(go.Scatter(x=listeNow,y=listeIDs,marker=dict(color="crimson", size=12),mode="markers",name="Ce mois-ci"))
        figRank.add_trace(go.Scatter(x=listeRankNow,y=listeIDs,marker=dict(color="crimson", size=12),mode="markers",name="Ce mois-ci"))

    figCount.add_trace(go.Scatter(x=listeMed,y=listeIDs,marker=dict(color="gold", size=8),mode="markers",name="Médiane"))
    figCount.add_trace(go.Scatter(x=listeMoy,y=listeIDs,marker=dict(color="cyan", size=8),mode="markers",name="Moyenne"))
    figCount.add_trace(go.Scatter(x=listeMax,y=listeIDs,marker=dict(color="yellowgreen", size=8),mode="markers",name="Maximum"))
    figCount.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=600,title="Indicateurs sur le nombre de {0} pour le Top 15".format(enteteCount(option).lower()),xaxis_title=enteteCount(option)+plus,yaxis_title=enteteNom(option),legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
    figCount.update_yaxes(automargin=True,ticktext=listeNoms,tickvals=listeIDs)
    figCount.update_xaxes(showgrid=False, zeroline=False)

    figRank.add_trace(go.Scatter(x=listeRankMed,y=listeIDs,marker=dict(color="gold", size=8),mode="markers",name="Médiane"))
    figRank.add_trace(go.Scatter(x=listeRankMoy,y=listeIDs,marker=dict(color="turquoise", size=8),mode="markers",name="Moyenne"))
    figRank.add_trace(go.Scatter(x=listeRankMax,y=listeIDs,marker=dict(color="yellowgreen", size=8),mode="markers",name="Minimum"))
    figRank.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=600,title="Indicateurs sur les rangs pour le Top 15",xaxis_title="Rang",yaxis_title=enteteNom(option),legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
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
        labels[semaine][jour]="{0}/{1}/{2}<br>{3}".format(i["Jour"],mois,annee,formatCount(somme,option))

    listeHeat.reverse()
    labels.reverse()
    fig = go.Figure(data=go.Heatmap(
                    x=["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"],
                    z=listeHeat,
                    text=labels,
                    texttemplate="%{text}",
                    textfont={"size":11},
                    colorscale="YlGnBu"))
                    
    fig.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=500,title="Calendrier {0} chaque jour du mois".format(enteteCount(option)))
    fig.update_yaxes(automargin=True, showgrid=False, zeroline=False)
    fig.update_xaxes(showgrid=False, zeroline=False)
    return plot(fig,output_type='div')


def heatmapAnnee(guild,option,annee):
    annee=annee[2:4]
    listeMois=["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Aout","Septembre","Octobre","Novembre","Décembre"]
    listeMois.reverse()
    listeHeat=[[None]*31 for i in range(12)]
    labels=[[""]*31 for i in range(12)]
    connexion,curseur=connectSQL(guild,"Rapports","Stats","GL","")
    
    for i in range(12):
        try:
            mois=tableauMois[listeMois[i].lower()]            
            dates=curseur.execute("SELECT DISTINCT Jour FROM ranks WHERE Mois='{0}' AND Annee='{1}' AND Type='{2}'".format(mois,annee,dictOptions[option])).fetchall()
            for j in dates:
                somme=curseur.execute("SELECT SUM(Count) AS Total FROM ranks WHERE Jour='{0}' AND Mois='{1}' AND Annee='{2}' AND Type='{3}'".format(j["Jour"],mois,annee,dictOptions[option])).fetchone()["Total"]
                jour=int(j["Jour"])-1
                listeHeat[i][jour]=somme
                labels[i][jour]=formatCount(somme,option)
                if option in ("voice","voicechan"):
                    if len(labels[i][jour].split(" "))>=3:
                        descip=""
                        for z in range(len(labels[i][jour].split(" "))):
                            if z==2:
                                descip+="\n"
                            descip+=labels[i][jour].split(" ")[z]+" "
                        labels[i][jour]=descip
        except:
            pass
    
    i=0
    while i!=len(listeHeat):
        if listeHeat[i].count(None)==31:
            del listeHeat[i]
            del listeMois[i]
            del labels[i]
        else:
            i+=1

    fig = go.Figure(data=go.Heatmap(
                    x=[i for i in range(1,32)],
                    y=listeMois,
                    z=listeHeat,
                    text=labels,
                    texttemplate="%{text}",
                    textfont={"size":10},
                    colorscale="YlGnBu"))
                    
    fig.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",title="Calendrier {0} chaque jour d'activité du serveur sur l'année".format(enteteCount(option).lower()),height=600,xaxis_title="Jours",yaxis_title="Mois")
    fig.update_yaxes(automargin=True)
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
                    
    fig.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",title="Calendrier {0} chaque mois d'activité du serveur".format(enteteCount(option).lower()))
    fig.update_yaxes(automargin=True)
    return plot(fig,output_type='div')


def linePlot(guild,option,user,curseur,curseurGet,curseurGuild,categ,moisDB,anneeDB):
    table=curseur.execute("SELECT ID FROM {0}{1} ORDER BY Rank ASC".format(moisDB,anneeDB)).fetchall()

    connexionGL,curseurGL=connectSQL(guild,dictOptions[option],categ,"GL","")

    old10=curseurGL.execute("SELECT * FROM firstM WHERE DateID<={0}{1} ORDER BY DateID DESC".format(anneeDB,tableauMois[moisDB],)).fetchall()
    old10=old10[0:10] if len(old10)>10 else old10

    listeDates=[]
    listeX,listeY,listeR=[[],[],[],[]],[[],[],[],[]],[[],[],[],[]]
    mini=inf
    maxi=-inf

    stop=3 if len(table)>3 else len(table)
    ids=list(map(lambda x:x["ID"],table))[:stop]
    if user.id not in ids and (option in ("messages","voice","mots") or categ=="Jeux"):
        ids.append(user.id)
        stop+=1
    ids.reverse()
    
    
    if option in ("messages","voice","mots"):
        checked=[]
        for i in ids:
            hide=curseurGuild.execute("SELECT * FROM users WHERE ID={0}".format(i)).fetchone()
            if hide!=None and not hide["Hide"]:
                checked.append(i)
        ids=checked
        stop=len(ids)
    elif option in ("salons","voicechan"):
        checked=[]
        for i in ids:
            hide=curseurGuild.execute("SELECT * FROM chans WHERE ID={0}".format(i)).fetchone()
            if hide!=None and not hide["Hide"]:
                checked.append(i)
        ids=checked
        stop=len(ids)

    for i in range(stop-1,-1,-1):
        for j in range(len(old10)-1,-1,-1):
            connexionMois,curseurMois=connectSQL(guild,dictOptions[option],categ,old10[j]["Mois"],old10[j]["Annee"])
            count=curseurMois.execute("SELECT Count,Rank FROM {0}{1} WHERE ID={2}".format(tableauMois[old10[j]["Mois"]],old10[j]["Annee"],ids[i])).fetchone()
            if count!=None:
                if old10[j]["DateID"] not in listeDates:
                    listeDates.append(old10[j]["DateID"])
                listeX[i].append("{0}/{1}".format(old10[j]["Mois"],old10[j]["Annee"]))
                listeY[i].append(count["Count"])
                listeR[i].append("{0}e".format(count["Rank"]))
                mini=min(count["Count"],mini)
                maxi=max(count["Count"],maxi)

    plus,div=voiceAxe(option,[maxi])

    listeDates.sort()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=["{0}/{1}".format(str(i)[2:4],str(i)[0:2]) for i in listeDates], y=[mini/div//1.5 for i in range(len(listeDates))],mode='none',name=""))

    dictLine={2:"dash",3:"dot"}
    colors=[]

    for i in range(stop):
        for j in range(len(listeY[i])):
            listeY[i][j]=round(listeY[i][j]/div,2)
        if option in ("messages","voice","mots"):
            infos=getUserInfo(ids[i],curseurGet,guild)
            color=infos["Color"]
            nom=infos["Nom"]
        elif categ=="Jeux":
            connexionUser,curseurUser=connectSQL("OT",ids[i],"Titres",None,None)
            infos=getAllInfos(curseurGet,curseurUser,connexionUser,ids[i])
            nom=infos["Full"]
            color=infos["Color"]
        else:
            nom=getNom(ids[i],option,curseurGet,False)
            color=None
        
        colors.append(color)
        count=colors.count(color)
        if count==1:
            fig.add_trace(go.Scatter(x=listeX[i], y=listeY[i],mode='lines+markers+text',name=nom,marker=dict(color=color, size=12),line=dict(color=color),text=listeR[i],textposition="top center"))
        else:
            fig.add_trace(go.Scatter(x=listeX[i], y=listeY[i],mode='lines+markers+text',name=nom,marker=dict(color=color, size=12),line=dict(color=color,dash=dictLine[count]),text=listeR[i],textposition="top center"))

    fig.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=600,title="Évolution des trois premiers du classement sur les 10 derniers mois",xaxis_title="Dates",yaxis_title=enteteCount(option)+plus,hovermode="x unified",legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(showgrid=False, zeroline=False)
    return plot(fig,output_type='div')
