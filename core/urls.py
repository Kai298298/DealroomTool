"""
URL-Konfiguration für die Core-App (Dashboard)
"""
from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'core'

def redirect_to_dashboard(request):
    """Weiterleitung zur Dashboard-Seite"""
    return redirect('core:dashboard')

urlpatterns = [
    # Root-URL (Startseite)
    path('', redirect_to_dashboard, name='home'),
    
    # Dashboard-Startseite
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Über-Seite
    path('about/', views.AboutView.as_view(), name='about'),
    
    # Hilfe-Seite
    path('help/', views.HelpView.as_view(), name='help'),
    
    # Impressum-Seite
    path('impressum/', views.ImpressumView.as_view(), name='impressum'),
    
    # Login-Erfolgs-Seite
    path('login-success/', views.LoginSuccessView.as_view(), name='login_success'),
] 