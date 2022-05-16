from math import inf
import plotly.graph_objects as go
from companion.Getteurs import getNom, getUserInfo
from companion.outils import connectSQL, dictOptions, tableauMois
from companion.templatetags.TagsCustom import formatCount
from plotly.offline import plot

def graphLine(guild,option,user,curseur,curseurGet,mois,annee,moisDB,anneeDB):
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