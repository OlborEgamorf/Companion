from django.http import HttpResponse

from companion.outils import connectSQL

def ajoutPin(request):
    guild,command,option,plus = request.GET.get("guild"),request.GET.get("command"),request.GET.get("option"),request.GET.get("plus")
    print(guild,command,option,plus)
    user=request.user
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    curseurGet.execute("CREATE TABLE IF NOT EXISTS pin_{0} (Guild TEXT, Option TEXT, Command TEXT, Plus TEXT)".format(user.id))
    curseurGet.execute("INSERT INTO pin_{0} VALUES ('{1}','{2}','{3}','{4}')".format(user.id,guild,option,command,plus))
    connexionGet.commit()
    return HttpResponse("Retirer de l'accès rapide") 


def delPin(request):
    guild,command,option,plus = request.GET.get("guild"),request.GET.get("command"),request.GET.get("option"),request.GET.get("plus")
    print(guild,command,option,plus)
    user=request.user
    connexionGet,curseurGet=connectSQL("OT","Meta","Guild",None,None)
    curseurGet.execute("DELETE FROM pin_{0} WHERE Guild='{1}' AND Option='{2}' AND Command='{3}' AND Plus='{4}'".format(user.id,guild,option,command,plus))
    connexionGet.commit()
    return HttpResponse("Épingler à l'accès rapide") 