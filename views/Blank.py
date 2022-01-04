from django.shortcuts import render

def iFrameBlank(request):
    return render(request,"companion/Blank/blank.html")

def iFrameBlankCompare(request):
    return render(request, "companion/Blank/blankcompare.html")