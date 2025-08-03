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
    path('', views.dashboard, name='dashboard'),
    path('test/', views.test_page, name='test_page'),
    path('export/csv/', views.export_deals_csv, name='export_deals_csv'),
] 