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


register.filter("usedict", useDict)
register.filter("tempsvoice",formatCount)
register.filter("len",getLen)

register.filter("getmois",getRankMois)
register.filter("getannee",getRankAnnee)
register.filter("getglobal",getRankGlobal)
register.filter("getfirst",getRankFirst)
register.filter("getperso",getRankPerso)
register.filter("getbest",getRankBest)
