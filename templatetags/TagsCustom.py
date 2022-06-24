import datetime
from django import template
from companion.tools.outils import dictRefCommands, dictRefOptions, dictRefPlus,dictOptions,tableauMois

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

def getRankDeux(stats):
    return [stats["deux"]]

def getRankFirst(stats):
    return [stats["first"]]

def getRankBest(stats):
    return [stats["bestperiod"]]

def getListBadges(badges,jeu):
    return badges[jeu]

def getUrlBadge(badge):
    dictLvl={1:"https://cdn.discordapp.com/attachments/726034739550486618/956648534449483817/BronzeBase2Crop400.png",2:"https://cdn.discordapp.com/attachments/726034739550486618/956648515528982558/ArgentBase2Crop400.png",3:"https://cdn.discordapp.com/attachments/726034739550486618/956648534646607954/OrBase2Crop400.png",11:"https://cdn.discordapp.com/attachments/726034739550486618/956648533988094013/BadgeBronzeAnneeCrop400.png",12:"https://cdn.discordapp.com/attachments/726034739550486618/956648533723844678/BadgeArgentAnneeCrop400.png",13:"https://cdn.discordapp.com/attachments/726034739550486618/956648534189416529/BadgeOrAnneeCrop400.png",101:"https://cdn.discordapp.com/attachments/726034739550486618/956648513708625920/SaphirGlobalCrop400.png",102:"https://cdn.discordapp.com/attachments/726034739550486618/956648513498927184/RubisGlobalRec400.png",103:"https://cdn.discordapp.com/attachments/726034739550486618/888859878926471198/DiamantGlobalRect400.png"}
    return dictLvl[badge]

def getNomBadge(badge):
    dictNom={1:"3eme sur un mois",2:"2eme sur un mois",3:"1er sur un mois",11:"3eme sur une année",12:"2eme sur une année",13:"1er sur une année",101:"3eme du classement général",102:"2e du classement général",103:"Premier du classement général"}
    return dictNom[badge]

def lexiqueOption(option):
    if option=="messages":
        return "Messages : correspond aux statistiques de messages envoyés sur votre serveur, par chaque membre, et sur différentes périodes."
    if option=="voice":
        return "Vocal : correspond aux statistiques du temps passé dans n'importe quel salon vocal, par chaque membre, et sur différentes périodes."
    if option=="emotes":
        return "Emotes : correspond aux statistiques des emotes et emojis envoyés dans les messages sur le serveur."
    if option=="freq":
        return "Fréquences : correspond aux heures où les messages ont été envoyés sur le serveur."
    if option=="salons":
        return "Salons : correspond aux statistiques de messages envoyés par les membres dans chaque salon textuel."
    if option=="voicechan":
        return "Salons vocaux : correspond aux statistiques du temps passé en vocal par les membres dans chaque salon vocal."
    if option=="reactions":
        return "Réactions : correspond aux statistiques des réactions laissées sur les messages par les membres du serveur."
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        return "Jeux : correspond aux classements des différents jeux proposé sur Olbor Track."

def lexiqueCommande(command):
    if command=="ranks":
        return "Classements : Affiche les statistiques sous forme de classements. Les classements sont disponibles sur plusieurs types de périodes : mois, année ou global." 
    if command=="periods":
        return "Périodes : Affiche les statistiques sous forme d'un résumé période par période." 
    if command=="evol":
        return "Évolution : Affiche votre évolution ou celle d'un objet (salon, emote, ...) pour le classement d'une période donnée." 
    if command=="first":
        return "Premiers : Affiche le premier du classement de chaque période." 
    if command=="jours":
        return "Premiers : Affiche les messages envoyés ou le temps passé en vocal pour chaque jour où il y a eu de l'activité sur le serveur." 

def lexiquePlus(plus):
    if plus=="":
        return "Tableaux : Affiche les statistiques dans un tableau simple. Vous pouvez trier le tableau en cliquant sur les en-têtes de colonnes, et chercher des éléments à l'intérieur. Cliquer sur une ligne affiche un tableau complémentaire sous ce lexique." 
    if plus=="serv":
        return "Tableaux pour le serveur : Affiche les statistiques dans un tableau simple. Ce tableau correspond aux statistiques du serveur dans son ensemble. Vous pouvez trier le tableau en cliquant sur les en-têtes de colonnes, et chercher des éléments à l'intérieur. Cliquer sur une ligne affiche un tableau complémentaire sous ce lexique." 
    if plus=="perso":
        return "Tableaux pour vous : Affiche les statistiques dans un tableau simple. Ce tableau correspond aux statistiques de vous seulement. Vous pouvez trier le tableau en cliquant sur les en-têtes de colonnes, et chercher des éléments à l'intérieur. Cliquer sur une ligne affiche un tableau complémentaire sous ce lexique."
    if plus=="obj":
        return "Tableaux pour un objet : Affiche les statistiques dans un tableau simple. Ce tableau correspond aux statistiques d'un objet : salon, emote, ou autre que vous choisissez. Vous pouvez trier le tableau en cliquant sur les en-têtes de colonnes, et chercher des éléments à l'intérieur. Cliquer sur une ligne affiche un tableau complémentaire sous ce lexique."  
    if plus=="pantheon":
        return "Pantheon : Affiche le classement des classements : tous les classements de toutes les périodes fusionnés, pour donner un super classement." 
    if plus=="graph":
        return "Graphiques : Affiche les statistiques dans différents graphiques, pour mieux visualiser."   

