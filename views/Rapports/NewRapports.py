from companion.outils import getMoisAnnee
from companion.views.Rapports.RapportAnnee import rapportAnnee
from companion.views.Rapports.RapportsGlobal import rapportGlobal
from companion.views.Rapports.RapportsMois import rapportMois
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
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
    
    return render(request, "companion/NewRapports.html", ctx)
