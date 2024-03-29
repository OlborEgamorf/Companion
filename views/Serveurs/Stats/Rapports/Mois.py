from random import shuffle

import plotly.graph_objects as go
from companion.tools.Getteurs import (addInfos, formatColor, getNom, getPin,
                                getUserInfo)
from companion.tools.outils import (connectSQL, dictOptions, getTablePerso, getTimes,
                              listeOptions, tableauMois)
from plotly.offline import plot


def rapportMois(guild,option,request,user,moisDB,anneeDB,mois,annee):
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
    guild_full=curseurGet.execute("SELECT * FROM guilds WHERE ID={0}".format(guild)).fetchone()
    
    connexion,curseur=connectSQL(guild,dictOptions[option],"Stats",tableauMois[moisDB],anneeDB)
    dictInfos={}

    top15_1=curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT 15".format(moisDB,anneeDB)).fetchall()
    idsTop15=list(map(lambda x:x["ID"],top15_1))
    if option in ("messages","voice","mots"):
        top15_2=curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT 30".format(moisDB,anneeDB)).fetchall()
        if len(top15_2)<=15:
            top15_2=None
        else:
            top15_2=top15_2[15:]
            for i in top15_2:
                infos=getUserInfo(i["ID"],curseurGet,guild)
                i["Nom"]=infos["Nom"]
                i["Avatar"]=infos["Avatar"]
                i["Color"]=infos["Color"]
                dictInfos[i["ID"]]=infos
        for i in top15_1:
            infos=getUserInfo(i["ID"],curseurGet,guild)
            i["Nom"]=infos["Nom"]
            i["Avatar"]=infos["Avatar"]
            i["Color"]=infos["Color"]
            dictInfos[i["ID"]]=infos
        
    else:
        for i in top15_1:
            i["Nom"]=getNom(i["ID"],option,curseurGet,False)
            dictInfos[i["ID"]]=i["Nom"]
        try:
            top15_2=curseur.execute("SELECT * FROM perso{0}{1}{2} ORDER BY Count DESC LIMIT 15".format(tableauMois[moisDB],anneeDB,user.id)).fetchall()
            for i in top15_2:
                i["Nom"]=getNom(i["ID"],option,curseurGet,False)
                dictInfos[i["ID"]]=i["Nom"]
        except:
            top15_2=[]
    
    avap=[]
    augm,stab,bais,nouv,reco=[],[],[],[],[]
    moisPrec,anneePrec=datePrec(tableauMois[moisDB],anneeDB)
    dateM1,dateM2=(moisPrec,anneePrec),datePrec(moisPrec,anneePrec)
    dateP1=dateSuiv(tableauMois[moisDB],anneeDB)
    dateP2=dateSuiv(dateP1[0],dateP1[1])
    for i in curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC LIMIT 100".format(moisDB,anneeDB)).fetchall():
        perso=getTablePerso(guild,dictOptions[option],i["ID"],False,"M","periodAsc")
        if i["ID"] in dictInfos:
            if option in ("messages","voice","mots"):
                i["Nom"]=dictInfos[i["ID"]]["Nom"]
                i["Avatar"]=dictInfos[i["ID"]]["Avatar"]
            else:
                i["Nom"]=dictInfos[i["ID"]]
        else:
            if option in ("messages","voice","mots"):
                infos=getUserInfo(i["ID"],curseurGet,guild)
                i["Nom"]=infos["Nom"]
                i["Avatar"]=infos["Avatar"]
            else:
                i["Nom"]=getNom(i["ID"],option,curseurGet,False)
        if len(list(filter(lambda x:x["Count"]>i["Count"],perso)))==0:
            reco.append(i)
        avant=list(filter(lambda x:x["Annee"]==anneePrec and x["Mois"]==moisPrec,perso))
        if len(avant)==0:
            nouv.append(i)
        else:
            i["Diff"]=i["Count"]-avant[0]["Count"]
            if abs(i["Diff"])<avant[0]["Count"]*0.1:
                stab.append(i)
            elif i["Diff"]>0:
                augm.append(i)
            else:
                bais.append(i)
        
        if i["ID"] in idsTop15:
            infos=dictInfos[i["ID"]]
            if option in ("messages","voice","mots"):
                dictAvAp={"ID":i["ID"],"CountNow":i["Count"],"RankNow":i["Rank"],"Nom":infos["Nom"],"Avatar":infos["Avatar"],"Color":infos["Color"]}
            else:
                dictAvAp={"ID":i["ID"],"CountNow":i["Count"],"RankNow":i["Rank"],"Nom":infos}
            avant2=list(filter(lambda x:x["Annee"]==dateM2[1] and x["Mois"]==dateM2[0],perso))
            apres1=list(filter(lambda x:x["Annee"]==dateP1[1] and x["Mois"]==dateP1[0],perso))
            apres2=list(filter(lambda x:x["Annee"]==dateP2[1] and x["Mois"]==dateP2[0],perso))
            
            if len(avant)!=0:
                dictAvAp["CountM1"]=avant[0]["Count"]
                dictAvAp["RankM1"]=avant[0]["Rank"]
            if len(avant2)!=0:
                dictAvAp["CountM2"]=avant2[0]["Count"]
                dictAvAp["RankM2"]=avant2[0]["Rank"]
            if len(apres1)!=0:
                dictAvAp["CountP1"]=apres1[0]["Count"]
                dictAvAp["RankP1"]=apres1[0]["Rank"]
            if len(apres2)!=0:
                dictAvAp["CountP2"]=apres2[0]["Count"]
                dictAvAp["RankP2"]=apres2[0]["Rank"]
            
            avap.append(dictAvAp)

    augm.sort(key=lambda x:x["Diff"],reverse=True)
    stab.sort(key=lambda x:x["Diff"],reverse=True)
    bais.sort(key=lambda x:x["Diff"])
    reco.sort(key=lambda x:x["Count"],reverse=True)

    connexionPrec,curseurPrec=connectSQL(guild,dictOptions[option],"Stats",moisPrec,anneePrec)
    try:
        idsPrec=list(map(lambda x:x["ID"],curseurPrec.execute("SELECT ID FROM {0}{1}".format(tableauMois[moisPrec],anneePrec))))
        idsNow=list(map(lambda x:x["ID"],curseur.execute("SELECT ID FROM {0}{1}".format(moisDB,anneeDB)).fetchall()))
        disp=list(filter(lambda x:x not in idsNow,idsPrec))
        dispAll=[]
        if option in ("messages","voice","mots"):
            for i in disp:
                dispAll.append(getUserInfo(i,curseurGet,guild))
        else:
            for i in disp:
                dispAll.append({"Nom":getNom(i,option,curseurGet,False)})
        shuffle(dispAll)
        miniPrec=curseurPrec.execute("SELECT MIN(Count) AS Mini FROM {0}{1}".format(tableauMois[moisPrec],anneePrec)).fetchone()["Mini"]
        maxiPrec=curseurPrec.execute("SELECT MAX(Count) AS Maxi FROM {0}{1}".format(tableauMois[moisPrec],anneePrec)).fetchone()["Maxi"]
        moyPrec=curseurPrec.execute("SELECT AVG(Count) AS Moy FROM {0}{1}".format(tableauMois[moisPrec],anneePrec)).fetchone()["Moy"]
        somPrec=curseurPrec.execute("SELECT SUM(Count) AS Somme FROM {0}{1}".format(tableauMois[moisPrec],anneePrec)).fetchone()["Somme"]
        try:
            vousPrec=curseurPrec.execute("SELECT Count FROM {0}{1} WHERE ID={2}".format(tableauMois[moisPrec],anneePrec,user.id)).fetchone()["Count"]
        except:
            vousPrec=None
    except:
        miniPrec,maxiPrec,moyPrec,vousPrec,somPrec=0,0,0,0,0
        dispAll=[]
        pass
    
    if len(augm)>7:
        augm=augm[:7]
    if len(stab)>7:
        stab=stab[:7]
    if len(bais)>7:
        bais=bais[:7]
    if len(reco)>7:
        reco=reco[:7]
    if len(dispAll)>7:
        dispAll=dispAll[:7]
    if len(nouv)>7:
        nouv=nouv[:7]

    mini=curseur.execute("SELECT MIN(Count) AS Mini FROM {0}{1}".format(moisDB,anneeDB)).fetchone()["Mini"]
    maxi=curseur.execute("SELECT MAX(Count) AS Maxi FROM {0}{1}".format(moisDB,anneeDB)).fetchone()["Maxi"]
    moy=curseur.execute("SELECT AVG(Count) AS Moy FROM {0}{1}".format(moisDB,anneeDB)).fetchone()["Moy"]
    som=curseur.execute("SELECT SUM(Count) AS Somme FROM {0}{1}".format(moisDB,anneeDB)).fetchone()["Somme"]
    try:
        vous=curseur.execute("SELECT Count FROM {0}{1} WHERE ID={2}".format(moisDB,anneeDB,user.id)).fetchone()["Count"]
    except:
        vous=None

    maxRange=maxi if maxi>maxiPrec else maxiPrec

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        value = mini,
        mode = "gauge+number+delta",
        title = {'text': "Valeur minimale"},
        delta = {'reference': miniPrec},
        gauge = {'axis': {'range': [None, maxRange*1.05]},
                'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': miniPrec}},
        domain = {'row': 0, 'column': 0}))
    
    fig.add_trace(go.Indicator(
        value = maxi,
        mode = "gauge+number+delta",
        title = {'text': "Valeur maximale"},
        delta = {'reference': maxiPrec},
        gauge = {'axis': {'range': [None, maxRange*1.05]},
                'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': maxiPrec}},
        domain = {'row': 0, 'column': 1}))
    
    fig.add_trace(go.Indicator(
        value = moy,
        mode = "gauge+number+delta",
        title = {'text': "Valeur moyenne"},
        delta = {'reference': moyPrec},
        gauge = {'axis': {'range': [None, maxRange*1.05]},
                'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': moyPrec}},
        domain = {'row': 1, 'column': 0}))
    
    maxRange=som if som>somPrec else somPrec
    fig.add_trace(go.Indicator(
        value = som,
        mode = "gauge+number+delta",
        title = {'text': "Total"},
        delta = {'reference': somPrec},
        gauge = {'axis': {'range': [None, maxRange*1.05]},
                'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': somPrec}},
        domain = {'row': 1, 'column': 1}))
    
    if option in ("messages","voice","mots"):
        fig.add_trace(go.Indicator(
            value = vous,
            mode = "gauge+number+delta",
            title = {'text': "Vous"},
            delta = {'reference': vousPrec},
            gauge = {'axis': {'range': [None, maxRange*1.05]},
                    #'steps' : [
                    #    {'range': [0, 250], 'color': "lightgray"},
                    #    {'range': [250, 400], 'color': "gray"}],
                    'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': vousPrec}
                    },
            domain = {'row': 1, 'column': 2}))

    fig.update_layout(paper_bgcolor="#111",plot_bgcolor="#333",font_family="Roboto",font_color="white",grid = {'rows': 2, 'columns': 3, 'pattern': "independent"},width=1000,height=550)
    div=plot(fig,output_type='div')

    connexionArc,curseurArc=connectSQL(guild,"Rapports","Stats","GL","")
    premiers=curseurArc.execute("SELECT * FROM archives WHERE Type='{0}' AND Periode='Mois' AND Mois='{1}' AND Annee='{2}' AND Rank=1 ORDER BY DateID ASC".format(dictOptions[option],tableauMois[moisDB],anneeDB)).fetchall()
    if len(premiers)==0:
        histo,archiveGlob,maxiGlob,archiveAnnee,maxiAnnee=None,None,None,None,None
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

        archiveGlob=curseurArc.execute("SELECT * FROM archives WHERE Type='{0}' AND Periode='Global' AND Mois='{1}' AND Annee='{2}' AND Jour='{3}' ORDER BY Rank ASC".format(dictOptions[option],tableauMois[moisDB],anneeDB,premiers[-1]["Jour"])).fetchall()
        archiveAnnee=curseurArc.execute("SELECT * FROM archives WHERE Type='{0}' AND Periode='Annee' AND Mois='{1}' AND Annee='{2}' AND Jour='{3}' ORDER BY Rank ASC".format(dictOptions[option],tableauMois[moisDB],anneeDB,premiers[-1]["Jour"])).fetchall()

        maxiGlob=max(archiveGlob,key=lambda x:x["Count"])["Count"]
        maxiAnnee=max(archiveAnnee,key=lambda x:x["Count"])["Count"]

        addInfos(archiveGlob,dictInfos,option,guild,curseurGet)
        addInfos(archiveAnnee,dictInfos,option,guild,curseurGet)

    deuxieme=curseurArc.execute("SELECT * FROM archives WHERE Type='{0}' AND Periode='Mois' AND Mois='{1}' AND Annee='{2}' AND Rank=2 ORDER BY DateID ASC".format(dictOptions[option],tableauMois[moisDB],anneeDB)).fetchall()
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

    listeMois,listeAnnee=getTimes(guild,option,"Stats")

    maxiTop15=max(top15_1,key=lambda x:x["Count"])["Count"]

    ctx={"top15_1":top15_1,"top15_2":top15_2,"augm":augm,"stab":stab,"bais":bais,"nouv":nouv,"reco":reco,"avap":avap,"disp":dispAll,
        "indics":div,"histo":histo,"archiveAnnee":archiveAnnee,"archiveGlob":archiveGlob,"histodeux":histoDeux,
        "periodM2":"{0}/{1}".format(dateM2[0],dateM2[1]),"periodM1":"{0}/{1}".format(dateM1[0],dateM1[1]),"periodP1":"{0}/{1}".format(dateP1[0],dateP1[1]),"periodP2":"{0}/{1}".format(dateP2[0],dateP2[1]),"periodNow":"{0}/{1}".format(tableauMois[moisDB],anneeDB),
        "maxiGlob":maxiGlob,"maxiAnnee":maxiAnnee,"maxiTop15":maxiTop15,
        "avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],
        "guildname":guild_full["Nom"],"guildid":guild,"guildicon":guild_full["Icon"],
        "mois":mois,"annee":annee,"listeMois":listeMois,"listeAnnee":listeAnnee,
        "command":"rapport","options":listeOptions,"option":option,"plus":"","travel":True,"selector":True,"obj":None,"pagestats":True,
        "pin":getPin(user,curseurGet,guild,option,"rapport","")}

    return ctx




def datePrec(mois,annee):
    if mois=="01":
        annee=str(int(annee)-1)
        mois="12"
    else:
        mois=int(mois)-1
        if mois<10:
            mois="0"+str(mois)
        else:
            mois=str(mois)
    return mois,annee

def dateSuiv(mois,annee):
    if mois=="12":
        annee=str(int(annee)+1)
        mois="01"
    else:
        mois=int(mois)+1
        if mois<10:
            mois="0"+str(mois)
        else:
            mois=str(mois)
    return mois,annee
