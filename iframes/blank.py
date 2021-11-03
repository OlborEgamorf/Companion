from django.shortcuts import render

def iFrameBlank(request):
    return render(request,"companion/blank.html")