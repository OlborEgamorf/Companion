from math import inf

import plotly.graph_objects as go
from companion.templatetags.TagsCustom import enteteCount, enteteNom
from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import (chooseGetteur, getAllInfos, getNom,
                                      getPin, getUserInfo)
from companion.tools.outils import (connectSQL, dictOptions, getTablePerso,
                                    listeOptions, listeOptionsJeux,
                                    tableauMois, voiceAxe)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from plotly.offline import plot


def graphFirstJeux(request,option):
    return graphFirst(request,"OT",option)

def iFrameGraphFirstJeux(request,option):
    return iFrameGraphFirst(request,"OT",option)

@login_required(login_url="/login")
@CompanionStats
def graphFirst(request,guild,option):
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
        connexionUser,curseurUser=connectSQL("OT",user.id,"Titres",None,None)
        infos=getAllInfos(curseurGet,curseurUser,connexionUser,user.id)
    else:
        categ="Stats"
        guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
        infos=getUserInfo(user.id,curseurGet,guild)
    
    connexion,curseur=connectSQL(guild,dictOptions[option],categ,"GL","")
    div1,div2=linePlot(guild,option,user,infos["Color"],curseur,curseurGet,curseurGuild,True,categ)

    #connexion.close()
    if categ=="Jeux":
        ctx={"fig":div1,"fig2":div2,"fig3":None,"fig4":None,"fig5":None,"fig6":None,"fig7":None,"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"guildname":"Classements jeux","guildid":"ot/jeux","pagestats":True,"ot":True,
        "command":"first","options":listeOptionsJeux,"option":option,"plus":"graphs","travel":False,"selector":True,"obj":None,
        "pin":getPin(user,curseurGet,"ot/jeux",option,"evol","graphs")}
    else:
        ctx={"fig":div1,"fig2":div2,"fig3":None,"fig4":None,"fig5":None,"fig6":None,"fig7":None,"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],"pagestats":True,
        "command":"first","options":listeOptions,"option":option,"plus":"graphs","travel":False,"selector":True,"obj":None,
        "pin":getPin(user,curseurGet,guild,option,"evol","graphs")}
    return render(request, "companion/Stats/Graphiques.html", ctx)


@login_required(login_url="/login")
def iFrameGraphFirst(request,guild,option):
    user=request.user

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
        connexionGet,curseurGet=connectSQL("OT","Titres","Titres",None,None)
    else:
        categ="Stats"
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)

    connexion,curseur=connectSQL(guild,dictOptions[option],categ,"GL","")
    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)

    stats=[]
    maxi=-inf
    for i in curseur.execute("SELECT * FROM firstM ORDER BY DateID DESC").fetchall():
        i["Rank"]=0
        if categ=="Jeux":
            i["W"]=0
            i["L"]=0

        ligne=chooseGetteur(option,categ,i,guild,curseurGet,curseurGuild)

        ligne["Mois"]=i["Mois"]
        ligne["Annee"]=i["Annee"]
        stats.append(ligne)

        maxi=max(maxi,i["Count"])

    ctx={"rank":stats,"id":user.id,"max":maxi,"option":option,"plus":"graph"}
    return render(request, "companion/Stats/First/iFrameFirstGraph.html", ctx)

