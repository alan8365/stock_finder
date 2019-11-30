from django.shortcuts import render
from .models import Foreign, Investment


# Create your views here.
def index(request):

    template = 'index.html'

    return render(request, template, {
        'bubu': 'bubu'
    })
