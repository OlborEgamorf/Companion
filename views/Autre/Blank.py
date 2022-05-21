from django.shortcuts import render

def iFrameBlank(request):
    return render(request,"companion/Blank/blank.html",{"option":request.GET.get("option"),"command":request.GET.get("command"),"plus":request.GET.get("plus")})
