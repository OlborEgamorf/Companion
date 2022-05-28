from companion.tools.outils import connectSQL
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required(login_url="/login")
def delMix(request,mix):
    user=request.user
    connexionMix,curseurMix=connectSQL("OT","Mixes","Guild",None,None)

    curseurMix.execute("DELETE FROM mixes_{0} WHERE Nombre={1}".format(user.id,mix))
    
    for i in curseurMix.execute("SELECT * FROM mixes_{0} WHERE Nombre>{1} ORDER BY Nombre ASC".format(user.id,mix)).fetchall():
        curseurMix.execute("UPDATE mixes_{0} SET Nombre={1} WHERE Nombre={2}".format(user.id,mix-1,mix))

    connexionMix.commit()
    return redirect("/companion")
