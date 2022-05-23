from django.urls import path
from companion.Pin import ajoutPin, delPin

from companion.views.Autre.Blank import iFrameBlank
from companion.views.Autre.GuildHome import viewGuildHome
from companion.views.Autre.HallOfBadges import viewBadges
from companion.views.Autre.home import home
from companion.views.Autre.StatsHome import statsHomeJeux, viewStatsHome
from companion.views.Evol.Evol import evolJeux, iFrameEvol, viewEvol
from companion.views.Evol.EvolCompare import viewEvolCompare
from companion.views.Evol.EvolGraph import graphEvol, iFrameGraphEvol
from companion.views.First.First import (firstJeux, iFrameFirst,
                                         iFrameFirstJeux, viewFirst)
from companion.views.First.FirstCompare import viewFirstCompare
from companion.views.First.FirstGraph import graphFirst, iFrameGraphFirst
from companion.views.Jours.Jours import iFrameJour, viewJours
from companion.views.Jours.JoursGraph import graphJours, iFrameGraphJours
from companion.views.Mixes.DelMix import delMix
from companion.views.Mixes.MixPeriods import iFrameMixPeriods, mixPeriods
from companion.views.Mixes.MixPerso import iFrameMixPerso, mixPerso
from companion.views.Mixes.MixRanks import iFrameMixRank, mixRank
from companion.views.Mixes.MixServ import iFrameMixServ, mixServ
from companion.views.Mondial.emotesmondial import emotesMondial, iframeEmotes
from companion.views.Mondial.EmotesWW import emotesMondialGuild
from companion.views.OT.OTTitres import viewOTStats, viewOTTitres
from companion.views.Periods.Periods import (iFramePeriods, iFramePeriodsJeux,
                                             periodsJeux, viewPeriods)
from companion.views.Periods.PeriodsCompare import viewPeriodsCompare
from companion.views.Periods.PeriodsGraph import (graphPeriods,
                                                  iFrameGraphPeriods)
from companion.views.Periods.Serv import iFrameServ, viewServ
from companion.views.Periods.ServCompare import viewServCompare
from companion.views.Profil.ProfilCustom import viewProfilPerso
from companion.views.Profil.ProfilHome import viewProfilHome
from companion.views.Profil.ProfilTitres import viewProfilTitres
from companion.views.Ranks.Pantheon import viewPantheon
from companion.views.Ranks.Perso import iFramePerso, viewPerso
from companion.views.Ranks.PersoCompare import viewPersoCompare
from companion.views.Ranks.Rank import (iFrameRank, iFrameRankJeux, rankJeux,
                                        viewRank, viewRankObj)
from companion.views.Ranks.RanksCompare import viewRankCompare
from companion.views.Ranks.RanksGraph import graphRanks, iFrameGraphRanks
from companion.views.Rapports.NewRapports import viewRapports
from companion.views.Roles.Roles import iFrameRoles

