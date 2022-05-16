import plotly.graph_objects as go
from companion.Getteurs import getNom, getUserInfo
from companion.outils import getTablePerso,dictOptions
from plotly.offline import plot


def graphPoint(guild,option,curseur,curseurGet,moisDB,anneeDB):
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
