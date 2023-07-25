from django.shortcuts import render
from django.shortcuts import HttpResponse


# Create your views here.
def store(request):
    return render(request, 'store/store.html')