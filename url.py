from django.urls import path

from companion.views.home import home
from companion.views.Mixes.DelMix import delMix
from companion.views.Mixes.Periods.MixPeriods import mixPeriods
from companion.views.Mixes.Periods.MixPeriodsCompare import \
    viewMixPeriodsCompare
from companion.views.Mixes.Periods.MixServ import mixServ
from companion.views.Mixes.Periods.MixServCompare import viewMixServCompare
from companion.views.Mixes.Ranks.MixPerso import mixPerso
from companion.views.Mixes.Ranks.MixRanks import mixRank
from companion.views.Mixes.Ranks.MixRanksCompare import viewMixRankCompare
from companion.views.OT.Jeux.HallOfBadges import viewBadges
from companion.views.OT.Stats import viewOTStats
from companion.views.OT.Support import viewOTSupport
from companion.views.OT.Titres import viewOTTitres
from companion.views.Pin import ajoutPin, delPin
from companion.views.Profil.Custom import viewProfilPerso
from companion.views.Profil.Home import viewProfilHome
from companion.views.Profil.Titres import viewProfilTitres
from companion.views.Serveurs.Anniv.Anniv import (setAnniv, viewAnniv)
from companion.views.Serveurs.Home import viewGuildHome
from companion.views.Serveurs.Outils.Adieu import (addImgAD, addMessAD, chanAD,
                                                   delImgAD, delMessAD,
                                                   editImgAD, editMessAD,
                                                   simulateAD, toggleAD,
                                                   toggleImgAD, toggleMessAD,
                                                   viewGestionAD)
from companion.views.Serveurs.Outils.AnnivAuto import (addImgAnniv,
                                                       addMessAnniv, chanAnniv,
                                                       delImgAnniv,
                                                       delMessAnniv,
                                                       editImgAnniv,
                                                       editMessAnniv,
                                                       simulateAnniv,
                                                       toggleAnniv,
                                                       toggleImgAnniv,
                                                       toggleMessAnniv, viewGestionAnniv)
from companion.views.Serveurs.Outils.Bienvenue import (addImgBV, addMessBV,
                                                       chanBV, delImgBV,
                                                       delMessBV, editImgBV,
                                                       editMessBV, simulateBV,
                                                       toggleBV, toggleImgBV,
                                                       toggleMessBV,
                                                       viewGestionBV)
from companion.views.Serveurs.Outils.Tableaux import (addTab, delTab, editTab,
                                                      toggleTab,
                                                      toggleTableaux,
                                                      viewGestionTableaux)
from companion.views.Serveurs.Outils.VoiceEphem import viewGestionVoiceEphem
from companion.views.Serveurs.Polls.Petitions import (createPetition,
                                                      viewPetitions,
                                                      votePetition)
from companion.views.Serveurs.Polls.Polls import (answerPoll, createPoll,
                                                  viewPolls)
from companion.views.Serveurs.Stats.Evol.Evol import evolJeux, viewEvol
from companion.views.Serveurs.Stats.Evol.EvolCompare import (compareEvolJeux,
                                                             viewEvolCompare)
from companion.views.Serveurs.Stats.Evol.EvolGraph import (graphEvol,
                                                           graphEvolJeux,
                                                           iFrameGraphEvol,
                                                           iFrameGraphEvolJeux)
from companion.views.Serveurs.Stats.First.First import firstJeux, viewFirst
from companion.views.Serveurs.Stats.First.FirstCompare import (
    compareFirstJeux, viewFirstCompare)
from companion.views.Serveurs.Stats.First.FirstGlobal import (firstGlobalJeux,
                                                              viewFirstGlobal)
from companion.views.Serveurs.Stats.First.FirstGraph import (
    graphFirst, graphFirstJeux, iFrameGraphFirst, iFrameGraphFirstJeux)
from companion.views.Serveurs.Stats.Home import statsHomeJeux, viewStatsHome
from companion.views.Serveurs.Stats.Jours.Jours import viewJours
from companion.views.Serveurs.Stats.Jours.JoursGraph import (graphJours,
                                                             iFrameGraphJours)
from companion.views.Serveurs.Stats.Periods.MorePeriods import (
    getGraphPeriods, getIndicsPeriods)
from companion.views.Serveurs.Stats.Periods.Periods import (periodsJeux,
                                                            viewPeriods)
