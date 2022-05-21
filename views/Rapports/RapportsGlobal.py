import plotly.graph_objects as go
from companion.Getteurs import (addInfos, formatColor, getNom, getPin,
                                getUserInfo)
from companion.outils import (connectSQL, dictOptions, dictRefCommands,
                              dictRefOptions, dictRefPlus, getCommands,
                              getTimes, listeOptions, tableauMois)
from plotly.offline import plot


def rapportGlobal(guild,option,request,user,moisDB,anneeDB,mois,annee):
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
    
    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
    dictInfos={}

    top15_1=curseur.execute("SELECT * FROM glob ORDER BY Rank ASC LIMIT 15").fetchall()
    if option in ("messages","voice","mots"):
        top15_2=curseur.execute("SELECT * FROM glob ORDER BY Rank ASC LIMIT 30").fetchall()
        if len(top15_2)<=15:
            top15_2=None
        else:
            top15_2=top15_2[15:]
            for i in top15_2:
                infos=getUserInfo(i["ID"],curseurGet,guild)
                i["Nom"]=infos["Nom"]
                i["Avatar"]=infos["Avatar"]
                i["Color"]=formatColor(infos["Color"])
                dictInfos[i["ID"]]=infos
        for i in top15_1:
            infos=getUserInfo(i["ID"],curseurGet,guild)
            i["Nom"]=infos["Nom"]
            i["Avatar"]=infos["Avatar"]
            i["Color"]=formatColor(infos["Color"])
            dictInfos[i["ID"]]=infos
        
    else:
        for i in top15_1:
            i["Nom"]=getNom(i["ID"],option,curseurGet,False)
            dictInfos[i["ID"]]=i["Nom"]
        try:
            top15_2=curseur.execute("SELECT * FROM persoTOGL{0} ORDER BY Count DESC LIMIT 15".format(user.id)).fetchall()
            for i in top15_2:
                i["Nom"]=getNom(i["ID"],option,curseurGet,False)
                dictInfos[i["ID"]]=i["Nom"]
        except:
            top15_2=[]

    mini=curseur.execute("SELECT MIN(Count) AS Mini FROM glob").fetchone()["Mini"]
    maxi=curseur.execute("SELECT MAX(Count) AS Maxi FROM glob").fetchone()["Maxi"]
    moy=curseur.execute("SELECT AVG(Count) AS Moy FROM glob").fetchone()["Moy"]
    som=curseur.execute("SELECT SUM(Count) AS Somme FROM glob").fetchone()["Somme"]
    try:
        vous=curseur.execute("SELECT Count FROM glob WHERE ID={0}".format(user.id)).fetchone()["Count"]
    except:
        vous=None

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        value = mini,
        mode = "gauge+number",
        title = {'text': "Valeur minimale"},
        gauge = {'axis': {'range': [None, maxi]},},
        domain = {'row': 0, 'column': 0}))
    
    fig.add_trace(go.Indicator(
        value = maxi,
        mode = "gauge+number",
        title = {'text': "Valeur maximale"},
        gauge = {'axis': {'range': [None, maxi]},},
        domain = {'row': 0, 'column': 1}))
    
    fig.add_trace(go.Indicator(
        value = moy,
        mode = "gauge+number",
        title = {'text': "Valeur moyenne"},
        gauge = {'axis': {'range': [None, maxi]},},
        domain = {'row': 1, 'column': 0}))
    
    if option in ("messages","voice","mots"):
        fig.add_trace(go.Indicator(
            value = vous,
            mode = "gauge+number+delta",
            title = {'text': "Vous"},
            gauge = {'axis': {'range': [None, maxi]},},
            domain = {'row': 1, 'column': 2}))
    
    fig.add_trace(go.Indicator(
        value = som,
        mode = "gauge+number+delta",
        title = {'text': "Total"},
        gauge = {'axis': {'range': [None, som]}},
        domain = {'row': 1, 'column': 1}))

    fig.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",grid = {'rows': 2, 'columns': 3, 'pattern': "independent"},width=1000,height=550)
    div=plot(fig,output_type='div')

    connexionArc,curseurArc=connectSQL(guild,"Rapports","Stats","GL","")
    premiers=curseurArc.execute("SELECT * FROM archives WHERE Type='{0}' AND Periode='Global' AND Rank=1 ORDER BY DateID ASC".format(dictOptions[option])).fetchall()
    if len(premiers)==0:
        histo=None
    else:
        histo=[]
        idFirst=premiers[0]["ID"]
        date=premiers[0]["DateID"]
        jours=0
        for i in premiers:
            if i["ID"]!=idFirst:
                if idFirst in dictInfos:
                    if option in ("messages","voice","mots"):
                        histo.append({"ID":idFirst,"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(i["DateID"])),"Nom":dictInfos[idFirst]["Nom"],"Avatar":dictInfos[idFirst]["Avatar"],"Jours":jours})
                    else:
                        histo.append({"ID":idFirst,"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(i["DateID"])),"Nom":dictInfos[idFirst],"Jours":jours})
                else:
                    if option in ("messages","voice","mots"):
                        infos=getUserInfo(idFirst,curseurGet,guild)
                        histo.append({"ID":idFirst,"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(i["DateID"])),"Nom":infos["Nom"],"Avatar":infos["Avatar"],"Jours":jours})
                    else:
                        infos=getNom(i["ID"],option,curseurGet,False)
                        histo.append({"ID":idFirst,"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(i["DateID"])),"Nom":infos,"Jours":jours})
                idFirst=i["ID"]
                date=i["DateID"]
                jours=0
            jours+=1

        if idFirst in dictInfos:
            if option in ("messages","voice","mots"):
                histo.append({"ID":idFirst,"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"En cours","Nom":dictInfos[idFirst]["Nom"],"Avatar":dictInfos[idFirst]["Avatar"],"Jours":jours})
            else:
                histo.append({"ID":idFirst,"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"En cours","Nom":dictInfos[idFirst],"Jours":jours})
        else:
            if option in ("messages","voice","mots"):
                infos=getUserInfo(idFirst,curseurGet,guild)
                histo.append({"ID":idFirst,"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"En cours","Nom":infos["Nom"],"Avatar":infos["Avatar"],"Jours":jours})
            else:
                infos=getNom(i["ID"],option,curseurGet,False)
                histo.append({"ID":idFirst,"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"En cours","Nom":infos,"Jours":jours})

    deuxieme=curseurArc.execute("SELECT * FROM archives WHERE Type='{0}' AND Periode='Global' AND Rank=2 ORDER BY DateID ASC".format(dictOptions[option])).fetchall()
    if len(deuxieme)==0:
        histoDeux=None
    else:
        histoDeux=[]
        idDeux=deuxieme[0]["ID"]
        date=deuxieme[0]["DateID"]
        jours=0
        for i in deuxieme:
            if i["ID"]!=idDeux:
                if idDeux in dictInfos:
                    if option in ("messages","voice","mots"):
                        histoDeux.append({"ID":idDeux,"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(i["DateID"])),"Nom":dictInfos[idDeux]["Nom"],"Avatar":dictInfos[idDeux]["Avatar"],"Jours":jours})
                    else:
                        histoDeux.append({"ID":idDeux,"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(i["DateID"])),"Nom":dictInfos[idDeux],"Jours":jours})
                else:
                    if option in ("messages","voice","mots"):
                        infos=getUserInfo(idDeux,curseurGet,guild)
                        histoDeux.append({"ID":idDeux,"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(i["DateID"])),"Nom":infos["Nom"],"Avatar":infos["Avatar"],"Jours":jours})
                    else:
                        infos=getNom(idDeux,option,curseurGet,False)
                        histoDeux.append({"ID":idDeux,"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(i["DateID"])),"Nom":infos,"Jours":jours})
                idDeux=i["ID"]
                date=i["DateID"]
                jours=0
            jours+=1

        if idDeux in dictInfos:
            if option in ("messages","voice","mots"):
                histoDeux.append({"ID":idDeux,"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"En cours","Nom":dictInfos[idDeux]["Nom"],"Avatar":dictInfos[idDeux]["Avatar"],"Jours":jours})
            else:
                histoDeux.append({"ID":idDeux,"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"En cours","Nom":dictInfos[idDeux],"Jours":jours})
        else:
            if option in ("messages","voice","mots"):
                infos=getUserInfo(idDeux,curseurGet,guild)
                histoDeux.append({"ID":idDeux,"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"En cours","Nom":infos["Nom"],"Avatar":infos["Avatar"],"Jours":jours})
            else:
                infos=getNom(idDeux,option,curseurGet,False)
                histoDeux.append({"ID":idDeux,"DateDebut":"{0[4]}{0[5]}/{0[2]}{0[3]}/{0[0]}{0[1]}".format(str(date)),"DateFin":"En cours","Nom":infos,"Jours":jours})

    lastMois=curseur.execute("SELECT * FROM firstM ORDER BY DateID DESC LIMIT 10").fetchall()
    bestMois=curseur.execute("SELECT * FROM firstM ORDER BY Count DESC LIMIT 10").fetchall()
    lastAnnee=curseur.execute("SELECT * FROM firstA WHERE Annee<>'GL' ORDER BY DateID ASC").fetchall()
    addInfos(lastMois,dictInfos,option,guild,curseurGet)
    addInfos(bestMois,dictInfos,option,guild,curseurGet)
    addInfos(lastAnnee,dictInfos,option,guild,curseurGet)
    maxiLM=max(lastMois,key=lambda x:x["Count"])["Count"]
    maxiBM=max(bestMois,key=lambda x:x["Count"])["Count"]
    maxiLA=max(lastAnnee,key=lambda x:x["Count"])["Count"]

    listeMois,listeAnnee=getTimes(guild,option,"Stats")

    maxiTop15=max(top15_1,key=lambda x:x["Count"])["Count"]

    ctx={"top15_1":top15_1,"top15_2":top15_2,
        "indics":div,"histo":histo,"maxiTop15":maxiTop15,"histodeux":histoDeux,"lastmois":lastMois,"bestmois":bestMois,"lastannee":lastAnnee,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"maxiLM":maxiLM,"maxiBM":maxiBM,"maxiLA":maxiLA,
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "commands":getCommands(option),"dictCommands":dictRefCommands,"command":"rapport",
        "options":listeOptions,"dictOptions":dictRefOptions,"option":option,
        "lisPlus":[],"dictPlus":dictRefPlus,"plus":"",
        "travel":True,"selector":True,"obj":None,
        "pin":getPin(user,curseurGet,guild,option,"rapport","")}

    return ctx


def datePrec(annee):
    return str(int(annee)-1)

def dateSuiv(annee):
    return str(int(annee)+1)
