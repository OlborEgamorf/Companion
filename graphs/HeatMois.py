import calendar
import plotly.graph_objects as go
from companion.outils import connectSQL, dictOptions
from companion.templatetags.TagsCustom import formatCount
from plotly.offline import plot

tableauMois={"01":"janvier","02":"février","03":"mars","04":"avril","05":"mai","06":"juin","07":"juillet","08":"aout","09":"septembre","10":"octobre","11":"novembre","12":"décembre","TO":"TOTAL","1":"janvier","2":"février","3":"mars","4":"avril","5":"mai","6":"juin","7":"juillet","8":"aout","9":"septembre","janvier":"01","février":"02","mars":"03","avril":"04","mai":"05","juin":"06","juillet":"07","aout":"08","septembre":"09","octobre":"10","novembre":"11","décembre":"12"}
listeTitres={"Messages":"nombre de messages envoyés","Salons":"nombre de messages envoyés","Freq":"nombre de messages envoyés","Emotes":"nombre d'emotes utilisées","Reactions":"nombre de réactions utilisées","Voice":"temps passé en vocal","Voicechan":"temps passé en vocal"}

def heatMois(guild,option,mois,annee):
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
                    
    fig.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",width=1000,height=500,title="Calendrier des messages envoyés")
    fig.update_yaxes(automargin=True)
    return plot(fig,output_type='div')
    
    
