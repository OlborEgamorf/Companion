from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="companion-home"),
    path("<int:guild>/messages/<str:section>",views.guildMessages,name="companion-guild-home"),
    path("<int:guild>/iframeevol",views.iFrameEvol,name="iframe-evol"),
    path("<int:guild>/iframerank",views.iFrameRank,name="iframe-rank"),
    path("<int:guild>/iframearchive",views.iFrameArchive,name="iframe-archive"),
    path("<int:guild>/iframeroles",views.iFrameRoles,name="iframe-roles"),
    path("iframeblank",views.iFrameBlank,name="iframe-blank")
]