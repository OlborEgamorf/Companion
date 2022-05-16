import plotly.graph_objects as go
from companion.outils import getTablePerso
from plotly.offline import plot

def graphLinePeriods(guild,option,user,color,perso,period):
    if perso:
        table=getTablePerso(guild,option,user.id,False,period,"periodAsc")
        listeRanks=list(map(lambda x:x["Rank"], table))
    else:
        table=getTablePerso(guild,option,guild,False,period,"periodAsc")

    listeLabels=list(map(lambda x:"20{1}-{0}".format(x["Mois"],x["Annee"]),table))
    listeCount=list(map(lambda x:x["Count"], table))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=listeLabels, y=listeCount, text=listeCount, mode='lines+markers+text', marker=dict(color=color, size=12), line=dict(color=color), textposition="top center"))

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

    figAn = go.Figure()
    colors=["green","red","cyan","turquoise","gold","yellowgreen","orange"]
    liste=[]
    save=0
    act=table[0]["Annee"]
    nb=0
    
    mois=[]
    for i in range(len(listeCount)):
        if act!=table[i]["Annee"]:
            figAn.add_trace(go.Scatter(x=mois, y=listeCount[save:i], text=listeCount[save:i], mode='lines+markers+text', marker=dict(color=colors[nb], size=10), line=dict(color=colors[nb]), textposition="top center",name="20{0}".format(act)))
            save=i
            liste=[table[i]["Count"]]
            act=table[i]["Annee"]
            mois=[int(table[i]["Mois"])]
            nb+=1
        else:
            liste.append(table[i]["Count"])
            mois.append(int(table[i]["Mois"]))

    figAn.add_trace(go.Scatter(x=mois, y=listeCount[save:i], text=listeCount[save:i], mode='lines+markers+text', marker=dict(color=colors[nb], size=10), line=dict(color=colors[nb]), textposition="top center",name="20{0}".format(act)))
    figAn.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Périodes - Comparaison de chaque année",xaxis_title="Dates",yaxis_title="Messages",hovermode="x")
    figAn.update_yaxes(automargin=True)
    figAn.update_xaxes(showgrid=False, zeroline=False,categoryorder='category ascending',ticktext=["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Aout","Septembre","Octobre","Novembre","Décembre"],tickvals=[1,2,3,4,5,6,7,8,9,10,11,12])

    figAn.update_layout(updatemenus=[dict(
        type = "buttons",
        direction = "left",
        buttons=list([
            dict(
                args=["type", "scatter"],
                label="Lignes",
                method="restyle"),
            dict(
                args=["type", "bar"],
                    label="Barres",
                    method="restyle")]),
        pad={"r": 10, "t": 10},
        showactive=True,
        x=0,
        xanchor="left",
        y=1,
        yanchor="top",
        font_color="cyan")])

    figBox=go.Figure()
    figBox.add_trace(go.Box(x=listeCount,marker_color=color))
    figBox.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=500,title="Périodes - Boxplot",xaxis_title="Messages",)
    figBox.update_xaxes(automargin=True)

    if perso:
        figRanks = go.Figure()
        figRanks.add_trace(go.Scatter(x=listeLabels, y=listeRanks, text=listeRanks, mode='lines+markers+text', marker=dict(color=color, size=12), line=dict(color=color), textposition="top center"))

        figRanks.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Périodes - Rangs",xaxis_title="Dates",yaxis_title="Rangs",hovermode="x")
        figRanks.update_yaxes(automargin=True,autorange="reversed")
        figRanks.update_xaxes(showgrid=False, zeroline=False,rangeslider_visible=True)

        return plot(fig,output_type='div'), plot(figRanks,output_type='div'),  plot(figAn,output_type='div'), plot(figBox,output_type='div')
    else:
        return plot(fig,output_type='div'), plot(figAn,output_type='div'), plot(figBox,output_type='div')
