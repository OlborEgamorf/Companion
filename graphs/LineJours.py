import plotly.graph_objects as go
from companion.graphs.Evol import xaxeEvol
from companion.outils import getTableDay, tableauMois
from plotly.offline import plot


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
