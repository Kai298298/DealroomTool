"""
Views für die Core-App (Dashboard)
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import csv
from django.http import HttpResponse
from deals.models import Deal, DealChangeLog
from files.models import GlobalFile
from users.models import CustomUser


def test_page(request):
    """Öffentliche Test-Seite für Server-Verifizierung"""
    return render(request, 'core/test_page.html', {
        'server_status': 'Running',
        'django_version': '5.2.4',
        'project_name': 'Dealroom Dashboard',
        'features': [
            'Automatische Website-Generierung',
            'GrapesJS Editor',
            'Datei-Management',
            'Benutzer-Rollen',
            'Analytics',
            'A/B Testing'
        ]
    })

@login_required
def dashboard(request):
    """Dashboard-View für eingeloggte Benutzer"""
    user = request.user
    
    # Hole relevante Daten
    deals = Deal.objects.filter(created_by=user).order_by('-created_at')
    
    # Suchfunktion
    search_query = request.GET.get('search', '')
    if search_query:
        deals = deals.filter(
            Q(title__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Status-Filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        deals = deals.filter(status=status_filter)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(deals, 10)  # 10 Dealrooms pro Seite
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Andere Daten
    active_deals = deals.filter(status='active')
    draft_deals = deals.filter(status='draft')
    global_files = GlobalFile.objects.filter(uploaded_by=user).order_by('-uploaded_at')[:5]
    recent_changes = DealChangeLog.objects.filter(deal__created_by=user).order_by('-changed_at')[:10]
    
    # Statistiken
    total_deals = deals.count()
    total_files = GlobalFile.objects.filter(uploaded_by=user).count()
    
    context = {
        'deals': deals,
        'dealrooms': page_obj,  # Paginierte Dealrooms
        'active_deals': active_deals,
        'draft_deals': draft_deals,
        'global_files': global_files,
        'recent_changes': recent_changes,
        'total_deals': total_deals,
        'total_files': total_files,
        'recent_global_files': global_files,  # Alias für Template-Kompatibilität
        'paginator': paginator,
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'core/dashboard.html', context)

def export_deals_csv(request):
    """Export Dealrooms als CSV"""
    if not request.user.is_authenticated:
        return redirect('users:login')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dealrooms.csv"'
    
    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'ID', 'Titel', 'Slug', 'Beschreibung', 'Status', 'Template-Typ',
        'Empfänger Name', 'Empfänger E-Mail', 'Empfänger Firma',
        'Hero Titel', 'Hero Untertitel', 'Call-to-Action',
        'Primärfarbe', 'Sekundärfarbe', 'Website Status',
        'Öffentliche URL', 'Lokale Website URL',
        'Erstellt von', 'Erstellt am', 'Aktualisiert von', 'Aktualisiert am',
        'Anzahl Dateien', 'Anzahl Änderungen'
    ])
    
    deals = Deal.objects.filter(created_by=request.user)
    for deal in deals:
        # Zähle Dateien und Änderungen
        file_count = deal.files.count()
        change_count = deal.change_logs.count()
        
        writer.writerow([
            deal.id, deal.title, deal.slug, deal.description or '', deal.status, deal.template_type or '',
            deal.recipient_name or '', deal.recipient_email or '', deal.company_name or '',
            deal.hero_title or '', deal.hero_subtitle or '', deal.call_to_action or '',
            deal.primary_color or '', deal.secondary_color or '', deal.website_status or '',
            deal.public_url or '', deal.local_website_url or '',
            deal.created_by.get_full_name() or deal.created_by.username,
            deal.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            deal.updated_by.get_full_name() if deal.updated_by else '',
            deal.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            file_count, change_count
        ])
    
    return response
