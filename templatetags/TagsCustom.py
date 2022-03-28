from django import template

register = template.Library()

def useDict(value,liste):
    return liste[value]

def tempsVoice(nb:int) -> str:
    """Permet de formater un nombre en unité de temps, pour les statistiques vocales."""
    if int(nb)<60:
        count=str(nb)+"s"
    elif int(nb)<3600:
        count=str(int(nb)//60)+"m "+str(int(nb)%60)+"s"
    elif int(nb)<86400:
        count=str(int(nb)//3600)+"h "+str(int(nb)%3600//60)+"m "+str(int(nb)%3600%60)+"s"
    else:
        count=str(int(nb)//86400)+"j "+str(int(nb)%86400//3600)+"h "+str(int(nb)%86400%3600//60)+"m "+str(int(nb)%86400%3600%60)+"s"
    return count

def formatCount(count,option) -> str:
    """Permet de décider en fonction de l'option donnée de s'il faut formater en unité de temps ou non."""
    if option in ("voice","voicechan"):
        return tempsVoice(count)
    return count

def getLen(liste):
    return len(liste)

def getRankMois(stats,option):
    return stats[option]["mois"]

def getRankAnnee(stats,option):
    return stats[option]["annee"]

def getRankGlobal(stats,option):
    return stats[option]["global"]

def getRankFirst(stats,option):
    return stats[option]["first"]

def getRankPerso(stats,option):
    return stats[option]["perso"]

def getRankBest(stats,option):
    return stats[option]["best"]

def getListBadges(badges,jeu):
    return badges[jeu]

def getUrlBadge(badge,lol):
    dictLvl={1:"https://cdn.discordapp.com/attachments/726034739550486618/956648534449483817/BronzeBase2Crop400.png",2:"https://cdn.discordapp.com/attachments/726034739550486618/956648515528982558/ArgentBase2Crop400.png",3:"https://cdn.discordapp.com/attachments/726034739550486618/956648534646607954/OrBase2Crop400.png",11:"https://cdn.discordapp.com/attachments/726034739550486618/956648533988094013/BadgeBronzeAnneeCrop400.png",12:"https://cdn.discordapp.com/attachments/726034739550486618/956648533723844678/BadgeArgentAnneeCrop400.png",13:"https://cdn.discordapp.com/attachments/726034739550486618/956648534189416529/BadgeOrAnneeCrop400.png",101:"https://cdn.discordapp.com/attachments/726034739550486618/956648513708625920/SaphirGlobalCrop400.png",102:"https://cdn.discordapp.com/attachments/726034739550486618/956648513498927184/RubisGlobalRec400.png",103:"https://cdn.discordapp.com/attachments/726034739550486618/888859878926471198/DiamantGlobalRect400.png"}
    return dictLvl[badge]



register.filter("usedict", useDict)
register.filter("tempsvoice",formatCount)
register.filter("len",getLen)
register.filter("badgeurl",getUrlBadge)

register.filter("getmois",getRankMois)
register.filter("getannee",getRankAnnee)
register.filter("getglobal",getRankGlobal)
register.filter("getfirst",getRankFirst)
register.filter("getperso",getRankPerso)
register.filter("getbest",getRankBest)

register.filter("getbadges",getListBadges)
