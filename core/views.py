"""
Views für die Core-App (Dashboard)
"""
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.core.paginator import Paginator
from deals.models import Deal, DealFile
from users.models import CustomUser


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard-Startseite mit Übersicht über alle wichtigen Daten
    """
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiken für das Dashboard
        context['total_dealrooms'] = Deal.objects.count()
        context['active_dealrooms'] = Deal.objects.filter(status='active').count()
        context['total_templates'] = Deal.objects.filter(status='active').count()
        context['total_files'] = DealFile.objects.count()
        context['total_users'] = CustomUser.objects.count()
        
        # Suchfunktion
        search_query = self.request.GET.get('search', '')
        context['search_query'] = search_query
        
        # Dealrooms mit Suchfilter
        dealrooms = Deal.objects.select_related('created_by').order_by('-created_at')
        
        if search_query:
            dealrooms = dealrooms.filter(
                Q(title__icontains=search_query) |
                Q(company_name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(created_by__username__icontains=search_query) |
                Q(created_by__first_name__icontains=search_query) |
                Q(created_by__last_name__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(dealrooms, 10)  # 10 Dealrooms pro Seite
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['dealrooms'] = page_obj
        context['paginator'] = paginator
        
        return context


class AboutView(TemplateView):
    """
    Über-Seite mit Informationen über das System
    """
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Über das Dealroom Dashboard'
        context['description'] = 'Ein modernes Dashboard zur Verwaltung von Dealroom-Daten und Templates für Landingpages.'
        return context


class HelpView(TemplateView):
    """
    Hilfe-Seite mit Anleitungen und Dokumentation
    """
    template_name = 'core/help.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Hilfe & Dokumentation'
        context['description'] = 'Anleitungen und Hilfe für die Nutzung des Dealroom Dashboards.'
        return context


class ImpressumView(TemplateView):
    """
    Impressum-Seite mit rechtlichen Informationen
    """
    template_name = 'core/impressum.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Impressum'
        context['description'] = 'Rechtliche Informationen und Kontaktdaten.'
        return context


class LoginSuccessView(TemplateView):
    """
    Login-Erfolgs-Seite
    """
    template_name = 'core/login_success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login erfolgreich'
        context['description'] = 'Anmeldung erfolgreich abgeschlossen.'
        return context
