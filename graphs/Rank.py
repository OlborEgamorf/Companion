import time
import plotly.graph_objects as go
from companion.Getteurs import (getChannels, getEmoteTable, getFreq, getNom, getUserInfo,
                                getUserTable)
from plotly.offline import plot

from companion.outils import connectSQL, dictOptions, tableauMois


def graphRank(guild,option,user,curseur,curseurGet,moisDB,anneeDB,circular):
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




def graphAnim(guild,option,curseur,curseurGet,moisDB,anneeDB):
    temps=time.time()
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
    print(time.time()-temps)
    return plot(fig,output_type='div')
