from django.urls import path
from .views.messages import guildMessages
from .views.home import home
from .iframes.archive import iFrameArchive
from .iframes.blank import iFrameBlank
from .iframes.evol import iFrameEvol
from .iframes.rank import iFrameRank
from .iframes.roles import iFrameRoles
from .iframes.jour import iFrameJour

urlpatterns = [
    path('', home, name="companion-home"),
    path("<int:guild>/messages/<str:section>",guildMessages,name="companion-guild-home"),
    path("<int:guild>/iframeevol",iFrameEvol,name="iframe-evol"),
    path("<int:guild>/iframerank",iFrameRank,name="iframe-rank"),
    path("<int:guild>/iframearchive",iFrameArchive,name="iframe-archive"),
    path("<int:guild>/iframeroles",iFrameRoles,name="iframe-roles"),
    path("<int:guild>/iframejour",iFrameJour,name="iframe-roles"),
    path("iframeblank",iFrameBlank,name="iframe-blank")
]