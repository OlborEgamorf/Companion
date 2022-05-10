import plotly.graph_objects as go
from companion.outils import connectSQL, dictOptions, tableauMois
from companion.templatetags.TagsCustom import formatCount
from plotly.offline import plot


def heatGlobal(guild,option,curseur):
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
