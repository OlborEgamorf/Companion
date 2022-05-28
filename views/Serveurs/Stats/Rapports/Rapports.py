from companion.tools.Decorator import CompanionStats
from companion.tools.outils import getMoisAnnee
from companion.views.Serveurs.Stats.Rapports.Annee import rapportAnnee
from companion.views.Serveurs.Stats.Rapports.Global import rapportGlobal
from companion.views.Serveurs.Stats.Rapports.Mois import rapportMois
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
@CompanionStats
def viewRapports(request,guild,option):
    user=request.user
    mois,annee = request.GET.get("mois"),request.GET.get("annee")
    mois,annee,moisDB,anneeDB=getMoisAnnee(mois,annee)

    if moisDB=="glob":
        ctx=rapportGlobal(guild,option,request,user,moisDB,anneeDB,mois,annee)
    elif moisDB=="to":
        ctx=rapportAnnee(guild,option,request,user,moisDB,anneeDB,mois,annee)
    else:
        ctx=rapportMois(guild,option,request,user,moisDB,anneeDB,mois,annee)
    
    return render(request, "companion/Stats/Rapports.html", ctx)
