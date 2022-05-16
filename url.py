from django.urls import path

from companion.views.Pantheon import viewPantheon

from .compare.EvolCompare import viewEvolCompare
from .compare.FirstCompare import viewFirstCompare
from .compare.PeriodsCompare import viewPeriodsCompare
from .compare.PersoCompare import viewPersoCompare
from .compare.RanksCompare import viewRankCompare
from .compare.ServCompare import viewServCompare
from .views.Blank import iFrameBlank, iFrameBlankCompare
from .views.emotesmondial import emotesMondial, iframeEmotes
from .views.EmotesWW import emotesMondialGuild
from .views.Evol import evolJeux, iFrameEvol, viewEvol
from .views.First import firstJeux, iFrameFirst, iFrameFirstJeux, viewFirst
from .views.graphiques import (graphEvol, graphFirst, graphJours, graphPeriods,
                               graphRanks, iFrameGraphEvol, iFrameGraphFirst,
                               iFrameGraphJours, iFrameGraphPeriods,
                               iFrameGraphRanks)
from .views.GuildHome import viewGuildHome
from .views.HallOfBadges import viewBadges
from .views.home import home
from .views.Jours import iFrameJour, viewJours
from .views.Periods import (iFramePeriods, iFramePeriodsJeux, periodsJeux,
                            viewPeriods)
from .views.Perso import iFramePerso, viewPerso
from .views.Profil import viewProfilHome, viewProfilPerso, viewProfilTitres
from .views.Rank import (iFrameRank, iFrameRankJeux, rankJeux, viewRank,
                         viewRankObj)
from .views.Rapports import viewRapports
from .views.Roles import iFrameRoles, viewRoles
from .views.Serv import iFrameServ, viewServ
from .views.StatsHome import statsHomeJeux, viewStatsHome

urlpatterns = [
    path('', home, name="companion-home"),
    path("<int:guild>",viewGuildHome,name="guild-home"),

    path("<int:guild>/home",viewStatsHome,name="stats-home"),
    path("<int:guild>/<str:option>/ranks",viewRank,name="stats-ranks"),
    path("<int:guild>/<str:option>/periods",viewServ,name="stats-periods"),
    path("<int:guild>/<str:option>/evol",viewEvol,name="stats-evol"),
    path("<int:guild>/<str:option>/jours",viewJours,name="stats-jours"),
    path("<int:guild>/<str:option>/roles",viewRoles,name="stats-roles"),
    path("<int:guild>/<str:option>/first",viewFirst,name="stats-first"),
    path("<int:guild>/<str:option>/rapport",viewRapports,name="stats-rapport"),
    path("<int:guild>/emotes/mondial",emotesMondialGuild,name="guild-emotes-mondial"),

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
    path("iframeblankcompare",iFrameBlankCompare,name="iframe-blank-compare"),

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

    path("jeux/home",statsHomeJeux,name="jeux-ranks"),
    path("jeux/<str:option>/ranks",rankJeux,name="jeux-ranks"),
    path("jeux/<str:option>/periods",periodsJeux,name="jeux-periods"),
    path("jeux/<str:option>/evol",evolJeux,name="jeux-evol"),
    path("jeux/<str:option>/first",firstJeux,name="jeux-first"),
    path("jeux/<str:option>/badges",viewBadges,name="jeux-first"),

    path("jeux/<str:option>/iframeranks",iFrameRankJeux,name="jeux-iframe-ranks"),
    path("jeux/<str:option>/iframeperiods",iFramePeriodsJeux,name="jeux-iframe-periods"),
    path("jeux/<str:option>/iframefirst",iFrameFirstJeux,name="jeux-iframe-first"),
]