def statshome(option,perso):
    if option=="messages":
        if perso:
            return "Messages envoyés"
        return "Membre le plus actif en messages"
    if option=="voice":
        if perso:
            return "Temps passé en vocal"
        return "Membre le plus actif en vocal"
    if option=="emotes":
        return "Emote la plus utilisée"
    if option=="freq":
        return "Meilleure heure d'activité"
    if option=="salons":
        return "Salon textuel le plus actif"
    if option=="voicechan":
        return "Salon vocal le plus actif"
    if option=="reactions":
        return "Réaction la plus utilisée"
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        if perso:
            return dictOptions[option]
        return "Meilleur joueur de {0}".format(dictOptions[option])

def enteteNom(option):
    if option in ("messages","voice"):
        return "Membre"
    if option in ("emotes","reactions"):
        return "Emote"
    if option=="freq":
        return "Heure"
    if option in ("salons","voicechan"):
        return "Salon"
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        return "Joueur"

def enteteCount(option):
    if option in ("messages","salons","freq"):
        return "Messages envoyés"
    if option in ("voice","voicechan"):
        return "Temps en vocal"
    if option in ("emotes","reactions"):
        return "Utilisations"
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        return "Points"

def nomsearch(option):
    if option in ("messages","voice"):
        return "un membre"
    if option in ("tortues","tortuesduo","p4","matrice","morpion","trivialversus","trivialbr","trivialparty"):
        return "un joueur"
    if option in ("emotes","reactions"):
        return "une emote"
    if option=="freq":
        return "une heure"
    if option in ("salons","voicechan"):
        return "un salon"

def getI(liste,i):
    return liste[i]

def getTable(ranks,option):
    return ranks[option][0]
def getMax(ranks,option):
    return ranks[option][1]
def getEnd(ranks,option):
    return ranks[option][2]

def getCommand(command):
    return dictRefCommands[command]
def getOption(option):
    return dictRefOptions[option]
def getPlus(plus):
    return dictRefPlus[plus]

def firstGlobal(periode):
    if periode[2:]=="GL":
        return "Global"
    if periode[:2]=="TO":
        return "Total 20{0}".format(periode[2:])
    return "{0} 20{1}".format(tableauMois[periode[2:]],periode[:2])

def getPropsPolls(props,counts):
    props=props.split(";")
    if counts=="0":
        counts=props.copy()
    else:
        counts=counts.split(";")
    dictFull=[]
    for i,el in enumerate(props):
        dictFull.append({"Count":counts[i],"Prop":el,"Nb":i+1})
    return dictFull

def epochtodate(epoch):
    return datetime.datetime.fromtimestamp(epoch).strftime('%d/%m/%Y - %H:%M:%S')

def calcpercent(count,total):
    return round(100*int(count)/total,2)


register.filter("usedict", useDict)
register.filter("tempsvoice",formatCount)
register.filter("len",getLen)
register.filter("badgeurl",getUrlBadge)
register.filter("badgename",getNomBadge)

register.filter("getdeux",getRankDeux)
register.filter("getfirst",getRankFirst)
register.filter("getbest",getRankBest)

register.filter("getbadges",getListBadges)
register.filter("soustraction",soustraction)

register.filter("lexiqueOption",lexiqueOption)
register.filter("lexiqueCommande",lexiqueCommande)
register.filter("lexiquePlus",lexiquePlus)
register.filter("statshome",statshome)

register.filter("headnom",enteteNom)
register.filter("headcount",enteteCount)
register.filter("nomsearch",nomsearch)

register.filter("getI",getI)
register.filter("getCommand",getCommand)
register.filter("getOption",getOption)
register.filter("getPlus",getPlus)

register.filter("periodfirst",firstGlobal)

register.filter("globtable",getTable)
register.filter("globmax",getMax)
register.filter("globend",getEnd)

register.filter("propspolls",getPropsPolls)
register.filter("epochtodate",epochtodate)
register.filter("calcpercent",calcpercent)