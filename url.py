from django.urls import path

from .views.EmotesWW import emotesMondialGuild

from .views.First import iFrameFirst, viewFirst

from .views.Blank import iFrameBlank, iFrameBlankCompare
from .views.emotesmondial import emotesMondial, iframeEmotes
from .views.Evol import iFrameEvol, viewEvol
from .views.graphiques import guildGraph
from .views.home import home
from .views.Jours import iFrameJour, viewJours
from .views.Periods import iFramePeriods, viewPeriods
from .views.Perso import iFramePerso, viewPerso
from .views.Rank import iFrameRank, iFrameRankObj, viewRank
from .views.Roles import iFrameRoles, viewRoles
from .views.Serv import iFrameServ, viewServ

urlpatterns = [
    path('', home, name="companion-home"),


    path("<int:guild>/<str:option>/ranks",viewRank,name="guild-ranks"),
    path("<int:guild>/<str:option>/periods",viewPeriods,name="guild-periods"),
    path("<int:guild>/<str:option>/evol",viewEvol,name="guild-evol"),
    path("<int:guild>/<str:option>/jours",viewJours,name="guild-jours"),
    path("<int:guild>/<str:option>/roles",viewRoles,name="guild-roles"),
    path("<int:guild>/<str:option>/serv",viewServ,name="guild-serv"),
    path("<int:guild>/<str:option>/perso",viewPerso,name="guild-perso"),
    path("<int:guild>/<str:option>/first",viewFirst,name="guild-first"),
    path("<int:guild>/emotes/mondial",emotesMondialGuild,name="guild-emotes-mondial"),

    path("<int:guild>/<str:option>/iframeranks",iFrameRank,name="iframe-ranks"),
    path("<int:guild>/<str:option>/iframeperiods",iFramePeriods,name="iframe-periods"),
    path("<int:guild>/<str:option>/iframeevol",iFrameEvol,name="iframe-evol"),
    path("<int:guild>/<str:option>/iframejours",iFrameJour,name="iframe-jours"),
    path("<int:guild>/<str:option>/iframeroles",iFrameRoles,name="iframe-roles"),
    path("<int:guild>/<str:option>/iframeranksobj",iFrameRankObj,name="iframe-ranks-obj"),
    path("<int:guild>/<str:option>/iframeserv",iFrameServ,name="iframe-serv"),
    path("<int:guild>/<str:option>/iframeperso",iFramePerso,name="iframe-perso"),
    path("<int:guild>/<str:option>/iframefirst",iFrameFirst,name="iframe-first"),


    path("iframeblank",iFrameBlank,name="iframe-blank"),
    path("iframeblankcompare",iFrameBlankCompare,name="iframe-blank-compare"),
    path("<int:guild>/graphs/messages/<str:section>",guildGraph,name="companion-guild-home"),


    path("mondial/emotes",emotesMondial,name="emotes-mondial"),
    path("<int:emote>/iframeemotesww",iframeEmotes,name="iframe-emotesww")
]
