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
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/export/', views.CSVExportView.as_view(), name='csv_export'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('help/', views.HelpView.as_view(), name='help'),
    path('impressum/', views.ImpressumView.as_view(), name='impressum'),
] 