from companion.views.Serveurs.Stats.Periods.PeriodsCompare import (
    comparePeriodsJeux, viewPeriodsCompare)
from companion.views.Serveurs.Stats.Periods.PeriodsGraph import (
    graphPeriods, graphPeriodsJeux, iFrameGraphPeriods, iFrameGraphPeriodsJeux)
from companion.views.Serveurs.Stats.Periods.Serv import viewServ
from companion.views.Serveurs.Stats.Periods.ServCompare import viewServCompare
from companion.views.Serveurs.Stats.Ranks.MoreRanks import (getAvAp, getEvol,
                                                            getHistoFirst,
                                                            getIndics)
from companion.views.Serveurs.Stats.Ranks.Pantheon import (morePantheon,
                                                           pantheonJeux,
                                                           viewPantheon)
from companion.views.Serveurs.Stats.Ranks.Perso import viewPerso
from companion.views.Serveurs.Stats.Ranks.PersoCompare import viewPersoCompare
from companion.views.Serveurs.Stats.Ranks.PersoGlobal import viewPersoGlobal
from companion.views.Serveurs.Stats.Ranks.Rank import (rankJeux, viewRank,
                                                       viewRankObj)
from companion.views.Serveurs.Stats.Ranks.RanksCompare import (compareRankJeux,
                                                               viewRankCompare)
from companion.views.Serveurs.Stats.Ranks.RanksGlobal import (ranksGlobalJeux,
                                                              viewRanksGlobal)
from companion.views.Serveurs.Stats.Ranks.RanksGraph import (
    graphRanks, graphRanksJeux, iFrameGraphRanks, iFrameGraphRanksJeux)
from companion.views.Serveurs.Stats.Rapports.Rapports import viewRapports
from companion.views.Serveurs.Stats.Recap import (addMoreRecap,
                                                  addMoreRecapJeux, recapJeux,
                                                  viewRecapStats)
from companion.views.Serveurs.SV.SV import (addSV, editSV, viewAddSV,
                                            viewModoSV, viewPersoSV,
                                            viewSVRandom)
from companion.views.Serveurs.Timeline.Timeline import viewTimeline

