from companion.tools.Getteurs import formatColor, getNom, getUserInfo
from companion.tools.outils import (connectSQL, dictOptions, getMoisAnnee,
                                    getTablePerso, tableauMois)
from django.http import JsonResponse

from companion.views.Serveurs.Stats.Periods.PeriodsGraph import linePlotQuick


def getIndicsPeriods(request,guild,option):
    plus=request.GET.get("plus")
    user=request.user
    data={}

    connexionRap,curseurRap=connectSQL(guild,"Rapports","Stats","GL","")
    if plus=="serv":
        allMois=getTablePerso(guild,dictOptions[option],guild,False,"M","countDesc")
        allAnnee=getTablePerso(guild,dictOptions[option],guild,False,"A","countDesc")
        color=None
        last=curseurRap.execute("SELECT * FROM ranks WHERE Type='{0}' ORDER BY DateID DESC LIMIT 1".format(dictOptions[option])).fetchone()
    else:
        allMois=getTablePerso(guild,dictOptions[option],user.id,False,"M","countDesc")
        allAnnee=getTablePerso(guild,dictOptions[option],user.id,False,"A","countDesc")
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
        color=curseurGet.execute("SELECT * FROM users JOIN users_{0} ON users.ID = users_{0}.ID WHERE users.ID={1}".format(guild,user.id)).fetchone()["Color"]
        color=formatColor(color)
        last=curseurRap.execute("SELECT * FROM ranks WHERE Type='{0}' AND ID={1} ORDER BY DateID DESC LIMIT 1".format(dictOptions[option],user.id)).fetchone()

    bestMois=allMois[0]
    mini=allMois[-1]["Count"]
    maxi=allMois[0]["Count"]
    med=allMois[len(allMois)//2]["Count"]
    som=sum(list(map(lambda x:x["Count"],allMois)))
    ent=len(allMois)
    moy=int(som/ent)
    allMois.sort(key=lambda x:x["Annee"]+x["Mois"])
    data["mois"]={"max":maxi,"min":mini,"moy":moy,"sum":som,"entrees":ent,"med":med,"best":bestMois,"since":allMois[0]}

    
    bestAnnee=allAnnee[0]
    mini=allAnnee[-1]["Count"]
    maxi=allAnnee[0]["Count"]
    med=allAnnee[len(allAnnee)//2]["Count"]
    som=sum(list(map(lambda x:x["Count"],allMois)))
    ent=len(allAnnee)
    moy=int(som/ent)
    data["annee"]={"max":maxi,"min":mini,"moy":moy,"entrees":ent,"med":med,"best":bestAnnee}
    data["color"]=color
    data["last"]=last
    return JsonResponse(data=data,safe=False)

def getGraphPeriods(request,guild,option):
    obj = False
    plus=request.GET.get("plus")
    user=request.user

    if plus=="serv":
        color='turquoise'
        perso=False
    else:
        connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
        color=curseurGet.execute("SELECT * FROM users JOIN users_{0} ON users.ID = users_{0}.ID WHERE users.ID={1}".format(guild,user.id)).fetchone()["Color"]
        color=formatColor(color)
        perso=True
        

    graph=linePlotQuick(guild,option,user.id,obj,color,perso,"M")
    return JsonResponse(data={"graph":graph},safe=False)
