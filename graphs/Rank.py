import plotly.graph_objects as go
from companion.Getteurs import (getChannels, getEmoteTable, getFreq,
                                getUserTable)
from plotly.offline import plot


def graphRank(guild,option,user,curseur,curseurGet,moisDB,anneeDB,circular):
    old=1
    colors=[]
    counts=[]
    ranks=[]
    names=[]

    for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC".format(moisDB,anneeDB)).fetchall():
        if i["ID"]==user.id:
            flag=True

        if option in ("messages","voice","mots"):
            ligne=getUserTable(i,curseurGet,guild)

        elif option in ("emotes","reactions"):
            ligne=getEmoteTable(i,curseurGet)

        elif option in ("salons","voicechan"):
            ligne=getChannels(i,curseurGet)

        elif option=="freq":
            ligne=getFreq(i)

        if ligne["Nom"]=="Ancien membre":
            old+=1
            colors.append("rgb(110,200,250)")
        else:
            colors.append(ligne["Color"])

        if len(ligne["Nom"])<15:
            names.append(ligne["Nom"])
        else:
            names.append(ligne["Nom"][:15]+"...")

        counts.append(i["Count"])
        ranks.append(i["Rank"])    
    
    fig=go.Figure(data=go.Bar(x=names,y=counts,marker_color=colors,text=counts,textposition="auto"))
    
    fig.update_layout(
        
        paper_bgcolor="#111",
        plot_bgcolor="#333",
        font_family="Roboto",
        font_color="white",
        xaxis={
            'categoryorder':'total descending',
            "rangeslider":{"visible":True},
            "title":"Membres"},
        yaxis_title="Messages",
        height=750,
        title="Messages envoyés sur la période globale"
    )
    fig.update_yaxes(automargin=True)

    if circular:
        if len(names)>10:
            names=names[0:10]+["Autres membres"]
            counts=counts[0:10]+[sum(counts[10:])]
            colors=colors[0:10]+["rgb(110,200,250)"]

        figCirc=go.Figure(data=go.Pie(labels=names,values=counts))
        figCirc.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=750,title="Top 10 VS Le reste")
        figCirc.update_traces(marker_colors=colors)
        figCirc.update_yaxes(automargin=True)

        return plot(fig,output_type='div'), plot(figCirc,output_type='div')
    else:
        return plot(fig,output_type='div')
