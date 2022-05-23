from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from companion.outils import connectSQL

def CompanionStats(func):
    def wrapper(*args,**kwargs):
        request=args[0]
        if len(args)==1:
            guild,option=kwargs["guild"],kwargs["option"]
            user=request.user
            try:
                connexionGuild,curseurGuild=connectSQL(guild,"Guild","Guild",None,None)
                hideblind=curseurGuild.execute("SELECT * FROM users WHERE ID={0}".format(user.id)).fetchone()
                assert not hideblind["Blind"]
                assert not hideblind["Leave"]
                assert curseurGuild.execute("SELECT * FROM stats").fetchone()["Active"]
            except AssertionError:
                raise PermissionDenied
        try:
            return func(*args,**kwargs)
        except AssertionError:
            return render(request,"companion/Erreurs/DateError.html")
        
    return wrapper