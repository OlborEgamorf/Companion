from companion.Getteurs import getChannels, getEmoteTable, getFreq, getNom, getUserTable
from companion.templatetags.TagsCustom import formatCount, tempsVoice
from companion.outils import connectSQL, getTablePerso
from random import choice

tableauMois={"01":"janvier","02":"février","03":"mars","04":"avril","05":"mai","06":"juin","07":"juillet","08":"aout","09":"septembre","10":"octobre","11":"novembre","12":"décembre","TO":"TOTAL","1":"janvier","2":"février","3":"mars","4":"avril","5":"mai","6":"juin","7":"juillet","8":"aout","9":"septembre","janvier":"01","février":"02","mars":"03","avril":"04","mai":"05","juin":"06","juillet":"07","aout":"08","septembre":"09","octobre":"10","novembre":"11","décembre":"12"}

def hierMAG(date,period,guild,option):
    if period=="mois":
        hier=getOlderMois(tableauMois[date[0]],date[1],guild,option)
    elif period=="annee":
        hier=getOlderAnnee(date[1],guild,option)
    elif period=="global":
        hier=None
    return hier

def getOlderJour(jour,mois,annee,curseur,table,option):
    etat=curseur.execute("SELECT Jour,Mois,Annee FROM {0} WHERE DateID < {1}{2}{3} AND Type='{4}' ORDER BY DateID DESC".format(table,annee,mois,jour,option)).fetchone()
    if etat==None:
        return None
    return etat["Jour"],etat["Mois"],etat["Annee"]

def getEarlierJour(jour,mois,annee,curseur,table,option):
    etat=curseur.execute("SELECT Jour,Mois,Annee FROM {0} WHERE DateID > {1}{2}{3} AND Type='{4}' ORDER BY DateID ASC".format(table,annee,mois,jour,option)).fetchone()
    if etat==None:
        return None
    return etat["Jour"],etat["Mois"],etat["Annee"]

def getOlderMois(mois,annee,guild,option):
    curseur=connectSQL(guild,option,"Stats","GL",None)[1]
    etat=curseur.execute("SELECT Mois,Annee FROM firstM WHERE DateID < {0}{1} ORDER BY DateID DESC".format(annee,mois)).fetchone()
    if etat==None:
        return None
    return tableauMois[etat["Mois"]],etat["Annee"]

def getEarlierMois(mois,annee,guild,option):
    curseur=connectSQL(guild,option,"Stats","GL",None)[1]
    etat=curseur.execute("SELECT Mois,Annee FROM firstM WHERE DateID > {0}{1} ORDER BY DateID ASC".format(annee,mois)).fetchone()
    if etat==None:
        return None
    return tableauMois[etat["Mois"]],etat["Annee"]

def getOlderAnnee(annee,guild,option):
    curseur=connectSQL(guild,option,"Stats","GL",None)[1]
    etat=curseur.execute("SELECT Mois,Annee FROM firstA WHERE DateID < {0} ORDER BY DateID DESC".format(annee)).fetchone()
    if etat==None:
        return None
    return "to",etat["Annee"]

def getEarlierAnnee(annee,guild,option):
    curseur=connectSQL(guild,option,"Stats","GL",None)[1]
    etat=curseur.execute("SELECT Mois,Annee FROM firstA WHERE DateID > {0} ORDER BY DateID ASC".format(annee)).fetchone()
    if etat==None:
        return None
    return "to",etat["Annee"]

def descipGlobal(option,result,start,stop,hier,guild,curseurGet,obj):
    stats=[]
    if hier!=None:
        curseur=connectSQL(guild,option,"Stats",tableauMois[hier[0]],hier[1])[1]
    for i in range(start,stop):
        try:
            oldRank=0
            assert hier!=None
            resultHier=curseur.execute("SELECT * FROM {0}{1} WHERE ID={2} ORDER BY Rank ASC".format(hier[0],hier[1],result[i]["ID"])).fetchone()
            if resultHier==None:
                assert len(result)-result[i]["Rank"]!=0
                oldRank=len(result)-result[i]["Rank"]
            else:
                assert resultHier["Rank"]-result[i]["Rank"]!=0
                oldRank=resultHier["Rank"]-result[i]["Rank"]
        except AssertionError:
            pass

        if option in ("messages","voice","mots") or obj:
            ligne=getUserTable(result[i],curseurGet,guild)

        elif option in ("emotes","reactions"):
            ligne=getEmoteTable(result[i],curseurGet)

        elif option in ("salons","voicechan"):
            ligne=getChannels(result[i],curseurGet)

        elif option=="freq":
            ligne=getFreq(result[i])

        ligne["Old"]=oldRank
        stats.append(ligne)
    return stats