urlpatterns = [
    path('', home, name="companion-home"),
    path("<int:guild>",viewGuildHome,name="guild-home"),

    path("<int:guild>/stats/",viewStatsHome,name="stats-home"),
    path("<int:guild>/stats/recap/<str:option>/",viewRecapStats,name="stats-ranks"),
    path("<int:guild>/stats/ranks/<str:option>/",viewRank,name="stats-ranks"),
    path("<int:guild>/stats/periods/<str:option>/",viewServ,name="stats-periods"),
    path("<int:guild>/stats/evol/<str:option>/",viewEvol,name="stats-evol"),
    path("<int:guild>/stats/jours/<str:option>/",viewJours,name="stats-jours"),
    path("<int:guild>/stats/first/<str:option>/",viewFirst,name="stats-first"),
    path("<int:guild>/stats/rapport/<str:option>/",viewRapports,name="stats-rapport"),
    
    path("<int:guild>/stats/ranks",viewRanksGlobal,name="stats-ranks"),
    path("<int:guild>/stats/first",viewFirstGlobal,name="stats-ranks"),
    path("<int:guild>/stats/ranks/perso",viewPersoGlobal,name="stats-ranks"),
    path("<int:guild>/stats/ranks/perso/<str:option>",viewPerso,name="stats-perso"),
    path("<int:guild>/stats/periods/perso/<str:option>",viewPeriods,name="stats-serv"),

    path("<int:guild>/stats/ranks/obj/<str:option>",viewRankObj,name="compare-perso"),
    path("<int:guild>/stats/ranks/pantheon/<str:option>",viewPantheon,name="stats-ranks"),

    path("<int:guild>/stats/ranks/compare/<str:option>",viewRankCompare,name="compare-ranks"),
    path("<int:guild>/stats/periods/compare/<str:option>",viewServCompare,name="compare-periods"),
    path("<int:guild>/stats/evol/compare/<str:option>",viewEvolCompare,name="compare-evol"),
    path("<int:guild>/stats/first/compare/<str:option>",viewFirstCompare,name="compare-first"),

    path("<int:guild>/stats/ranks/compareperso/<str:option>",viewPersoCompare,name="compare-perso"),
    path("<int:guild>/stats/periods/compareperso/<str:option>",viewPeriodsCompare,name="compare-periods"),

    path("<int:guild>/stats/ranks/graphs/<str:option>",graphRanks,name="graphs-ranks"),
    path("<int:guild>/stats/periods/graphs/<str:option>",graphPeriods,name="graphs-periods"),
    path("<int:guild>/stats/evol/graphs/<str:option>",graphEvol,name="graphs-periods"),
    path("<int:guild>/stats/first/graphs/<str:option>",graphFirst,name="graphs-periods"),
    path("<int:guild>/stats/jours/graphs/<str:option>",graphJours,name="graphs-periods"),

    path("<int:guild>/<str:option>/iframeranks/graphs",iFrameGraphRanks,name="iframe-graphs-ranks"),
    path("<int:guild>/<str:option>/iframeperiods/graphs",iFrameGraphPeriods,name="iframe-graphs-ranks"),
    path("<int:guild>/<str:option>/iframeevol/graphs",iFrameGraphEvol,name="iframe-graphs-ranks"),
    path("<int:guild>/<str:option>/iframefirst/graphs",iFrameGraphFirst,name="iframe-graphs-ranks"),
    path("<int:guild>/<str:option>/iframejours/graphs",iFrameGraphJours,name="iframe-graphs-ranks"),

    path("<int:guild>/sondages/",viewPolls,name="stats-home"),
    path("<int:guild>/sondages/create",createPoll,name="stats-home"),
    path("<int:guild>/sondages/vote/<int:pollid>",answerPoll,name="stats-home"),

    path("<int:guild>/petitions/",viewPetitions,name="stats-home"),
    path("<int:guild>/petitions/create",createPetition,name="stats-home"),
    path("<int:guild>/petitions/sign/<int:pollid>",votePetition,name="stats-home"),

    path("<int:guild>/giveaways/",viewPetitions,name="stats-home"),
    path("<int:guild>/giveaways/create",createPetition,name="stats-home"),
    path("<int:guild>/giveaways/enter/<int:pollid>",votePetition,name="stats-home"),

    path("<int:guild>/sv/",viewSVRandom,name="stats-home"),
    path("<int:guild>/sv/add/",viewAddSV,name="stats-home"),
    path("<int:guild>/sv/edit/<int:idsv>",editSV,name="stats-home"),
    path("<int:guild>/sv/perso/",viewPersoSV,name="stats-home"),
    path("<int:guild>/sv/modo/",viewModoSV,name="stats-home"),
    path("<int:guild>/sv/add/add",addSV,name="stats-home"),

    path("<int:guild>/anniv/",viewAnniv,name="stats-home"),
    path("<int:guild>/anniv/set",setAnniv,name="stats-home"),

    path("<int:guild>/timeline/",viewTimeline,name="stats-home"),

    path("<int:guild>/bienvenue/",viewGestionBV,name="stats-home"),
    path("<int:guild>/adieu/",viewGestionAD,name="stats-home"),
    path("<int:guild>/annivauto/",viewGestionAnniv,name="stats-home"),
    path("<int:guild>/tableaux/",viewGestionTableaux,name="stats-home"),
    path("<int:guild>/cmdauto/",viewGestionVoiceEphem,name="stats-home"),
    path("<int:guild>/dynicon/",viewGestionVoiceEphem,name="stats-home"),

    path("<int:guild>/bienvenue/simulate/<int:idimg>",simulateBV,name="stats-home"),
    path("<int:guild>/bienvenue/chanbv",chanBV,name="stats-home"),
    path("<int:guild>/bienvenue/togglebv/",toggleBV,name="stats-home"),
    path("<int:guild>/bienvenue/toggleimg/<int:idimg>",toggleImgBV,name="stats-home"),
    path("<int:guild>/bienvenue/togglemessage/<int:idmessage>",toggleMessBV,name="stats-home"),
    path("<int:guild>/bienvenue/editmessage/<int:idmessage>",editMessBV,name="stats-home"),
    path("<int:guild>/bienvenue/editimg/<int:idimg>",editImgBV,name="stats-home"),
    path("<int:guild>/bienvenue/addmessage/",addMessBV,name="stats-home"),
    path("<int:guild>/bienvenue/addimg",addImgBV,name="stats-home"),
    path("<int:guild>/bienvenue/delmessage/<int:idmessage>",delMessBV,name="stats-home"),
    path("<int:guild>/bienvenue/delimg/<int:idimg>",delImgBV,name="stats-home"),

    path("<int:guild>/adieu/simulate/<int:idimg>",simulateAD,name="stats-home"),
    path("<int:guild>/adieu/chanad",chanAD,name="stats-home"),
    path("<int:guild>/adieu/togglead/",toggleAD,name="stats-home"),
    path("<int:guild>/adieu/toggleimg/<int:idimg>",toggleImgAD,name="stats-home"),
    path("<int:guild>/adieu/togglemessage/<int:idmessage>",toggleMessAD,name="stats-home"),
    path("<int:guild>/adieu/editmessage/<int:idmessage>",editMessAD,name="stats-home"),
    path("<int:guild>/adieu/editimg/<int:idimg>",editImgAD,name="stats-home"),
    path("<int:guild>/adieu/addmessage/",addMessAD,name="stats-home"),
    path("<int:guild>/adieu/addimg",addImgAD,name="stats-home"),
    path("<int:guild>/adieu/delmessage/<int:idmessage>",delMessAD,name="stats-home"),
    path("<int:guild>/adieu/delimg/<int:idimg>",delImgAD,name="stats-home"),

    path("<int:guild>/annivauto/simulate/<int:idimg>",simulateAnniv,name="stats-home"),
    path("<int:guild>/annivauto/chanad",chanAnniv,name="stats-home"),
    path("<int:guild>/annivauto/toggleanniv/",toggleAnniv,name="stats-home"),
    path("<int:guild>/annivauto/toggleimg/<int:idimg>",toggleImgAnniv,name="stats-home"),
    path("<int:guild>/annivauto/togglemessage/<int:idmessage>",toggleMessAnniv,name="stats-home"),
    path("<int:guild>/annivauto/editmessage/<int:idmessage>",editMessAnniv,name="stats-home"),
    path("<int:guild>/annivauto/editimg/<int:idimg>",editImgAnniv,name="stats-home"),
    path("<int:guild>/annivauto/addmessage/",addMessAnniv,name="stats-home"),
    path("<int:guild>/annivauto/addimg",addImgAnniv,name="stats-home"),
    path("<int:guild>/annivauto/delmessage/<int:idmessage>",delMessAnniv,name="stats-home"),
    path("<int:guild>/annivauto/delimg/<int:idimg>",delImgAnniv,name="stats-home"),

    path("<int:guild>/tableaux/toggletableaux/",toggleTableaux,name="stats-home"),
    path("<int:guild>/tableaux/toggletab/<int:idtab>",toggleTab,name="stats-home"),
    path("<int:guild>/tableaux/edittab/<int:idtab>",editTab,name="stats-home"),
    path("<int:guild>/tableaux/addtab/",addTab,name="stats-home"),
    path("<int:guild>/tableaux/deltab/<int:idtab>",delTab,name="stats-home"),

    path("profil/<int:user>",viewProfilHome,name="user-profil"),
    path("profil/<int:user>/titres",viewProfilTitres,name="user-titres"),
    path("profil/<int:user>/custom",viewProfilPerso,name="user-custom"),

    path("mixes/<int:mix>/ranks/<str:option>",mixRank,name="stats-ranks"),
    path("mixes/<int:mix>/periods/<str:option>",mixServ,name="stats-periods"),

    path("mixes/<int:mix>/periods/perso/<str:option>",mixPeriods,name="stats-serv"),
    path("mixes/<int:mix>/ranks/perso/<str:option>",mixPerso,name="stats-perso"),
    path("mixes/<int:mix>/ranks/compare/<str:option>",viewMixRankCompare,name="compare-ranks"),
    path("mixes/<int:mix>/periods/compare/<str:option>",viewMixServCompare,name="compare-periods"),
    path("mixes/<int:mix>/periods/compareperso/<str:option>",viewMixPeriodsCompare,name="compare-periods"),

    path("<int:guild>/<str:option>/recapmore",addMoreRecap,name="stats-ranks"),
    path("ot/jeux/<str:option>/recapmore",addMoreRecapJeux,name="stats-ranks"),

    path("<int:guild>/<str:option>/ranksmore/indics",getIndics,name="stats-ranks"),
    path("<int:guild>/<str:option>/ranksmore/histofirst",getHistoFirst,name="stats-ranks"),
    path("<int:guild>/<str:option>/ranksmore/evol",getEvol,name="stats-ranks"),
    path("<int:guild>/<str:option>/ranksmore/avap",getAvAp,name="stats-ranks"),

    path("<int:guild>/<str:option>/pantheonmore",morePantheon,name="stats-ranks"),

    path("<int:guild>/<str:option>/periodsmore/indics",getIndicsPeriods,name="stats-ranks"),
    path("<int:guild>/<str:option>/periodsmore/graph",getGraphPeriods,name="stats-ranks"),

    path("mixes/<int:mix>/del",delMix,name="del-mix"),
    path("pin",ajoutPin),
    path("pin/add",ajoutPin),
    path("pin/del",delPin),

    path("ot/titres",viewOTTitres,name="del-mix"),
    path("ot/stats",viewOTStats,name="del-mix"),
    path("ot/support",viewOTSupport,name="del-mix"),

    path("ot/jeux/",statsHomeJeux,name="stats-home"),
    path("ot/jeux/recap/<str:option>/",recapJeux,name="stats-ranks"),
    path("ot/jeux/ranks/<str:option>/",rankJeux,name="stats-ranks"),
    path("ot/jeux/periods/<str:option>/",periodsJeux,name="stats-periods"),
    path("ot/jeux/evol/<str:option>/",evolJeux,name="stats-evol"),
    path("ot/jeux/first/<str:option>/",firstJeux,name="stats-first"),
    path("ot/jeux/badges/<str:option>/",viewBadges,name="jeux-first"),
    path("ot/jeux/ranks/pantheon/<str:option>",pantheonJeux,name="stats-ranks"),

    path("ot/jeux/ranks/compare/<str:option>",compareRankJeux,name="compare-ranks"),
    path("ot/jeux/periods/compare/<str:option>",comparePeriodsJeux,name="compare-periods"),
    path("ot/jeux/evol/compare/<str:option>",compareEvolJeux,name="compare-evol"),
    path("ot/jeux/first/compare/<str:option>",compareFirstJeux,name="compare-first"),

    path("ot/jeux/ranks/graphs/<str:option>",graphRanksJeux,name="graphs-ranks"),
    path("ot/jeux/periods/graphs/<str:option>",graphPeriodsJeux,name="graphs-periods"),
    path("ot/jeux/evol/graphs/<str:option>",graphEvolJeux,name="graphs-periods"),
    path("ot/jeux/first/graphs/<str:option>",graphFirstJeux,name="graphs-periods"),

    path("ot/jeux/<str:option>/iframeranks/graphs",iFrameGraphRanksJeux,name="iframe-graphs-ranks"),
    path("ot/jeux/<str:option>/iframeperiods/graphs",iFrameGraphPeriodsJeux,name="iframe-graphs-ranks"),
    path("ot/jeux/<str:option>/iframeevol/graphs",iFrameGraphEvolJeux,name="iframe-graphs-ranks"),
    path("ot/jeux/<str:option>/iframefirst/graphs",iFrameGraphFirstJeux,name="iframe-graphs-ranks"),

    path("ot/jeux/ranks",ranksGlobalJeux,name="stats-ranks"),
    path("ot/jeux/first",firstGlobalJeux,name="stats-ranks"),


    #path("mondial/emotes",emotesMondial,name="emotes-mondial"),
    #path("<int:emote>/iframeemotesww",iframeEmotes,name="iframe-emotesww"),
    #path("<int:guild>/<str:option>/roles",viewRoles,name="stats-roles"),
    #path("<int:guild>/emotes/mondial/",emotesMondialGuild,name="guild-emotes-mondial"),
    
]


"""path("<int:guild>/outils/voiceephem/togglevoiceephem/",toggleVoiceEphem,name="stats-home"),
    path("<int:guild>/outils/voiceephem/togglehub/<int:idhub>",toggleHub,name="stats-home"),
    path("<int:guild>/outils/voiceephem/edithub/<int:idhub>",editHub,name="stats-home"),
    path("<int:guild>/outils/voiceephem/addhub/",addHub,name="stats-home"),
    path("<int:guild>/outils/voiceephem/delhub/<int:idhub>",delHub,name="stats-home"),"""
