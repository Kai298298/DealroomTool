"""
Views für die Core-App (Dashboard)
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.core.paginator import Paginator
from deals.models import Deal, DealChangeLog, DealFile
from users.models import CustomUser
from files.models import GlobalFile
from django.http import HttpResponse
import csv
from datetime import datetime


class HomeView(TemplateView):
    """
    Startseite - Weiterleitung zum Dashboard für eingeloggte Benutzer
    """
    template_name = 'core/home.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('core:dashboard')
        return super().get(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard - Übersicht über alle Dealrooms und Statistiken
    """
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Alle Dealrooms
        context['deals'] = Deal.objects.all()
        
        # Aktive Dealrooms
        context['active_deals'] = Deal.objects.filter(status='active')
        
        # Entwürfe
        context['draft_deals'] = Deal.objects.filter(status='draft')
        
        # Globale Dateien
        context['global_files'] = GlobalFile.objects.all()
        
        # Neueste globale Dateien (letzte 6)
        context['recent_global_files'] = GlobalFile.objects.order_by('-uploaded_at')[:6]
        
        # Letzte Änderungen (letzte 10)
        context['recent_changes'] = DealChangeLog.objects.select_related('deal', 'changed_by').order_by('-changed_at')[:10]
        
        # Dealroom-Liste mit Suchfunktion und Pagination
        search_query = self.request.GET.get('search', '')
        status_filter = self.request.GET.get('status', '')
        context['search_query'] = search_query
        context['status_filter'] = status_filter
        
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
        
        # Status-Filter anwenden
        if status_filter:
            dealrooms = dealrooms.filter(status=status_filter)
        
        # Pagination
        paginator = Paginator(dealrooms, 10)  # 10 Dealrooms pro Seite
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['dealrooms'] = page_obj
        context['paginator'] = paginator
        
        return context


class CSVExportView(LoginRequiredMixin, TemplateView):
    """
    CSV-Export für alle Dealrooms
    """
    def get(self, request, *args, **kwargs):
        # Erstelle CSV-Response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="dealrooms_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        # CSV-Writer erstellen
        writer = csv.writer(response, delimiter=';')
        
        # Header schreiben
        writer.writerow([
            'ID',
            'Titel',
            'Slug',
            'Beschreibung',
            'Status',
            'Template-Typ',
            'Empfänger Name',
            'Empfänger E-Mail',
            'Empfänger Firma',
            'Hero Titel',
            'Hero Untertitel',
            'Call-to-Action',
            'Primärfarbe',
            'Sekundärfarbe',
            'Website Status',
            'Öffentliche URL',
            'Lokale Website URL',
            'Erstellt von',
            'Erstellt am',
            'Aktualisiert von',
            'Aktualisiert am',
            'Anzahl Dateien',
            'Anzahl Änderungen'
        ])
        
        # Dealrooms abrufen
        dealrooms = Deal.objects.select_related('created_by', 'updated_by').prefetch_related('files').all()
        
        # Daten schreiben
        for dealroom in dealrooms:
            writer.writerow([
                dealroom.id,
                dealroom.title,
                dealroom.slug,
                dealroom.description or '',
                dealroom.get_status_display(),
                dealroom.get_template_type_display(),
                dealroom.recipient_name or '',
                dealroom.recipient_email or '',
                dealroom.recipient_company or '',
                dealroom.hero_title or '',
                dealroom.hero_subtitle or '',
                dealroom.call_to_action or '',
                dealroom.primary_color or '',
                dealroom.secondary_color or '',
                dealroom.get_website_status_display(),
                dealroom.public_url or '',
                dealroom.local_website_url or '',
                dealroom.created_by.get_full_name() if dealroom.created_by else dealroom.created_by.username if dealroom.created_by else '',
                dealroom.created_at.strftime('%d.%m.%Y %H:%M') if dealroom.created_at else '',
                dealroom.updated_by.get_full_name() if dealroom.updated_by else dealroom.updated_by.username if dealroom.updated_by else '',
                dealroom.updated_at.strftime('%d.%m.%Y %H:%M') if dealroom.updated_at else '',
                dealroom.files.count(),
                DealChangeLog.objects.filter(deal=dealroom).count()
            ])
        
        return response


class AboutView(TemplateView):
    """
    Über uns - Informationen über das Tool
    """
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Über das Dealroom Dashboard'
        context['description'] = 'Ein modernes Dashboard zur Verwaltung von Dealroom-Daten und Templates für Landingpages.'
        return context


class HelpView(TemplateView):
    """
    Hilfe - Anleitungen und Dokumentation
    """
    template_name = 'core/help.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Hilfe & Dokumentation'
        context['description'] = 'Anleitungen und Hilfe für die Nutzung des Dealroom Dashboards.'
        return context


class ImpressumView(TemplateView):
    """
    Impressum - Rechtliche Informationen
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