def paliers(curseur,period,date,option):
    liste=[]
    if option in ("voice","voicechan"):
        allMile={"jour":{1800:0,3600:0,14400:0,36000:0},"mois":{7200:0,18000:0,86400:0,432000:0},"annee":{86400:0,432000:0,864000:0,2678400:0},"global":{432000:0,864000:0,2678400:0,5356800:0}}
    else:
        allMile={"jour":{50:0,250:0,500:0,1000:0},"mois":{250:0,1000:0,2500:0,5000:0},"annee":{1000:0,2500:0,5000:0,10000:0},"global":{5000:0,10000:0,25000:0,50000:0}}
    dictMile=allMile[period]
    for i in dictMile:
        if period=="jour":
            dictMile[i]=curseur.execute("SELECT COUNT() AS Total FROM ranks WHERE Jour='{0}' AND Mois='{1}' AND Annee='{2}' AND Type='{3}' AND Count>{4}".format(date[0],date[1],date[2],option,i)).fetchone()["Total"]
        else:
            dictMile[i]=curseur.execute("SELECT COUNT() AS Total FROM {0}{1} WHERE Count>{2}".format(date[0],date[1],i)).fetchone()["Total"]

    for i in dictMile:
        if dictMile[i]!=0:
            if dictMile[i]>1:
                dictPhrase={"salons":"{0} salons ont vu plus de {1} messages envoyés".format(dictMile[i],i),"freq":"{0} heures ont vu plus de {1} messages envoyés".format(dictMile[i],i),"emotes":"{0} emotes ont été utilisées plus de {1} fois".format(dictMile[i],i),"reactions":"{0} réactions ont été utilisées plus de {1} fois".format(dictMile[i],i),"voicechan":"{0} salons ont été utilisés pendant plus de {1} en vocal en cumulé.".format(dictMile[i],tempsVoice(i)),"messages":"{0} membres ont envoyé plus de {1} messages".format(dictMile[i],i),"vocal":"{0} membres ont passé plus de {1} en vocal".format(dictMile[i],i),"mots":"{0} membres ont envoyé plus de {1} mots".format(dictMile[i],i)}
            else:
                dictPhrase={"salons":"1 salon a vu plus de {0} messages envoyés".format(i),"freq":"1 heure a vu plus de {0} messages envoyés".format(i),"emotes":"1 emote a été utilisée plus de {0} fois".format(i),"reactions":"1 réaction a été utilisée plus de {0} fois".format(i),"voicechan":"1 salon a été utilisé pendant plus de {0} en vocal en cumulé.".format(tempsVoice(i)),"messages":"1 membre a envoyé plus de {0} messages".format(i),"vocal":"1 membre a passé plus de {0} en vocal".format(i),"mots":"1 membre ont envoyé plus de {0} mots".format(i)}
            liste.append(dictPhrase[option])
    return liste