def linePlot(guild,option,user,color,curseur,curseurGet,curseurGuild,graphnb,categ,annee=None):
    if annee==None or annee=="":
        first=curseur.execute("SELECT * FROM firstM ORDER BY DateID ASC").fetchall()
    else:
        first=curseur.execute("SELECT * FROM firstM WHERE Annee='{0}' ORDER BY DateID ASC".format(annee)).fetchall()
    
    moy=[]
    noms=[]
    ids=[]
    dictNoms={}
    dictColors={}

    for i in first:
        connexionMois,curseurMois=connectSQL(guild,dictOptions[option],categ,i["Mois"],i["Annee"])
        mois=curseurMois.execute("SELECT AVG(Count) AS Moy FROM {0}{1}".format(tableauMois[i["Mois"]],i["Annee"])).fetchone()
        if mois!=None:
            moy.append({"DateID":i["DateID"],"Mois":i["Mois"],"Annee":i["Annee"],"Count":mois["Moy"]})
        if option in ("messages","voice","mots"):
            hide=curseurGuild.execute("SELECT * FROM users WHERE ID={0}".format(i["ID"])).fetchone()
            if hide==None or hide["Hide"]:
                nom="Membre masqué"
                hexa="turquoise"
                i["Count"]=0
            infos=getUserInfo(i["ID"],curseurGet,guild)
            nom=infos["Nom"]
            hexa=infos["Color"]
        elif categ=="Jeux":
            connexionUser,curseurUser=connectSQL("OT",i["ID"],"Titres",None,None)
            infos=getAllInfos(curseurGet,curseurUser,connexionUser,i["ID"])
            nom=infos["Full"]
            if infos["Color"]!=None:
                hexa=infos["Color"]
            else:
                hexa="turquoise"
        else:
            if option in ("salons","voicechan"):
                hide=curseurGuild.execute("SELECT * FROM chans WHERE ID={0}".format(i["ID"])).fetchone()
                if hide!=None or not hide["Hide"]:
                    nom="Salon masqué"
                    i["Count"]=0
            else:
                nom=getNom(i["ID"],option,curseurGet,False)
            hexa="turquoise"

        noms.append(nom)
        ids.append(i["ID"])
        
        dictNoms[i["ID"]]=nom
        dictColors[i["ID"]]=hexa

    listeCount=list(map(lambda x:x["Count"],first))
    plus,div=voiceAxe(option,listeCount)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(map(lambda x:"20{1}-{0}".format(x["Mois"],x["Annee"]),first)), 
        y=listeCount, 
        text=noms, 
        mode='lines+markers', 
        marker=dict(color="gold", size=10), 
        line=dict(color="gold"), 
        textposition="top center",
        hovertemplate = "%{y}<br>%{text}",
        name="Premiers"))
    
    if option in ("messages","voice","mots") or categ=="Jeux":
        perso=getTablePerso(guild,dictOptions[option],user.id,False,"M","periodAsc")
        listeCount=list(map(lambda x:x["Count"],perso))
        # FILTER POUR METTRE QUE ANNEE
        for i in range(len(listeCount)):
            listeCount[i]=round(listeCount[i]/div,2)
        fig.add_trace(go.Scatter(
            x=list(map(lambda x:"20{1}-{0}".format(x["Mois"],x["Annee"]),perso)), 
            y=listeCount, 
            text=list(map(lambda x:x["Rank"],perso)), 
            mode='lines+markers', 
            marker=dict(color=color, size=10), 
            line=dict(color=color), 
            hovertemplate = "%{y}<br>%{text}e",
            name="Vous"))

    listeCount=list(map(lambda x:x["Count"],moy))
    for i in range(len(listeCount)):
        listeCount[i]=round(listeCount[i]/div,2)

    fig.add_trace(go.Scatter(
        x=list(map(lambda x:"20{1}-{0}".format(x["Mois"],x["Annee"]),moy)), 
        y=listeCount, 
        text=noms, 
        mode='lines+markers', 
        marker=dict(color="turquoise", size=10), 
        line=dict(color="turquoise"), 
        hovertemplate = "%{y}",
        name="Moyenne du serveur"))

    fig.update_layout(paper_bgcolor="#222",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Pour chaque mois d'activité, comparaison entre vous, le premier, et la moyenne du serveur en terme de {0}".format(enteteCount(option).lower()),xaxis_title="Date",yaxis_title=enteteCount(option)+plus,hovermode="x")
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(showgrid=False, zeroline=False,rangeslider_visible=True,type="date",rangeselector=dict(font_color="#222",
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

    if graphnb:
        idsDist=curseur.execute("SELECT DISTINCT ID FROM firstM").fetchall()
        nbfirst=[]
        colorsNb=[]
        nomsNb=[]
        for i in idsDist:
            if option in ("messages","voice"):
                hide=curseurGuild.execute("SELECT * FROM users WHERE ID={0}".format(i["ID"])).fetchone()
                if hide==None or hide["Hide"]:
                    continue
            elif option in ("salons","voicechan"):
                hide=curseurGuild.execute("SELECT * FROM chans WHERE ID={0}".format(i["ID"])).fetchone()
                if hide==None or hide["Hide"]:
                    continue
            nbfirst.append({"ID":i["ID"],"Count":curseur.execute("SELECT Count() AS Nombre FROM firstM WHERE ID={0}".format(i["ID"])).fetchone()["Nombre"]})
            nomsNb.append(dictNoms[i["ID"]])
            colorsNb.append(dictColors[i["ID"]])
        counts=list(map(lambda x:x["Count"],nbfirst))

        figNb=go.Figure(data=go.Bar(x=list(map(lambda x:str(x["ID"]),idsDist)),y=counts,marker_color=colorsNb,text=counts,textposition="auto"))

        figNb.update_layout(
            
            paper_bgcolor="#222",
            plot_bgcolor="#333",
            font_family="Roboto",
            font_color="white",
            xaxis={
                'categoryorder':'total descending',
                "rangeslider":{"visible":True},
                "title":enteteNom(option),
                "range":[-0.5,20.5 if len(nbfirst)>20 else len(nbfirst)+0.5]},
            yaxis_title="Nombre de fois premier",
            height=750,
            title="Nombre de fois premiers au classement"
        )
        figNb.update_yaxes(automargin=True)
        figNb.update_xaxes(ticktext=nomsNb,tickvals=list(map(lambda x:str(x["ID"]),idsDist)))

        return plot(fig,output_type='div'), plot(figNb,output_type='div')
    return plot(fig,output_type='div')
