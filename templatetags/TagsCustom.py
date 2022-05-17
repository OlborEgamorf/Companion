from django import template

register = template.Library()

def useDict(value,liste):
    return liste[value]

def tempsVoice(nb:int) -> str:
    """Permet de formater un nombre en unité de temps, pour les statistiques vocales."""
    if int(nb)<0:
        nb=abs(int(nb))
        neg="- "
    else:
        neg=""
    if int(nb)<60:
        count=str(nb)+"s"
    elif int(nb)<3600:
        count=str(int(nb)//60)+"m "+str(int(nb)%60)+"s"
    elif int(nb)<86400:
        count=str(int(nb)//3600)+"h "+str(int(nb)%3600//60)+"m "+str(int(nb)%3600%60)+"s"
    else:
        count=str(int(nb)//86400)+"j "+str(int(nb)%86400//3600)+"h "+str(int(nb)%86400%3600//60)+"m "+str(int(nb)%86400%3600%60)+"s"
    return neg+count

def formatCount(count,option) -> str:
    """Permet de décider en fonction de l'option donnée de s'il faut formater en unité de temps ou non."""
    if count=="":
        return ""
    if option in ("voice","voicechan"):
        return tempsVoice(count)
    return count

def soustraction(op1,op2):
    return op1-op2

def getLen(liste):
    return len(liste)

def getRankRank(stats,option):
    return stats[option]["rank"]

def getRankFirst(stats,option):
    return stats[option]["first"]

def getRankPerso(stats,option):
    return stats[option]["perso"]

def getRankBest(stats,option):
    return stats[option]["best"]

def getListBadges(badges,jeu):
    return badges[jeu]

def getUrlBadge(badge):
    dictLvl={1:"https://cdn.discordapp.com/attachments/726034739550486618/956648534449483817/BronzeBase2Crop400.png",2:"https://cdn.discordapp.com/attachments/726034739550486618/956648515528982558/ArgentBase2Crop400.png",3:"https://cdn.discordapp.com/attachments/726034739550486618/956648534646607954/OrBase2Crop400.png",11:"https://cdn.discordapp.com/attachments/726034739550486618/956648533988094013/BadgeBronzeAnneeCrop400.png",12:"https://cdn.discordapp.com/attachments/726034739550486618/956648533723844678/BadgeArgentAnneeCrop400.png",13:"https://cdn.discordapp.com/attachments/726034739550486618/956648534189416529/BadgeOrAnneeCrop400.png",101:"https://cdn.discordapp.com/attachments/726034739550486618/956648513708625920/SaphirGlobalCrop400.png",102:"https://cdn.discordapp.com/attachments/726034739550486618/956648513498927184/RubisGlobalRec400.png",103:"https://cdn.discordapp.com/attachments/726034739550486618/888859878926471198/DiamantGlobalRect400.png"}
    return dictLvl[badge]

def getNomBadge(badge):
    dictNom={1:"3eme sur un mois",2:"2eme sur un mois",3:"1er sur un mois",11:"3eme sur une année",12:"2eme sur une année",13:"1er sur une année",101:"3eme du classement général",102:"2e du classement général",103:"Premier du classement général"}
    return dictNom[badge]



register.filter("usedict", useDict)
register.filter("tempsvoice",formatCount)
register.filter("len",getLen)
register.filter("badgeurl",getUrlBadge)
register.filter("badgename",getNomBadge)

register.filter("getrank",getRankRank)
register.filter("getfirst",getRankFirst)
register.filter("getperso",getRankPerso)
register.filter("getbest",getRankBest)

register.filter("getbadges",getListBadges)
register.filter("soustraction",soustraction)