def descipMoyennes(option,result):
    numb=len(result)
    count=0
    for i in result:
        count+=i["Count"]

    dictBloc={
        "messages":[{"Nom":"Total messages","Count":count},{"Nom":"Membres","Count":numb},{"Nom":"Moyenne par membre","Count":round(count/numb,3)},{"Nom":"Meilleur membre","Count":result[0]["Count"]},{"Nom":"Médiane","Count":result[len(result)//2]["Count"]},{"Nom":"Pire membre","Count":result[len(result)-1]["Count"]}],

        "voice":[{"Nom":"Total temps en vocal","Count":tempsVoice(count)},{"Nom":"Membres","Count":numb},{"Nom":"Moyenne par membre","Count":tempsVoice(int(count/numb))},{"Nom":"Meilleur membre","Count":tempsVoice(result[0]["Count"])},{"Nom":"Médiane","Count":tempsVoice(result[len(result)//2]["Count"])},{"Nom":"Pire membre","Count":tempsVoice(result[len(result)-1]["Count"])}],

        "emotes":[{"Nom":"Total emotes utilisées","Count":count},{"Nom":"Emotes différentes","Count":numb},{"Nom":"Moyenne par emote","Count":round(count/numb,3)},{"Nom":"Meilleur emote","Count":result[0]["Count"]},{"Nom":"Médiane","Count":result[len(result)//2]["Count"]},{"Nom":"Pire emote","Count":result[len(result)-1]["Count"]}],

        "reactions":[{"Nom":"Total réactions utilisées","Count":count},{"Nom":"Réactions différentes","Count":numb},{"Nom":"Moyenne par réaction","Count":round(count/numb,3)},{"Nom":"Meilleure réaction","Count":result[0]["Count"]},{"Nom":"Médiane","Count":result[len(result)//2]["Count"]},{"Nom":"Pire réaction","Count":result[len(result)-1]["Count"]}],

        "salons":[{"Nom":"Salons utilisés","Count":numb},{"Nom":"Moyenne messages par salon","Count":round(count/numb,3)},{"Nom":"Meilleur salon","Count":result[0]["Count"]},{"Nom":"Médiane","Count":result[len(result)//2]["Count"]},{"Nom":"Pire salon","Count":result[len(result)-1]["Count"]}],

        "freq":[{"Nom":"Heures actives","Count":numb},{"Nom":"Moyenne messages par heure","Count":round(count/numb,3)},{"Nom":"Meilleur heure","Count":result[0]["Count"]},{"Nom":"Médiane","Count":result[len(result)//2]["Count"]},{"Nom":"Pire heure","Count":result[len(result)-1]["Count"]}],

        "voicechan":[{"Nom":"Salons utilisés","Count":numb},{"Nom":"Moyenne temps en vocal par salon","Count":tempsVoice(round(count/numb,3))},{"Nom":"Meilleur salon","Count":tempsVoice(result[0]["Count"])},{"Nom":"Médiane","Count":tempsVoice(result[len(result)//2]["Count"])},{"Nom":"Pire salon","Count":tempsVoice(result[len(result)-1]["Count"])}],
    }
    return dictBloc[option]


def anecdotesSpe(date,guild,option,period,curseur,curseurGet,curseurHier):
    conGL,curGL=connectSQL(guild,option,"Stats","GL","")
    anecs=[]

    if period in ("mois","annee"):
        result=curseur.execute("SELECT * FROM {0}{1} ORDER BY Rank ASC".format(date[0],date[1])).fetchall()
        premiers=curseur.execute("SELECT * FROM {0}{1} WHERE Rank=1 ORDER BY Rank ASC".format(date[0],date[1])).fetchall()
        alea=choice(premiers)
        if period=="mois":
            first=curGL.execute("SELECT COUNT() AS Premier FROM firstM WHERE DateID<{0} AND ID={1}".format(date[1]+tableauMois[date[0]],alea["ID"])).fetchone()
        else:
            first=curGL.execute("SELECT COUNT() AS Premier FROM firstA WHERE DateID<{0} AND ID={1}".format(date[1],alea["ID"])).fetchone()
    elif period=="global":
        result=curseur.execute("SELECT * FROM glob ORDER BY Rank ASC").fetchall()
        premiers=curseur.execute("SELECT * FROM glob WHERE Rank=1 ORDER BY Rank ASC".format()).fetchall()
        alea=choice(premiers)

    nom=getNom(alea["ID"],option,curseurGet,False)
    if period=="global":
        count=""
    elif first["Premier"]==0:
        count=", c'est la **première** fois !"
    else:
        count=" pour la **{0}e** fois.".format(first["Premier"]+1)
    if len(premiers)==1:
        ex=""
    else:
        ex="\nIl est accompagné par {0} autre(s)".format(len(premiers)-1)
    dictPremier={"salons":"Le salon le plus actif est {0}{1}{2}","freq":"L'heure la plus active est {0}{1}{2}","emotes":"L'emote la plus utilisée est {0}{1}{2}","reactions":"La réaction la plus utilisée est {0}{1}{2}","messages":"Le membre le plus actif est {0}{1}{2}","voice":"Le membre le plus actif est {0}{1}{2}","voicechan":"Le salon le plus actif est {0}{1}{2}"}
    anecs.append({"Nom":"Premiers","Values":dictPremier[option].format(nom,count,ex)})

    hier=hierMAG(date,period,guild,option)
    if period!="global":
        if hier!=None:
            if period=="mois":
                premierH=curGL.execute("SELECT ID FROM firstM WHERE Mois='{0}' AND Annee='{1}'".format(tableauMois[hier[0]],hier[1])).fetchone()["ID"]
                if premierH!=alea["ID"]:
                    consec=curGL.execute("SELECT ID FROM firstM WHERE DateID<={0} ORDER BY DateID DESC".format(hier[1]+tableauMois[hier[0]])).fetchall()
                    try:
                        i=0
                        while consec[i]["ID"]==premierH:
                            i+=1
                    except:
                        i=len(consec)
                    anecs.append({"Nom":"Série première place","Value":"Il arrête la série de {0}, premier **{1} fois** d'affilée jusque là".format(getNom(premierH,option,curseurGet,False),i)})
                else:
                    consec=curGL.execute("SELECT ID FROM firstM WHERE DateID<={0} ORDER BY DateID DESC".format(hier[1]+tableauMois[hier[0]])).fetchall()
                    try:
                        i=1
                        while consec[i]["ID"]==alea["ID"]:
                            i+=1
                        anecs.append({"Nom":"Série première place","Value":"Il est sur une série de **{0}** premières places d'affilée.".format(i)})
                    except:
                        anecs.append({"Nom":"Série première place","Value":"Il n'a **jamais arrêté** d'être premier."})

            elif period=="annee":
                premierH=curGL.execute("SELECT ID FROM firstA WHERE Annee='{0}'".format(hier[1])).fetchone()["ID"]
                if premierH!=alea["ID"]:
                    consec=curGL.execute("SELECT ID FROM firstA WHERE DateID<={0} ORDER BY DateID DESC".format(hier[1])).fetchall()
                    try:
                        i=0
                        while consec[i]["ID"]==premierH:
                            i+=1
                    except:
                        i=len(consec)
                    anecs.append({"Nom":"Série première place","Value":"Il arrête la série de {0}, premier **{1} fois** d'affilée jusque là".format(getNom(premierH,option,curseurGet,False),i)})
                else:
                    consec=curGL.execute("SELECT ID FROM firstA WHERE DateID<={0} ORDER BY DateID DESC".format(hier[1])).fetchall()
                    try:
                        i=1
                        while consec[i]["ID"]==alea["ID"]:
                            i+=1
                        anecs.append({"Nom":"Série première place","Value":"Il est sur une série de **{0}** premières places d'affilée.".format(i)})
                    except:
                        anecs.append({"Nom":"Série première place","Value":"Il n'a **jamais arrêté** d'être premier."})
                
    if period!="global":
        records=[]
        if period=="mois":
            for i in result:
                try:
                    tablePerso=getTablePerso(guild,option,i["ID"],False,"M","countDesc")
                    tablePerso=list(filter(lambda x:x["Annee"]+x["Mois"]<=date[1]+tableauMois[date[0]]))
                    tablePerso.sort(key=lambda x:x["Count"], reverse=True)
                    tablePerso=curGL.execute("SELECT Mois, Annee, Annee || '' || Mois AS DateID, Count FROM persoM{0} WHERE DateID<='{1}{2}' ORDER BY Count DESC".format(i["ID"],date[1],tableauMois[date[0]])).fetchone()
                    if tablePerso[0]["Mois"]==tableauMois[date[0]] and tablePerso[0]["Annee"]==date[1]:
                        records.append({"ID":i["ID"],"Count":formatCount(option,tablePerso["Count"])})
                except:
                    continue
        elif period=="annee":
            for i in result:
                try:
                    tablePerso=getTablePerso(guild,option,i["ID"],False,"A","countDesc")
                    tablePerso=list(filter(lambda x:x["Annee"]<=date[1] and x["Annee"]!="GL"))
                    tablePerso.sort(key=lambda x:x["Count"], reverse=True)
                    if tablePerso[0]["Annee"]==date[1]:
                        records.append({"ID":i["ID"],"Count":formatCount(option,tablePerso["Count"])})
                except:
                    continue
        if records==[]:
            anecs.append({"Nom":"Records","Value":"Rien ou personne n'a battu son record d'activité à cette date."})
        else:
            descip=""
            stop=7 if len(records)>7 else len(records)
            for i in range(stop):
                choix=choice(records)
                descip+=", {0} ({1})".format(getNom(choix["ID"],option,curseurGet,False),choix["Count"])
                records.remove(choix)
            descip=descip[1:len(descip)]
            if len(records)==0:
                reste=""
            else:
                reste=", ainsi que {0} autre(s)".format(len(records))
            dictPremier={"Salons":"Des salons ont vu leur plus grande activité à cette date : {0}{1}","Freq":"Certaines heures ont vu leur pic d'activité à cette date : {0}{1}","Emotes":"Certaines emotes n'ont jamais été autant utilisées à cette date : {0}{1}","Reactions":"Certaines réactions n'ont jamais été autant utilisées à cette date : {0}{1}","Messages":"Certaines personnes n'ont jamais été autant actifs à cette date : {0}{1}","Voicechan":"Des salons ont vu leur plus grande activité à cette date : {0}{1}","Voice":"Certaines personnes n'ont jamais été autant actifs à cette date : {0}{1}"}
            anecs.append({"Nom":"Records","Value":dictPremier[option].format(descip,reste)})
    
    if hier!=None and period!="global":
        plus,moins,new=0,0,0
        if period in ("mois","annee"):
            if period=="mois":
                title="Par rapport au {0}/{1}".format(tableauMois[hier[0]],hier[1])
            else:
                title="Par rapport au 20{0}".format(hier[1])
        else:
            title="Par rapport au {0}/{1}/{2}".format(hier[0],hier[1],hier[2])
        for i in result:
            count=curseurHier.execute("SELECT Count FROM {0}{1} WHERE ID={2}".format(hier[0],hier[1],i["ID"])).fetchone()
            if count==None:
                new+=1
            elif count["Count"]>i["Count"]:
                moins+=1
            elif count["Count"]<i["Count"]:
                plus+=1
        dictPlusMoins={"messages":"Parmi les membres actifs à cette date, **{0}** l'ont été **moins** que la période précédente, **{1} plus** et **{2} ne l'avaient pas été**.","salons":"Parmi les salons actifs à cette date, **{0}** l'ont été **moins** que la période précédente, **{1} plus** et **{2} ne l'avaient pas été**.","freq":"Parmi les heures actives à cette date, **{0}** l'ont été **moins** que la période précédente, **{1} plus** et **{2} ne l'avaient pas été**.","emotes":"Parmi les emotes utilisées à cette date, **{0}** l'ont été **moins** que la période précédente, **{1} plus** et **{2} ne l'avaient pas été**.","reactions":"Parmi les réactions utilisées à cette date, **{0}** l'ont été **moins** que la période précédente, **{1} plus** et **{2} ne l'avaient pas été**.","voice":"Parmi les membres actifs à cette date, **{0}** l'ont été **moins** que la période précédente, **{1} plus** et **{2} ne l'avaient pas été**.","voicechan":"Parmi les salons actifs à cette date, **{0}** l'ont été **moins** que la période précédente, **{1} plus** et **{2} ne l'avaient pas été**."}
        anecs.append({"Nom":title,"Value":dictPlusMoins[option].format(moins,plus,new)})

    return anecs
