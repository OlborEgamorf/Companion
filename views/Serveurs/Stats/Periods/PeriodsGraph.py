from math import inf

import plotly.graph_objects as go
from companion.templatetags.TagsCustom import enteteCount
from companion.tools.Decorator import CompanionStats
from companion.tools.Getteurs import (getAllInfos, getPin, getUserInfo,
                                      objSelector)
from companion.tools.outils import (connectSQL, dictOptions, getTablePerso,
                                    listeOptions, listeOptionsJeux, voiceAxe)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from plotly.offline import plot


def graphPeriodsJeux(request,option):
    return graphPeriods(request,"OT",option)

def iFrameGraphPeriodsJeux(request,option):
    return iFrameGraphPeriods(request,"OT",option)


@login_required(login_url="/login")
@CompanionStats
def graphPeriods(request,guild,option):
    obj = request.GET.get("obj")
    user=request.user

    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
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

    connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
    listeObj=objSelector(guild,option,categ,user,curseurGet,curseurGuild)

    if option not in ("messages","voice","mots") and categ!="Jeux":
        if obj==None:
            obj=listeObj[0]["ID"]
    
    if option in ("messages","voice","mots") or categ=="Jeux":
        div1,div2,div3,div4=linePlot(guild,option,user.id,False,infos["Color"],True,"M")
        div5,div6,div7=linePlot(guild,option,user.id,False,"turquoise",False,"M")
        div8=None
    else:
        div1,div2,div3,div4=linePlot(guild,option,user.id,obj,infos["Color"],True,"M")
        div5,div6,div7,div8=linePlot(guild,option,user.id,obj,"turquoise",False,"M")

    #connexion.close()
    if categ=="Jeux":
        ctx={"fig":div1,"fig2":div2,"fig3":div3,"fig4":div4,"fig5":div5,"fig6":div6,"fig7":div7,"fig8":div8,"pagestats":True,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"guildname":"Classements jeux","guildid":"ot/jeux",
        "command":"periods","options":listeOptionsJeux,"option":option,"plus":"graphs",
        "travel":False,"selector":True,"obj":obj,"listeObjs":listeObj,"ot":True,
        "pin":getPin(user,curseurGet,"ot/jeux",option,"periods","graphs")}
    else:
        ctx={"fig":div1,"fig2":div2,"fig3":div3,"fig4":div4,"fig5":div5,"fig6":div6,"fig7":div7,"fig8":div8,"pagestats":True,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "command":"periods","options":listeOptions,"option":option,"plus":"graphs",
        "travel":False,"selector":True,"obj":obj,"listeObjs":listeObj,
        "pin":getPin(user,curseurGet,guild,option,"periods","graphs")}
    return render(request, "companion/Stats/Periods/graphPeriods.html", ctx)


@login_required(login_url="/login")
def iFrameGraphPeriods(request,guild,option):
    obj=request.GET.get("data")
    user=request.user

    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        categ="Jeux"
    else:
        categ="Stats"

    if option in ("messages","voice","mots") or categ=="Jeux":
        tableUser=getTablePerso(guild,dictOptions[option],user.id,False,"M","periodAsc")
        tableServ=getTablePerso(guild,dictOptions[option],guild,False,"M","periodAsc")
    else:
        tableUser=getTablePerso(guild,dictOptions[option],user.id,obj,"M","periodAsc")
        tableServ=getTablePerso(guild,dictOptions[option],obj,False,"M","periodAsc")
    maxiUser=max(tableUser,key=lambda x:x["Count"])
    maxiServ=max(tableServ,key=lambda x:x["Count"])

    ctx={"user":tableUser,"serv":tableServ,"id":user.id,"maxUser":maxiUser,"maxServ":maxiServ,"option":option,"plus":"graph"}
    return render(request, "companion/Stats/Periods/iFramePeriodsGraph.html", ctx)


def linePlot(guild,option,user,obj,color,perso,period):
    if perso:
        if obj!=False:
            table=getTablePerso(guild,dictOptions[option],user,obj,period,"periodAsc")
        else:
            table=getTablePerso(guild,dictOptions[option],user,False,period,"periodAsc")
        listeRanks=list(map(lambda x:x["Rank"], table))
    else:
        if obj!=False:
            table=getTablePerso(guild,dictOptions[option],obj,False,period,"periodAsc")
            listeRanks=list(map(lambda x:x["Rank"], table))
        else:
            table=getTablePerso(guild,dictOptions[option],guild,False,period,"periodAsc")

    listeLabels=list(map(lambda x:"20{1}-{0}".format(x["Mois"],x["Annee"]),table))
    listeCount=list(map(lambda x:x["Count"], table))
    plus,div=voiceAxe(option,listeCount)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=listeLabels, y=listeCount, text=listeCount, mode='lines+markers+text', marker=dict(color=color, size=12), line=dict(color=color), textposition="top center",hovertemplate = "%{y}",name="Courbe"))

    fig.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Périodes d'activité - évolution {0}".format(enteteCount(option).lower()),xaxis_title="Dates",yaxis_title=enteteCount(option)+plus,hovermode="x")
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
            figAn.add_trace(go.Scatter(x=mois, y=listeCount[save:i], text=listeCount[save:i], mode='lines+markers+text', marker=dict(color=colors[nb], size=10), line=dict(color=colors[nb]), textposition="top center",name="20{0}".format(act),hovertemplate = "%{y}"))
            save=i
            liste=[table[i]["Count"]]
            act=table[i]["Annee"]
            mois=[int(table[i]["Mois"])]
            nb+=1
        else:
            liste.append(table[i]["Count"])
            mois.append(int(table[i]["Mois"]))

    if save!=i:
        figAn.add_trace(go.Scatter(x=mois, y=listeCount[save:], text=listeCount[save:], mode='lines+markers+text', marker=dict(color=colors[nb], size=10), line=dict(color=colors[nb]), textposition="top center",name="20{0}".format(act),hovertemplate = "%{y}"))
    figAn.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Périodes d'activité - mise en parallèle de chaque année",xaxis_title="Dates",yaxis_title=enteteCount(option)+plus,hovermode="x")
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

    if perso or obj!=False:
        figRanks = go.Figure()
        figRanks.add_trace(go.Scatter(x=listeLabels, y=listeRanks, text=listeRanks, mode='lines+markers+text', marker=dict(color=color, size=12), line=dict(color=color), textposition="top center",hovertemplate = "%{y}",name="Courbe"))

        figRanks.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",height=800,title="Périodes d'activité - évolution du rang",xaxis_title="Dates",yaxis_title="Rang",hovermode="x")
        figRanks.update_yaxes(automargin=True,autorange="reversed")
        figRanks.update_xaxes(showgrid=False, zeroline=False,rangeslider_visible=True,type="date",rangeselector=dict(font_color="#111",
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

        return plot(fig,output_type='div'), plot(figRanks,output_type='div'),  plot(figAn,output_type='div'), plot(figBox,output_type='div')
    else:
        return plot(fig,output_type='div'), plot(figAn,output_type='div'), plot(figBox,output_type='div')
