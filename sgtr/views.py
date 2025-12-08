from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def index(request):
    """
    Vista principal inteligente:
    - Si el usuario NO está logueado -> Muestra Landing Page.
    - Si el usuario SÍ está logueado -> Muestra Dashboard (home.html).
    """
    if request.user.is_authenticated:
        return render(request, 'home.html')
    else:
        return render(request, 'landing.html')

def landing(request):
    """
    Vista de landing page - siempre muestra la landing page.
    Usada para logout redirect.
    """
    return render(request, 'landing.html')
