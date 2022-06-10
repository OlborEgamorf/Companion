from companion.tools.outils import connectSQL
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url="/login")
def viewOTSupport(request):
    user=request.user
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    user_full=curseurGet.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()

    ctx={"avatar":user_full["Avatar"],"id":user.id,"nom":user_full["Nom"],"ot":True,"guildname":"Supporter le projet",
        "options":["stats","titres","support"],"dictOptions":{"home":"Accueil","titres":"Titres","support":"Soutenir le projet","stats":"Stats"},"option":"support"}

    return render(request, "companion/OT/Support.html", ctx)