urlpatterns = [
    path('', home, name="companion-home"),
    path("<int:guild>",viewGuildHome,name="guild-home"),

    path("<int:guild>/home",viewStatsHome,name="stats-home"),
    path("<int:guild>/<str:option>/ranks/",viewRank,name="stats-ranks"),
    path("<int:guild>/<str:option>/periods/",viewServ,name="stats-periods"),
    path("<int:guild>/<str:option>/evol/",viewEvol,name="stats-evol"),
    path("<int:guild>/<str:option>/jours/",viewJours,name="stats-jours"),
    path("<int:guild>/<str:option>/first/",viewFirst,name="stats-first"),
    path("<int:guild>/<str:option>/rapport/",viewRapports,name="stats-rapport"),
    #path("<int:guild>/<str:option>/roles",viewRoles,name="stats-roles"),
    path("<int:guild>/emotes/mondial/",emotesMondialGuild,name="guild-emotes-mondial"),

    path("<int:guild>/<str:option>/periods/perso",viewPeriods,name="stats-serv"),
    path("<int:guild>/<str:option>/ranks/perso",viewPerso,name="stats-perso"),
    path("<int:guild>/<str:option>/ranks/obj",viewRankObj,name="compare-perso"),

    path("<int:guild>/<str:option>/iframeranks",iFrameRank,name="iframe-ranks"),
    path("<int:guild>/<str:option>/iframeperiods",iFramePeriods,name="iframe-periods"),
    path("<int:guild>/<str:option>/iframeevol",iFrameEvol,name="iframe-evol"),
    path("<int:guild>/<str:option>/iframejours",iFrameJour,name="iframe-jours"),
    path("<int:guild>/<str:option>/iframeroles",iFrameRoles,name="iframe-roles"),
    path("<int:guild>/<str:option>/iframeserv",iFrameServ,name="iframe-serv"),
    path("<int:guild>/<str:option>/iframeperso",iFramePerso,name="iframe-perso"),
    path("<int:guild>/<str:option>/iframefirst",iFrameFirst,name="iframe-first"),

    path("iframeblank",iFrameBlank,name="iframe-blank"),

    path("mondial/emotes",emotesMondial,name="emotes-mondial"),
    path("<int:emote>/iframeemotesww",iframeEmotes,name="iframe-emotesww"),

    path("<int:guild>/<str:option>/ranks/graphs",graphRanks,name="graphs-ranks"),
    path("<int:guild>/<str:option>/periods/graphs",graphPeriods,name="graphs-periods"),
    path("<int:guild>/<str:option>/evol/graphs",graphEvol,name="graphs-periods"),
    path("<int:guild>/<str:option>/first/graphs",graphFirst,name="graphs-periods"),
    path("<int:guild>/<str:option>/jours/graphs",graphJours,name="graphs-periods"),
    path("<int:guild>/<str:option>/iframeranks/graphs",iFrameGraphRanks,name="iframe-graphs-ranks"),
    path("<int:guild>/<str:option>/iframeperiods/graphs",iFrameGraphPeriods,name="iframe-graphs-ranks"),
    path("<int:guild>/<str:option>/iframeevol/graphs",iFrameGraphEvol,name="iframe-graphs-ranks"),
    path("<int:guild>/<str:option>/iframefirst/graphs",iFrameGraphFirst,name="iframe-graphs-ranks"),
    path("<int:guild>/<str:option>/iframejours/graphs",iFrameGraphJours,name="iframe-graphs-ranks"),

    path("<int:guild>/<str:option>/ranks/compare",viewRankCompare,name="compare-ranks"),
    path("<int:guild>/<str:option>/ranks/compareperso",viewPersoCompare,name="compare-perso"),
    path("<int:guild>/<str:option>/periods/compare",viewServCompare,name="compare-periods"),
    path("<int:guild>/<str:option>/periods/compareperso",viewPeriodsCompare,name="compare-periods"),
    path("<int:guild>/<str:option>/evol/compare",viewEvolCompare,name="compare-evol"),
    
    path("<int:guild>/<str:option>/first/compare",viewFirstCompare,name="compare-first"),

    path("<int:guild>/<str:option>/ranks/pantheon",viewPantheon,name="stats-ranks"),

    path("profil/<int:user>",viewProfilHome,name="user-profil"),
    path("profil/<int:user>/titres",viewProfilTitres,name="user-titres"),
    path("profil/<int:user>/custom",viewProfilPerso,name="user-custom"),

    path("jeux/home/",statsHomeJeux,name="jeux-ranks"),
    path("jeux/<str:option>/ranks/",rankJeux,name="jeux-ranks"),
    path("jeux/<str:option>/periods/",periodsJeux,name="jeux-periods"),
    path("jeux/<str:option>/evol/",evolJeux,name="jeux-evol"),
    path("jeux/<str:option>/first/",firstJeux,name="jeux-first"),
    path("jeux/<str:option>/badges/",viewBadges,name="jeux-first"),

    path("jeux/<str:option>/iframeranks",iFrameRankJeux,name="jeux-iframe-ranks"),
    path("jeux/<str:option>/iframeperiods",iFramePeriodsJeux,name="jeux-iframe-periods"),
    path("jeux/<str:option>/iframefirst",iFrameFirstJeux,name="jeux-iframe-first"),

    path("mixes/<int:mix>/<str:option>/ranks/",mixRank,name="stats-ranks"),
    path("mixes/<int:mix>/<str:option>/periods/",mixServ,name="stats-periods"),

    path("mixes/<int:mix>/<str:option>/periods/perso",mixPeriods,name="stats-serv"),
    path("mixes/<int:mix>/<str:option>/ranks/perso",mixPerso,name="stats-perso"),

    path("mixes/<int:mix>/<str:option>/iframeranks",iFrameMixRank,name="iframe-ranks"),
    path("mixes/<int:mix>/<str:option>/iframeperiods",iFrameMixPeriods,name="iframe-periods"),
    path("mixes/<int:mix>/<str:option>/iframeserv",iFrameMixServ,name="iframe-serv"),
    path("mixes/<int:mix>/<str:option>/iframeperso",iFrameMixPerso,name="iframe-perso"),

    path("mixes/<int:mix>/del",delMix,name="del-mix"),

    path("pin",ajoutPin),
    path("pin/add",ajoutPin),
    path("pin/del",delPin),

    path("ot/titres",viewOTTitres,name="del-mix"),
    path("ot/stats",viewOTStats,name="del-mix"),
    
]
