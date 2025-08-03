"""
Models für das Dealroom-Dashboard - Deals als Landingpages
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
import os
from django.conf import settings

User = get_user_model()


class Deal(models.Model):
    """
    Deal-Modell - Jeder Deal ist eine Landingpage
    """
    
    class DealStatus(models.TextChoices):
        DRAFT = 'draft', _('Entwurf')
        ACTIVE = 'active', _('Aktiv')
        INACTIVE = 'inactive', _('Inaktiv')
        ARCHIVED = 'archived', _('Archiviert')
    
    class TemplateType(models.TextChoices):
        MODERN = 'modern', _('Modern')
        CLASSIC = 'classic', _('Klassisch')
        MINIMAL = 'minimal', _('Minimalistisch')
        CORPORATE = 'corporate', _('Corporate')
        CREATIVE = 'creative', _('Kreativ')
        ELEGANT = 'elegant', _('Elegant')
        BOLD = 'bold', _('Bold')
        TECH = 'tech', _('Tech')
        LUXURY = 'luxury', _('Luxury')
        CLEAN = 'clean', _('Clean')
    
    class ThemeType(models.TextChoices):
        LIGHT = 'light', _('Hell')
        DARK = 'dark', _('Dunkel')
        AUTO = 'auto', _('Automatisch (System)')
    
    class URLType(models.TextChoices):
        FRIENDLY = 'friendly', _('Benutzerfreundlich (Name-basiert)')
        RANDOM = 'random', _('Random-Nummern (Sicher)')
    
    # Grundlegende Informationen
    title = models.CharField(
        max_length=200,
        unique=True,
        verbose_name=_('Titel')
    )
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name=_('URL-Slug')
    )
    
    # URL-Typ für Landingpage
    url_type = models.CharField(
        max_length=20,
        choices=URLType.choices,
        default=URLType.FRIENDLY,
        verbose_name=_('URL-Typ'),
        help_text=_('Benutzerfreundliche URLs oder sichere Random-Nummern')
    )
    
    random_url_code = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_('Random-URL-Code'),
        help_text=_('Automatisch generierter Code für sichere URLs')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Beschreibung')
    )
    
    # Status und Template
    status = models.CharField(
        max_length=20,
        choices=DealStatus.choices,
        default=DealStatus.DRAFT,
        verbose_name=_('Status')
    )
    
    template_type = models.CharField(
        max_length=20,
        choices=TemplateType.choices,
        default=TemplateType.MODERN,
        verbose_name=_('Template-Typ')
    )
    
    theme_type = models.CharField(
        max_length=10,
        choices=ThemeType.choices,
        default=ThemeType.LIGHT,
        verbose_name=_('Theme-Typ')
    )
    
    # Benutzer und Datum
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_deals',
        verbose_name=_('Erstellt von')
    )
    
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_deals',
        verbose_name=_('Aktualisiert von')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Erstellt am')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Aktualisiert am')
    )
    
    # Deal-spezifische Felder
    # Dealroom-spezifische Felder
    company_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Firmenname')
    )
    
    # Empfänger-Informationen
    recipient_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Empfänger Name')
    )
    
    recipient_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Empfänger E-Mail')
    )
    
    recipient_company = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Empfänger Firma')
    )
    
    # Kunden-Informationen
    customer_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Kundenname')
    )
    
    customer_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Kunden E-Mail')
    )
    
    customer_info = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Informationen zum Kunden')
    )
    
    # Video-Informationen
    central_video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Zentrales Video (YouTube/Vimeo)')
    )
    
    central_video_file = models.FileField(
        upload_to='dealroom_videos/',
        blank=True,
        null=True,
        verbose_name=_('Zentrales Video (Datei)')
    )
    
    # Zugriffs-Tracking
    last_accessed = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Letzter Zugriff')
    )
    
    access_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Zugriffsanzahl')
    )
    
    # Landingpage-spezifische Felder
    hero_title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Hero-Titel')
    )
    
    hero_subtitle = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Hero-Untertitel')
    )
    
    call_to_action = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Call-to-Action Text')
    )
    
    # Deal-Status & Fortschritt
    deal_status = models.CharField(
        max_length=50,
        choices=[
            ('initial', _('Initial')),
            ('offer_review', _('Angebot in Prüfung')),
            ('contract_prepared', _('Vertragsdaten bereitgestellt')),
            ('pending_signature', _('Unterschrift ausstehend')),
            ('completed', _('Abgeschlossen')),
        ],
        default='initial',
        verbose_name=_('Deal-Status')
    )
    
    deal_progress = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Deal-Fortschritt (%)')
    )
    
    # Begrüßung & Personalisierung
    welcome_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Willkommensnachricht')
    )
    
    customer_logo_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Kunden-Logo URL')
    )
    
    # Aufgaben & To-Dos
    customer_tasks = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Kunden-Aufgaben')
    )
    
    # Kommunikation
    contact_person_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Ansprechpartner Name')
    )
    
    contact_person_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Ansprechpartner E-Mail')
    )
    
    contact_person_phone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Ansprechpartner Telefon')
    )
    
    # FAQ & Hilfe
    faq_items = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('FAQ-Elemente')
    )
    
    # Timeline & Aktivitäten
    timeline_events = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Timeline-Ereignisse')
    )
    
    # Produktbeschreibung & Details
    product_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Produktname')
    )
    
    product_description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Produktbeschreibung')
    )
    
    product_features = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Produktfeatures')
    )
    
    product_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('Produktpreis')
    )
    
    product_currency = models.CharField(
        max_length=3,
        default='EUR',
        verbose_name=_('Währung')
    )
    
    # Erweiterte Dokumentenverwaltung
    document_categories = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Dokumentenkategorien')
    )
    
    document_access_levels = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Dokumentenzugriffsebenen')
    )
    
    primary_color = models.CharField(
        max_length=7,
        default='#0d6efd',
        verbose_name=_('Primärfarbe')
    )
    
    secondary_color = models.CharField(
        max_length=7,
        default='#6c757d',
        verbose_name=_('Sekundärfarbe')
    )
    
    # SEO-Felder
    meta_title = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        verbose_name=_('Meta-Titel')
    )
    
    meta_description = models.TextField(
        max_length=160,
        blank=True,
        null=True,
        verbose_name=_('Meta-Beschreibung')
    )
    
    # Landingpage-URL
    public_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Öffentliche URL')
    )
    
    # Website-Generator-Felder
    website_status = models.CharField(
        max_length=20,
        choices=[
            ('not_generated', _('Nicht generiert')),
            ('generating', _('Wird generiert')),
            ('generated', _('Generiert')),
            ('failed', _('Generierung fehlgeschlagen')),
        ],
        default='not_generated',
        verbose_name=_('Website-Status')
    )
    
    last_generation = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Letzte Generierung')
    )
    
    generation_error = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Generierungsfehler')
    )
    
    local_website_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Lokale Website-URL')
    )
    
    # HTML-Editor Felder für manuelle Bearbeitung
    custom_html_header = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Benutzerdefinierter HTML-Header'),
        help_text=_('HTML-Code für den <head> Bereich (CSS, Meta-Tags, etc.)')
    )
    
    custom_html_body_start = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Benutzerdefinierter HTML-Body-Start'),
        help_text=_('HTML-Code nach dem <body> Tag (Navigation, etc.)')
    )
    
    custom_html_content = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Benutzerdefinierter HTML-Content'),
        help_text=_('HTML-Code für den Hauptinhalt (ersetzt automatisch generierten Content)')
    )
    
    custom_html_body_end = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Benutzerdefinierter HTML-Body-End'),
        help_text=_('HTML-Code vor dem </body> Tag (Footer, Scripts, etc.)')
    )
    
    custom_css = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Benutzerdefiniertes CSS'),
        help_text=_('Zusätzliches CSS für die Website')
    )
    
    custom_javascript = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Benutzerdefiniertes JavaScript'),
        help_text=_('Zusätzliches JavaScript für die Website')
    )
    
    html_editor_mode = models.CharField(
        max_length=20,
        choices=[
            ('auto', _('Automatisch generiert')),
            ('manual', _('Manuell bearbeitet')),
            ('hybrid', _('Hybrid (Auto + Manuell)')),
        ],
        default='auto',
        verbose_name=_('HTML-Editor-Modus')
    )
    
    last_html_edit = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Letzte HTML-Bearbeitung')
    )
    
    html_edit_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Anzahl HTML-Bearbeitungen')
    )
    
    # Passwortschutz für Landingpage
    password_protection_enabled = models.BooleanField(
        default=False,
        verbose_name=_('Passwortschutz aktiviert')
    )
    
    password_protection_password = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name=_('Passwortschutz-Passwort'),
        help_text=_('Passwort für den Zugriff auf die Landingpage (wird verschlüsselt gespeichert)')
    )
    
    password_protection_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Passwortschutz-Nachricht'),
        help_text=_('Benutzerdefinierte Nachricht für die Passwortabfrage'),
        default=_('Diese Landingpage ist passwortgeschützt. Bitte geben Sie das Passwort ein.')
    )
    
    password_protection_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Passwortversuche')
    )
    
    password_protection_last_attempt = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Letzter Passwortversuch')
    )
    
    password_protection_blocked_until = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Gesperrt bis')
    )
    
    # Passwortschutz-Einstellungen
    password_protection_max_attempts = models.PositiveIntegerField(
        default=5,
        verbose_name=_('Maximale Passwortversuche'),
        help_text=_('Anzahl der erlaubten Versuche bevor der Zugriff gesperrt wird')
    )
    
    password_protection_block_duration = models.PositiveIntegerField(
        default=15,
        verbose_name=_('Sperrdauer (Minuten)'),
        help_text=_('Dauer der Sperrung nach zu vielen Versuchen')
    )
    
    password_protection_log_attempts = models.BooleanField(
        default=True,
        verbose_name=_('Passwortversuche protokollieren'),
        help_text=_('Protokolliert alle Passwortversuche für Sicherheitsanalysen')
    )
    
    class Meta:
        verbose_name = _('Deal')
        verbose_name_plural = _('Deals')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('deals:dealroom_detail', kwargs={'pk': self.pk})
    
    def get_landingpage_url(self):
        """Gibt die öffentliche Landingpage-URL zurück"""
        if self.public_url:
            return self.public_url
        return reverse('deals:landingpage', kwargs={'deal_id': self.pk})
    
    def get_files_count(self):
        """Gibt die Anzahl der zugehörigen Dateien zurück"""
        return self.files.count()
    
    def get_total_file_size(self):
        """Gibt die Gesamtgröße aller Dateien zurück"""
        total_size = 0
        for file_obj in self.files.all():
            if file_obj.file:
                total_size += file_obj.file.size
        return total_size
    
    def is_published(self):
        """Prüft ob die Landingpage veröffentlicht ist"""
        return self.status == self.DealStatus.ACTIVE
    
    def get_template_css_class(self):
        """Gibt CSS-Klasse für Template-Typ zurück"""
        return f"template-{self.template_type}"
    
    def get_assigned_files(self, role=None):
        """Gibt die zugeordneten Dateien zurück, optional gefiltert nach Rolle"""
        queryset = self.file_assignments.select_related('global_file').order_by('order')
        if role:
            queryset = queryset.filter(role=role)
        return queryset
    
    def get_hero_images(self):
        """Gibt alle Hero-Bilder zurück"""
        return self.get_assigned_files(role='hero_image')
    
    def get_logos(self):
        """Gibt alle Logos zurück"""
        return self.get_assigned_files(role='logo')
    
    def get_gallery_files(self):
        """Gibt alle Galerie-Dateien zurück"""
        return self.get_assigned_files(role='gallery')
    
    def get_documents(self):
        """Gibt alle Dokumente zurück"""
        return self.get_assigned_files(role='document')
    
    def get_videos(self):
        """Gibt alle Videos zurück"""
        return self.get_assigned_files(role='video')
    
    def get_data_files(self):
        """Gibt alle Daten-Dateien zurück"""
        return self.get_assigned_files(role='data')
    
    def get_file_size_display(self):
        """Gibt die Dateigröße benutzerfreundlich zurück"""
        size = self.get_file_size()
        return size if size != "Unbekannt" else "0 B"
    
    # Template-Methoden für schnelle Erstellung
    @classmethod
    def create_from_template(cls, template_name, **kwargs):
        """Erstellt einen Deal basierend auf einem Template"""
        templates = {
            'software_offer': {
                'product_name': 'Premium Software Lösung',
                'product_description': 'Eine umfassende Software-Lösung für Ihr Unternehmen mit modernster Technologie und benutzerfreundlicher Oberfläche.',
                'product_features': [
                    {'text': 'Cloud-basiert', 'icon': '☁️'},
                    {'text': '24/7 Support', 'icon': '🛟'},
                    {'text': 'Automatische Updates', 'icon': '🔄'},
                    {'text': 'DSGVO-konform', 'icon': '🔒'}
                ],
                'product_price': 2999.99,
                'product_currency': 'EUR',
                'deal_status': 'offer_review',
                'deal_progress': 65,
                'welcome_message': 'Willkommen in Ihrem persönlichen Dealroom!',
                'customer_tasks': [
                    {'title': 'Angebot prüfen', 'description': 'Bitte prüfen Sie das Angebot sorgfältig', 'completed': False, 'due_date': '2024-01-20'},
                    {'title': 'Dokumente signieren', 'description': 'Unterschreiben Sie die bereitgestellten Dokumente', 'completed': False, 'due_date': '2024-01-25'}
                ],
                'contact_person_name': 'Max Mustermann',
                'contact_person_email': 'max@example.com',
                'contact_person_phone': '+49 123 456789',
                'faq_items': [
                    {'question': 'Wie funktioniert die Software?', 'answer': 'Die Software ist cloud-basiert und kann über jeden Browser genutzt werden.'},
                    {'question': 'Gibt es Support?', 'answer': 'Ja, wir bieten 24/7 Support für alle Kunden.'}
                ],
                'timeline_events': [
                    {'date': '2024-01-15', 'title': 'Dealroom erstellt', 'description': 'Ihr persönlicher Dealroom wurde angelegt'},
                    {'date': '2024-01-16', 'title': 'Angebot erstellt', 'description': 'Ihr individuelles Angebot wurde erstellt'},
                    {'date': '2024-01-17', 'title': 'Dokumente hochgeladen', 'description': 'Alle relevanten Unterlagen wurden bereitgestellt'}
                ]
            },
            'consulting_project': {
                'product_name': 'Beratungsprojekt',
                'product_description': 'Professionelle Beratung für Ihr Unternehmen mit maßgeschneiderten Lösungen.',
                'product_features': [
                    {'text': 'Individuelle Beratung', 'icon': '🎯'},
                    {'text': 'Erfahrene Berater', 'icon': '👨‍💼'},
                    {'text': 'Nachhaltige Lösungen', 'icon': '🌱'},
                    {'text': 'Follow-up Support', 'icon': '📞'}
                ],
                'product_price': 5000.00,
                'product_currency': 'EUR',
                'deal_status': 'initial',
                'deal_progress': 25,
                'welcome_message': 'Willkommen zu Ihrem Beratungsprojekt!',
                'customer_tasks': [
                    {'title': 'Projektanforderungen definieren', 'description': 'Definieren Sie Ihre spezifischen Anforderungen', 'completed': False, 'due_date': '2024-01-30'},
                    {'title': 'Kick-off Meeting', 'description': 'Planen Sie das erste Projektmeeting', 'completed': False, 'due_date': '2024-02-05'}
                ],
                'contact_person_name': 'Dr. Berater',
                'contact_person_email': 'berater@example.com',
                'contact_person_phone': '+49 123 456789',
                'faq_items': [
                    {'question': 'Wie läuft die Beratung ab?', 'answer': 'Wir beginnen mit einer Analyse und entwickeln dann maßgeschneiderte Lösungen.'},
                    {'question': 'Wie lange dauert das Projekt?', 'answer': 'Die Dauer hängt von der Komplexität ab, typischerweise 3-6 Monate.'}
                ],
                'timeline_events': [
                    {'date': '2024-01-15', 'title': 'Projekt initiiert', 'description': 'Ihr Beratungsprojekt wurde gestartet'},
                    {'date': '2024-01-20', 'title': 'Anforderungsanalyse', 'description': 'Analyse Ihrer spezifischen Bedürfnisse'}
                ]
            },
            'marketing_campaign': {
                'product_name': 'Marketing Kampagne',
                'product_description': 'Professionelle Marketing-Kampagne für Ihr Unternehmen mit modernen Strategien.',
                'product_features': [
                    {'text': 'Social Media Marketing', 'icon': '📱'},
                    {'text': 'Content Creation', 'icon': '✍️'},
                    {'text': 'Analytics & Reporting', 'icon': '📊'},
                    {'text': 'A/B Testing', 'icon': '🧪'}
                ],
                'product_price': 1500.00,
                'product_currency': 'EUR',
                'deal_status': 'contract_prepared',
                'deal_progress': 80,
                'welcome_message': 'Willkommen zu Ihrer Marketing-Kampagne!',
                'customer_tasks': [
                    {'title': 'Kampagnen-Briefing', 'description': 'Geben Sie uns Ihr Briefing für die Kampagne', 'completed': True, 'due_date': '2024-01-10'},
                    {'title': 'Finale Freigabe', 'description': 'Geben Sie die finale Freigabe für die Kampagne', 'completed': False, 'due_date': '2024-01-28'}
                ],
                'contact_person_name': 'Marketing Manager',
                'contact_person_email': 'marketing@example.com',
                'contact_person_phone': '+49 123 456789',
                'faq_items': [
                    {'question': 'Wann startet die Kampagne?', 'answer': 'Die Kampagne startet nach Ihrer finalen Freigabe.'},
                    {'question': 'Wie wird der Erfolg gemessen?', 'answer': 'Wir verwenden umfassende Analytics-Tools zur Erfolgsmessung.'}
                ],
                'timeline_events': [
                    {'date': '2024-01-15', 'title': 'Kampagne geplant', 'description': 'Ihre Marketing-Kampagne wurde geplant'},
                    {'date': '2024-01-20', 'title': 'Content erstellt', 'description': 'Alle Inhalte wurden erstellt'},
                    {'date': '2024-01-25', 'title': 'Bereit für Launch', 'description': 'Kampagne ist bereit für den Launch'}
                ]
            }
        }
        
        if template_name not in templates:
            available_templates = list(templates.keys())
            raise ValueError(f"Template '{template_name}' nicht gefunden. Verfügbare Templates: {available_templates}")
        
        # Erstelle unique slug falls nicht vorhanden
        if 'slug' not in kwargs:
            from django.utils.text import slugify
            base_slug = slugify(kwargs.get('title', 'template'))
            slug = base_slug
            counter = 1
            while cls.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            kwargs['slug'] = slug
        
        # Template-Daten mit kwargs überschreiben
        template_data = templates[template_name].copy()
        template_data.update(kwargs)
        
        return cls.objects.create(**template_data)
    
    @classmethod
    def get_available_templates(cls):
        """Gibt verfügbare Templates zurück"""
        return [
            {'name': 'modern', 'display_name': 'Modern', 'description': 'Moderne, responsive Landingpage mit Hero-Sektion und Gradienten'},
            {'name': 'classic', 'display_name': 'Klassisch', 'description': 'Traditionelles Design mit klarer Struktur und serifen Schrift'},
            {'name': 'minimal', 'display_name': 'Minimalistisch', 'description': 'Sauberes, minimalistisches Design mit viel Weißraum'},
            {'name': 'corporate', 'display_name': 'Corporate', 'description': 'Professionelles Corporate-Design mit Business-Fokus'},
            {'name': 'creative', 'display_name': 'Kreativ', 'description': 'Kreatives, auffälliges Design mit Animationen'},
            {'name': 'elegant', 'display_name': 'Elegant', 'description': 'Elegantes Design mit feinen Details und Premium-Look'},
            {'name': 'bold', 'display_name': 'Bold', 'description': 'Mutiges Design mit starken Kontrasten und großen Elementen'},
            {'name': 'tech', 'display_name': 'Tech', 'description': 'Technisches Design mit futuristischen Elementen'},
            {'name': 'luxury', 'display_name': 'Luxury', 'description': 'Luxuriöses Design mit Gold-Akzenten und Premium-Materialien'},
            {'name': 'clean', 'display_name': 'Clean', 'description': 'Sauberes, modernes Design mit klaren Linien'}
        ]
    
    # Passwortschutz-Methoden
    def set_password_protection(self, password: str, message: str = None):
        """Aktiviert Passwortschutz für die Landingpage"""
        from django.contrib.auth.hashers import make_password
        
        self.password_protection_enabled = True
        self.password_protection_password = make_password(password)
        
        if message:
            self.password_protection_message = message
        else:
            self.password_protection_message = _('Diese Landingpage ist passwortgeschützt. Bitte geben Sie das Passwort ein.')
        
        self.save()
    
    def disable_password_protection(self):
        """Deaktiviert Passwortschutz für die Landingpage"""
        self.password_protection_enabled = False
        self.password_protection_password = None
        self.password_protection_attempts = 0
        self.password_protection_last_attempt = None
        self.password_protection_blocked_until = None
        self.save()
    
    def check_password(self, password: str) -> bool:
        """Überprüft das Passwort für die Landingpage"""
        from django.contrib.auth.hashers import check_password
        from django.utils import timezone
        
        # Prüfe ob gesperrt
        if self.is_blocked():
            return False
        
        # Prüfe Passwort
        if check_password(password, self.password_protection_password):
            # Erfolgreich - Reset Versuche
            self.password_protection_attempts = 0
            self.password_protection_last_attempt = timezone.now()
            self.save()
            return True
        else:
            # Fehlgeschlagen - Erhöhe Versuche
            self.password_protection_attempts += 1
            self.password_protection_last_attempt = timezone.now()
            
            # Prüfe ob gesperrt werden soll
            if self.password_protection_attempts >= self.password_protection_max_attempts:
                from datetime import timedelta
                self.password_protection_blocked_until = timezone.now() + timedelta(minutes=self.password_protection_block_duration)
            
            self.save()
            return False
    
    def is_blocked(self) -> bool:
        """Prüft ob der Zugriff gesperrt ist"""
        from django.utils import timezone
        
        if not self.password_protection_blocked_until:
            return False
        
        return timezone.now() < self.password_protection_blocked_until
    
    def get_remaining_attempts(self) -> int:
        """Gibt die verbleibenden Versuche zurück"""
        return max(0, self.password_protection_max_attempts - self.password_protection_attempts)
    
    def get_block_remaining_time(self) -> int:
        """Gibt die verbleibende Sperrzeit in Minuten zurück"""
        from django.utils import timezone
        
        if not self.password_protection_blocked_until:
            return 0
        
        remaining = self.password_protection_blocked_until - timezone.now()
        return max(0, int(remaining.total_seconds() / 60))
    
    def log_password_attempt(self, success: bool, ip_address: str = None):
        """Protokolliert einen Passwortversuch"""
        if not self.password_protection_log_attempts:
            return
        
        # Hier könnte ein Log-Eintrag erstellt werden
        print(f"Passwortversuch für Deal '{self.title}': {'Erfolgreich' if success else 'Fehlgeschlagen'} - IP: {ip_address}")
    
    def generate_random_url_code(self):
        """Generiert einen zufälligen URL-Code"""
        import random
        import string
        chars = string.ascii_letters + string.digits
        code = ''.join(random.choice(chars) for _ in range(8))
        
        # Stelle sicher, dass der Code eindeutig ist
        while Deal.objects.filter(random_url_code=code).exists():
            code = ''.join(random.choice(chars) for _ in range(8))
        
        return code
    
    def get_public_url(self):
        """Gibt die öffentliche URL basierend auf URL-Typ zurück"""
        if self.url_type == 'random':
            if not self.random_url_code:
                self.random_url_code = self.generate_random_url_code()
                self.save(update_fields=['random_url_code'])
            return f"/deals/{self.random_url_code}/"
        else:
            return f"/deals/{self.slug}/"
    
    def get_content_blocks_by_type(self, content_type):
        """Gibt Content-Blöcke nach Typ zurück"""
        from .models import ContentBlock
        return ContentBlock.objects.filter(
            content_type=content_type,
            is_active=True
        ).order_by('category', 'title')
    
    def get_media_by_type(self, media_type):
        """Gibt Medien nach Typ zurück"""
        from .models import MediaLibrary
        return MediaLibrary.objects.filter(
            media_type=media_type,
            is_active=True
        ).order_by('category', 'title')
    
    def get_layout_templates(self):
        """Gibt verfügbare Layout-Vorlagen zurück"""
        from .models import LayoutTemplate
        return LayoutTemplate.objects.filter(
            is_active=True
        ).order_by('category', 'title')
    
    def duplicate(self, new_title=None, new_slug=None, include_files=True, include_content=True):
        """
        Dupliziert einen Dealroom mit allen Einstellungen
        
        Args:
            new_title: Neuer Titel für den duplizierten Deal
            new_slug: Neuer Slug für den duplizierten Deal
            include_files: Ob Dateien mit dupliziert werden sollen
            include_content: Ob Content mit dupliziert werden soll
        """
        from django.utils.text import slugify
        from django.utils import timezone
        
        # Standard-Titel und Slug generieren
        if not new_title:
            new_title = f"{self.title} (Kopie)"
        if not new_slug:
            new_slug = slugify(new_title)
            # Eindeutigkeit sicherstellen
            counter = 1
            original_slug = new_slug
            while Deal.objects.filter(slug=new_slug).exists():
                new_slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Neuen Deal erstellen
        new_deal = Deal.objects.create(
            title=new_title,
            slug=new_slug,
            description=self.description,
            status='draft',  # Immer als Draft starten
            template_type=self.template_type,
            theme_type=self.theme_type,
            url_type=self.url_type,
            created_by=self.created_by,
            
            # Kunden-Informationen
            company_name=self.company_name,
            recipient_name=self.recipient_name,
            recipient_email=self.recipient_email,
            recipient_company=self.recipient_company,
            customer_name=self.customer_name,
            customer_email=self.customer_email,
            customer_info=self.customer_info,
            
            # Video-Informationen
            central_video_url=self.central_video_url,
            central_video_file=self.central_video_file,
            
            # Landingpage-spezifische Felder
            hero_title=self.hero_title,
            hero_subtitle=self.hero_subtitle,
            call_to_action=self.call_to_action,
            
            # Deal-Status & Fortschritt
            deal_status=self.deal_status,
            deal_progress=self.deal_progress,
            
            # Begrüßung & Personalisierung
            welcome_message=self.welcome_message if include_content else '',
            customer_logo_url=self.customer_logo_url,
            
            # Aufgaben & To-Dos
            customer_tasks=self.customer_tasks if include_content else [],
            
            # Kommunikation
            contact_person_name=self.contact_person_name,
            contact_person_email=self.contact_person_email,
            contact_person_phone=self.contact_person_phone,
            
            # FAQ & Hilfe
            faq_items=self.faq_items if include_content else [],
            
            # Timeline & Aktivitäten
            timeline_events=self.timeline_events if include_content else [],
            
            # Produktbeschreibung & Details
            product_name=self.product_name,
            product_description=self.product_description if include_content else '',
            product_features=self.product_features if include_content else [],
            product_price=self.product_price,
            product_currency=self.product_currency,
            
            # Erweiterte Dokumentenverwaltung
            document_categories=self.document_categories if include_content else [],
            document_access_levels=self.document_access_levels if include_content else [],
            
            # Design
            primary_color=self.primary_color,
            secondary_color=self.secondary_color,
            
            # SEO-Felder
            meta_title=self.meta_title,
            meta_description=self.meta_description,
            
            # HTML-Editor Felder
            custom_html_header=self.custom_html_header,
            custom_html_body_start=self.custom_html_body_start,
            custom_html_content=self.custom_html_content,
            custom_html_body_end=self.custom_html_body_end,
            custom_css=self.custom_css,
            custom_javascript=self.custom_javascript,
            html_editor_mode=self.html_editor_mode,
            
            # Passwortschutz (deaktiviert für Kopie)
            password_protection_enabled=False,
            password_protection_message=self.password_protection_message,
            password_protection_max_attempts=self.password_protection_max_attempts,
            password_protection_block_duration=self.password_protection_block_duration,
            password_protection_log_attempts=self.password_protection_log_attempts,
        )
        
        # Dateien duplizieren (optional)
        if include_files:
            # DealFiles duplizieren
            for file in self.files.all():
                DealFile.objects.create(
                    deal=new_deal,
                    title=file.title,
                    description=file.description,
                    file_source=file.file_source,
                    file=file.file,  # Referenz auf dieselbe Datei
                    global_file=file.global_file,
                    file_type=file.file_type,
                    uploaded_by=file.uploaded_by,
                    is_public=file.is_public,
                    is_primary=file.is_primary,
                    document_category=file.document_category,
                    document_version=file.document_version,
                    document_access_level=file.document_access_level,
                    document_expiry_date=file.document_expiry_date,
                    document_requires_signature=file.document_requires_signature,
                )
            
            # DealFileAssignments duplizieren
            for assignment in self.file_assignments.all():
                DealFileAssignment.objects.create(
                    deal=new_deal,
                    global_file=assignment.global_file,
                    assigned_by=assignment.assigned_by,
                    role=assignment.role,
                    order=assignment.order,
                )
        
        # Änderungsprotokoll erstellen
        DealChangeLog.objects.create(
            deal=new_deal,
            change_type='created',
            changed_by=self.created_by,
            description=f'Dealroom dupliziert von "{self.title}"',
        )
        
        return new_deal
    
    def get_duplicate_options(self):
        """Gibt Optionen für die Duplizierung zurück"""
        return {
            'include_files': True,
            'include_content': True,
            'reset_status': True,
            'reset_progress': True,
            'reset_password_protection': True,
        }

# Signal-Handler für automatische Website-Generierung
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
import threading
import time
from django.conf import settings

@receiver(post_save, sender=Deal)
def auto_generate_website(sender, instance, created, **kwargs):
    """
    Automatische Website-Generierung bei Dealroom-Änderungen
    
    Diese Funktion wird automatisch ausgelöst wenn:
    - Ein neuer Dealroom erstellt wird
    - Ein bestehender Dealroom geändert wird
    - Der Status auf 'active' gesetzt wird
    
    Die Generierung läuft asynchron um die Performance nicht zu beeinträchtigen.
    """
    
    print(f"🔍 Signal triggered for: {instance.title} (Status: {instance.status}, Created: {created})")
    
    # Nur für aktive Dealrooms
    if instance.status == 'active':
        try:
            from generator.renderer import DealroomGenerator
            import os
            
            # Direkte Generierung für bessere Zuverlässigkeit
            try:
                print(f"🔄 Starte automatische Website-Generierung für '{instance.title}'...")
                
                # Generator initialisieren
                generator = DealroomGenerator(instance)
                
                # Website-Verzeichnis erstellen
                output_dir = os.path.join(settings.BASE_DIR, 'generated_pages', f'dealroom-{instance.id}')
                output_path = os.path.join(output_dir, 'index.html')
                
                # Website speichern
                success = generator.save_website(output_path)
                
                if success:
                    # URL im Model speichern (ohne Signal auszulösen)
                    website_url = f"/generated_pages/dealroom-{instance.id}/index.html"
                    instance.local_website_url = website_url
                    instance.website_status = 'generated'
                    instance.last_generation = timezone.now()
                    instance.generation_error = None
                    # Signal temporär deaktivieren
                    from django.db.models.signals import post_save
                    post_save.disconnect(auto_generate_website, sender=Deal)
                    instance.save(update_fields=['local_website_url', 'website_status', 'last_generation', 'generation_error'])
                    # Signal wieder aktivieren
                    post_save.connect(auto_generate_website, sender=Deal)
                    
                    print(f"✅ Website für '{instance.title}' automatisch generiert: {website_url}")
                else:
                    instance.website_status = 'failed'
                    instance.generation_error = 'Fehler beim Speichern der Website'
                    # Signal temporär deaktivieren
                    from django.db.models.signals import post_save
                    post_save.disconnect(auto_generate_website, sender=Deal)
                    instance.save(update_fields=['website_status', 'generation_error'])
                    # Signal wieder aktivieren
                    post_save.connect(auto_generate_website, sender=Deal)
                    print(f"❌ Fehler beim Speichern der Website für '{instance.title}'")
                
            except Exception as e:
                print(f"❌ Fehler bei automatischer Website-Generierung für '{instance.title}': {e}")
                # Fehler im Model speichern (ohne Signal auszulösen)
                instance.website_status = 'failed'
                instance.generation_error = str(e)
                # Signal temporär deaktivieren
                from django.db.models.signals import post_save
                post_save.disconnect(auto_generate_website, sender=Deal)
                instance.save(update_fields=['website_status', 'generation_error'])
                # Signal wieder aktivieren
                post_save.connect(auto_generate_website, sender=Deal)
            
        except ImportError:
            print("⚠️ Generator-Modul nicht verfügbar - Website-Generierung übersprungen")
        except Exception as e:
            print(f"❌ Fehler beim Starten der automatischen Website-Generierung: {e}")

@receiver(post_delete, sender=Deal)
def delete_website_on_dealroom_delete(sender, instance, **kwargs):
    """
    Löscht Website wenn Dealroom gelöscht wird
    
    Diese Funktion wird automatisch ausgelöst wenn ein Dealroom
    aus der Datenbank gelöscht wird.
    """
    
    try:
        from generator.renderer import DealroomGenerator
        
        print(f"🗑️ Lösche Website für gelöschten Dealroom '{instance.title}'...")
        
        # Generator initialisieren und Website löschen
        generator = DealroomGenerator(instance)
        generator.delete_website()
        
        print(f"✅ Website für '{instance.title}' erfolgreich gelöscht")
        
    except ImportError:
        print("⚠️ Generator-Modul nicht verfügbar - Website-Löschung übersprungen")
    except Exception as e:
        print(f"❌ Fehler beim Löschen der Website für '{instance.title}': {e}")

# Signal für Datei-Uploads (wenn neue Dateien hinzugefügt werden)
@receiver(post_save, sender='deals.DealFile')
def regenerate_website_on_file_change(sender, instance, created, **kwargs):
    """
    Regeneriert Website wenn Dateien hinzugefügt oder geändert werden
    
    Diese Funktion wird automatisch ausgelöst wenn:
    - Neue Dateien zu einem Dealroom hinzugefügt werden
    - Bestehende Dateien geändert werden
    """
    
    try:
        # Nur für aktive Dealrooms
        if instance.deal.status == 'active':
            from generator.renderer import DealroomGenerator
            import os
            
            def delayed_regeneration():
                """Verzögerte Regenerierung um Race Conditions zu vermeiden"""
                time.sleep(3)  # 3 Sekunden warten
                try:
                    print(f"🔄 Regeneriere Website für '{instance.deal.title}' nach Datei-Änderung...")
                    
                    # Generator initialisieren
                    generator = DealroomGenerator(instance.deal)
                    
                    # Website-Verzeichnis erstellen
                    output_dir = os.path.join(settings.BASE_DIR, 'generated_pages', f'dealroom-{instance.deal.id}')
                    output_path = os.path.join(output_dir, 'index.html')
                    
                    # Website speichern
                    success = generator.save_website(output_path)
                    
                    if success:
                        # URL im Model speichern
                        website_url = f"/generated_pages/dealroom-{instance.deal.id}/"
                        instance.deal.local_website_url = website_url
                        instance.deal.website_status = 'generated'
                        instance.deal.last_generation = timezone.now()
                        instance.deal.generation_error = None
                        instance.deal.save(update_fields=['local_website_url', 'website_status', 'last_generation', 'generation_error'])
                        
                        print(f"✅ Website für '{instance.deal.title}' nach Datei-Änderung regeneriert: {website_url}")
                    else:
                        instance.deal.website_status = 'failed'
                        instance.deal.generation_error = 'Fehler beim Speichern der Website nach Datei-Änderung'
                        instance.deal.save(update_fields=['website_status', 'generation_error'])
                        print(f"❌ Fehler beim Speichern der Website für '{instance.deal.title}' nach Datei-Änderung")
                    
                except Exception as e:
                    print(f"❌ Fehler bei Website-Regenerierung für '{instance.deal.title}' nach Datei-Änderung: {e}")
                    instance.deal.website_status = 'failed'
                    instance.deal.generation_error = str(e)
                    instance.deal.save(update_fields=['website_status', 'generation_error'])
            
            # Thread für asynchrone Ausführung starten
            thread = threading.Thread(target=delayed_regeneration)
            thread.daemon = True
            thread.start()
            
    except ImportError:
        print("⚠️ Generator-Modul nicht verfügbar - Website-Regenerierung übersprungen")
    except Exception as e:
        print(f"❌ Fehler beim Starten der Website-Regenerierung nach Datei-Änderung: {e}")

@receiver(post_delete, sender='deals.DealFile')
def regenerate_website_on_file_delete(sender, instance, **kwargs):
    """
    Regeneriert Website wenn Dateien gelöscht werden
    
    Diese Funktion wird automatisch ausgelöst wenn:
    - Dateien von einem Dealroom gelöscht werden
    """
    
    try:
        # Nur für aktive Dealrooms
        if instance.deal.status == 'active':
            from generator.renderer import DealroomGenerator
            import os
            
            def delayed_regeneration():
                """Verzögerte Regenerierung um Race Conditions zu vermeiden"""
                time.sleep(3)  # 3 Sekunden warten
                try:
                    print(f"🔄 Regeneriere Website für '{instance.deal.title}' nach Datei-Löschung...")
                    
                    # Generator initialisieren
                    generator = DealroomGenerator(instance.deal)
                    
                    # Website-Verzeichnis erstellen
                    output_dir = os.path.join(settings.BASE_DIR, 'generated_pages', f'dealroom-{instance.deal.id}')
                    output_path = os.path.join(output_dir, 'index.html')
                    
                    # Website speichern
                    success = generator.save_website(output_path)
                    
                    if success:
                        # URL im Model speichern
                        website_url = f"/generated_pages/dealroom-{instance.deal.id}/"
                        instance.deal.local_website_url = website_url
                        instance.deal.website_status = 'generated'
                        instance.deal.last_generation = timezone.now()
                        instance.deal.generation_error = None
                        instance.deal.save(update_fields=['local_website_url', 'website_status', 'last_generation', 'generation_error'])
                        
                        print(f"✅ Website für '{instance.deal.title}' nach Datei-Löschung regeneriert: {website_url}")
                    else:
                        instance.deal.website_status = 'failed'
                        instance.deal.generation_error = 'Fehler beim Speichern der Website nach Datei-Löschung'
                        instance.deal.save(update_fields=['website_status', 'generation_error'])
                        print(f"❌ Fehler beim Speichern der Website für '{instance.deal.title}' nach Datei-Löschung")
                    
                except Exception as e:
                    print(f"❌ Fehler bei Website-Regenerierung für '{instance.deal.title}' nach Datei-Löschung: {e}")
                    instance.deal.website_status = 'failed'
                    instance.deal.generation_error = str(e)
                    instance.deal.save(update_fields=['website_status', 'generation_error'])
            
            # Thread für asynchrone Ausführung starten
            thread = threading.Thread(target=delayed_regeneration)
            thread.daemon = True
            thread.start()
            
    except ImportError:
        print("⚠️ Generator-Modul nicht verfügbar - Website-Regenerierung übersprungen")
    except Exception as e:
        print(f"❌ Fehler beim Starten der Website-Regenerierung nach Datei-Löschung: {e}")


class DealFile(models.Model):
    """
    Datei-Modell für Deal-bezogene Dateien
    """
    
    class FileType(models.TextChoices):
        HERO_IMAGE = 'hero_image', _('Hero-Bild')
        LOGO = 'logo', _('Logo')
        GALLERY = 'gallery', _('Galerie')
        DOCUMENT = 'document', _('Dokument')
        CONTRACT = 'contract', _('Vertrag')
        OFFER = 'offer', _('Angebot')
        INVOICE = 'invoice', _('Rechnung')
        PRESENTATION = 'presentation', _('Präsentation')
        SPECIFICATION = 'specification', _('Spezifikation')
        VIDEO = 'video', _('Video')
        OTHER = 'other', _('Sonstiges')
    
    class FileSource(models.TextChoices):
        UPLOADED = 'uploaded', _('Direkt hochgeladen')
        GLOBAL_ASSIGNED = 'global_assigned', _('Globale Datei zugeordnet')
    
    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_('Deal')
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Titel')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Beschreibung')
    )
    
    # Datei-Quelle
    file_source = models.CharField(
        max_length=20,
        choices=FileSource.choices,
        default=FileSource.UPLOADED,
        verbose_name=_('Datei-Quelle')
    )
    
    # Direkt hochgeladene Datei
    file = models.FileField(
        upload_to='deal_files/',
        blank=True,
        null=True,
        verbose_name=_('Datei')
    )
    
    # Referenz auf globale Datei (falls zugeordnet)
    global_file = models.ForeignKey(
        'files.GlobalFile',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='deal_file_references',
        verbose_name=_('Globale Datei')
    )
    
    file_type = models.CharField(
        max_length=20,
        choices=FileType.choices,
        default=FileType.OTHER,
        verbose_name=_('Dateityp')
    )
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Hochgeladen von')
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Hochgeladen am')
    )
    
    is_public = models.BooleanField(
        default=True,
        verbose_name=_('Öffentlich')
    )
    
    # Für Hero-Bilder und Logos
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_('Primär (für Hero/Logo)')
    )
    
    # Erweiterte Dokumentenverwaltung
    document_category = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Dokumentenkategorie')
    )
    
    document_version = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Dokumentversion')
    )
    
    document_access_level = models.CharField(
        max_length=20,
        choices=[
            ('public', _('Öffentlich')),
            ('customer', _('Nur Kunde')),
            ('internal', _('Intern')),
            ('confidential', _('Vertraulich')),
        ],
        default='public',
        verbose_name=_('Zugriffsebene')
    )
    
    document_expiry_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Ablaufdatum')
    )
    
    document_requires_signature = models.BooleanField(
        default=False,
        verbose_name=_('Unterschrift erforderlich')
    )
    
    class Meta:
        verbose_name = _('Deal-Datei')
        verbose_name_plural = _('Deal-Dateien')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.deal.title}"
    
    def get_file_size(self):
        """Gibt die Dateigröße zurück"""
        if self.file_source == self.FileSource.UPLOADED and self.file:
            try:
                size = self.file.size
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024.0:
                        return f"{size:.1f} {unit}"
                    size /= 1024.0
                return f"{size:.1f} TB"
            except:
                return "Unbekannt"
        elif self.file_source == self.FileSource.GLOBAL_ASSIGNED and self.global_file:
            return self.global_file.get_file_size()
        return "Unbekannt"
    
    def get_file_extension(self):
        """Gibt die Dateiendung zurück"""
        if self.file_source == self.FileSource.UPLOADED and self.file:
            return os.path.splitext(self.file.name)[1].lower()
        elif self.file_source == self.FileSource.GLOBAL_ASSIGNED and self.global_file:
            return self.global_file.get_file_extension()
        return ""
    
    def is_image(self):
        """Prüft ob es sich um ein Bild handelt"""
        if self.file_source == self.FileSource.UPLOADED and self.file:
            ext = self.get_file_extension().lower()
            return ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        elif self.file_source == self.FileSource.GLOBAL_ASSIGNED and self.global_file:
            return self.global_file.is_image()
        return False
    
    def is_document(self):
        """Prüft ob es sich um ein Dokument handelt"""
        if self.file_source == self.FileSource.UPLOADED and self.file:
            ext = self.get_file_extension().lower()
            return ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']
        elif self.file_source == self.FileSource.GLOBAL_ASSIGNED and self.global_file:
            return self.global_file.is_document()
        return False
    
    def get_actual_file(self):
        """Gibt die tatsächliche Datei zurück (entweder direkt oder über globale Referenz)"""
        if self.file_source == self.FileSource.UPLOADED:
            return self.file
        elif self.file_source == self.FileSource.GLOBAL_ASSIGNED and self.global_file:
            return self.global_file.file
        return None
    
    def get_file_url(self):
        """Gibt die Download-URL zurück"""
        if self.file_source == self.FileSource.UPLOADED:
            return self.file.url if self.file else None
        elif self.file_source == self.FileSource.GLOBAL_ASSIGNED and self.global_file:
            return self.global_file.file.url if self.global_file.file else None
        return None
    
    def get_file_size_display(self):
        """Gibt die Dateigröße in einem benutzerfreundlichen Format zurück"""
        return self.get_file_size()


class DealFileAssignment(models.Model):
    """
    Zuordnung von globalen Dateien zu Dealrooms
    """
    deal = models.ForeignKey(
        'Deal',
        on_delete=models.CASCADE,
        related_name='file_assignments',
        verbose_name=_('Dealroom')
    )
    
    global_file = models.ForeignKey(
        'files.GlobalFile',
        on_delete=models.CASCADE,
        related_name='deal_assignments',
        verbose_name=_('Globale Datei')
    )
    
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Zugeordnet von')
    )
    
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Zugeordnet am')
    )
    
    # Spezielle Rolle für diese Datei im Dealroom
    role = models.CharField(
        max_length=50,
        choices=[
            ('hero_image', _('Hero-Bild')),
            ('logo', _('Logo')),
            ('gallery', _('Galerie')),
            ('document', _('Dokument')),
            ('video', _('Video')),
            ('data', _('Daten')),
            ('other', _('Sonstiges')),
        ],
        default='other',
        verbose_name=_('Rolle')
    )
    
    # Reihenfolge für Sortierung
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Reihenfolge')
    )
    
    class Meta:
        verbose_name = _('Dealroom-Datei-Zuordnung')
        verbose_name_plural = _('Dealroom-Datei-Zuordnungen')
        ordering = ['order', 'assigned_at']
        unique_together = ['deal', 'global_file']
    
    def __str__(self):
        return f"{self.deal.title} - {self.global_file.title} ({self.get_role_display()})"


class DealChangeLog(models.Model):
    """
    Änderungsprotokoll für Dealrooms
    """
    class ChangeType(models.TextChoices):
        CREATED = 'created', _('Erstellt')
        UPDATED = 'updated', _('Aktualisiert')
        DELETED = 'deleted', _('Gelöscht')
        FILE_ASSIGNED = 'file_assigned', _('Datei zugeordnet')
        FILE_UNASSIGNED = 'file_unassigned', _('Datei entfernt')
        STATUS_CHANGED = 'status_changed', _('Status geändert')
        WEBSITE_GENERATED = 'website_generated', _('Website generiert')
        WEBSITE_DELETED = 'website_deleted', _('Website gelöscht')
    
    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='change_logs',
        verbose_name=_('Dealroom')
    )
    
    change_type = models.CharField(
        max_length=50,
        choices=ChangeType.choices,
        verbose_name=_('Änderungstyp')
    )
    
    changed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Geändert von')
    )
    
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Geändert am')
    )
    
    field_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Feldname')
    )
    
    old_value = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Alter Wert')
    )
    
    new_value = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Neuer Wert')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Beschreibung')
    )
    
    class Meta:
        verbose_name = _('Dealroom-Änderung')
        verbose_name_plural = _('Dealroom-Änderungen')
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.deal.title} - {self.get_change_type_display()} ({self.changed_at})"
    
    def get_change_description(self):
        return self.description or f"{self.get_change_type_display()} von {self.changed_by}"


# Content-Bibliothek Modelle
class ContentBlock(models.Model):
    """
    Wiederverwendbare Textblöcke für Landingpages
    """
    class ContentType(models.TextChoices):
        WELCOME = 'welcome', _('Begrüßung')
        PRODUCT_DESCRIPTION = 'product_description', _('Produktbeschreibung')
        FAQ_ITEM = 'faq_item', _('FAQ-Eintrag')
        CTA_TEXT = 'cta_text', _('Call-to-Action')
        FOOTER_INFO = 'footer_info', _('Footer-Information')
        CONTACT_INFO = 'contact_info', _('Kontaktinformation')
        DEAL_STATUS = 'deal_status', _('Deal-Status')
        TASK_DESCRIPTION = 'task_description', _('Aufgabenbeschreibung')
        TIMELINE_EVENT = 'timeline_event', _('Timeline-Ereignis')
        CUSTOM = 'custom', _('Benutzerdefiniert')
    
    class Category(models.TextChoices):
        GENERAL = 'general', _('Allgemein')
        SOFTWARE = 'software', _('Software')
        CONSULTING = 'consulting', _('Beratung')
        MARKETING = 'marketing', _('Marketing')
        SALES = 'sales', _('Vertrieb')
        SUPPORT = 'support', _('Support')
        CUSTOM = 'custom', _('Benutzerdefiniert')
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Titel')
    )
    
    content_type = models.CharField(
        max_length=50,
        choices=ContentType.choices,
        verbose_name=_('Content-Typ')
    )
    
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.GENERAL,
        verbose_name=_('Kategorie')
    )
    
    content = models.TextField(
        verbose_name=_('Inhalt')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Beschreibung'),
        help_text=_('Kurze Beschreibung für die Auswahl')
    )
    
    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Tags'),
        help_text=_('Tags für bessere Kategorisierung')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Aktiv')
    )
    
    usage_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Verwendungsanzahl')
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Erstellt von')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Erstellt am')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Aktualisiert am')
    )
    
    class Meta:
        verbose_name = _('Content-Block')
        verbose_name_plural = _('Content-Blöcke')
        ordering = ['category', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"
    
    def increment_usage(self):
        """Erhöht die Verwendungsanzahl"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class MediaLibrary(models.Model):
    """
    Zentrale Medienbibliothek für Landingpages
    """
    class MediaType(models.TextChoices):
        IMAGE = 'image', _('Bild')
        VIDEO = 'video', _('Video')
        DOCUMENT = 'document', _('Dokument')
        LOGO = 'logo', _('Logo')
        ICON = 'icon', _('Icon')
        OTHER = 'other', _('Sonstiges')
    
    class Category(models.TextChoices):
        GENERAL = 'general', _('Allgemein')
        CORPORATE = 'corporate', _('Corporate')
        PRODUCT = 'product', _('Produkt')
        TEAM = 'team', _('Team')
        BACKGROUND = 'background', _('Hintergrund')
        CUSTOM = 'custom', _('Benutzerdefiniert')
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Titel')
    )
    
    media_type = models.CharField(
        max_length=20,
        choices=MediaType.choices,
        verbose_name=_('Medien-Typ')
    )
    
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.GENERAL,
        verbose_name=_('Kategorie')
    )
    
    file = models.FileField(
        upload_to='media_library/',
        verbose_name=_('Datei')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Beschreibung')
    )
    
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Alt-Text'),
        help_text=_('Für Barrierefreiheit')
    )
    
    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Tags')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Aktiv')
    )
    
    usage_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Verwendungsanzahl')
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Erstellt von')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Erstellt am')
    )
    
    class Meta:
        verbose_name = _('Medien-Bibliothek')
        verbose_name_plural = _('Medien-Bibliothek')
        ordering = ['category', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.get_media_type_display()})"
    
    def get_file_url(self):
        """Gibt die URL der Datei zurück"""
        return self.file.url if self.file else None
    
    def increment_usage(self):
        """Erhöht die Verwendungsanzahl"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class LayoutTemplate(models.Model):
    """
    Layout-Vorlagen für Landingpages
    """
    class LayoutType(models.TextChoices):
        SINGLE_COLUMN = 'single_column', _('Einspaltig')
        TWO_COLUMN = 'two_column', _('Zweispaltig')
        THREE_COLUMN = 'three_column', _('Dreispaltig')
        GRID = 'grid', _('Grid-Layout')
        HERO_FOCUS = 'hero_focus', _('Hero-Fokus')
        CONTENT_FOCUS = 'content_focus', _('Content-Fokus')
        CUSTOM = 'custom', _('Benutzerdefiniert')
    
    class Category(models.TextChoices):
        GENERAL = 'general', _('Allgemein')
        CORPORATE = 'corporate', _('Corporate')
        CREATIVE = 'creative', _('Kreativ')
        MINIMAL = 'minimal', _('Minimalistisch')
        MODERN = 'modern', _('Modern')
        CUSTOM = 'custom', _('Benutzerdefiniert')
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Titel')
    )
    
    layout_type = models.CharField(
        max_length=50,
        choices=LayoutType.choices,
        verbose_name=_('Layout-Typ')
    )
    
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.GENERAL,
        verbose_name=_('Kategorie')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Beschreibung')
    )
    
    css_classes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('CSS-Klassen'),
        help_text=_('CSS-Klassen für das Layout')
    )
    
    html_structure = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('HTML-Struktur'),
        help_text=_('HTML-Grundstruktur für das Layout')
    )
    
    preview_image = models.ImageField(
        upload_to='layout_previews/',
        blank=True,
        null=True,
        verbose_name=_('Vorschau-Bild')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Aktiv')
    )
    
    usage_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Verwendungsanzahl')
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Erstellt von')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Erstellt am')
    )
    
    class Meta:
        verbose_name = _('Layout-Vorlage')
        verbose_name_plural = _('Layout-Vorlagen')
        ordering = ['category', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.get_layout_type_display()})"
    
    def increment_usage(self):
        """Erhöht die Verwendungsanzahl"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])





class CMSElement(models.Model):
    """
    CMS-Elemente für die Element-Bibliothek
    """
    class ElementType(models.TextChoices):
        # Layout Elements
        CONTAINER = 'container', _('Container')
        ROW = 'row', _('Zeile')
        COLUMN = 'column', _('Spalte')
        SECTION = 'section', _('Sektion')
        
        # Text Elements
        HEADING = 'heading', _('Überschrift')
        PARAGRAPH = 'paragraph', _('Absatz')
        LIST = 'list', _('Liste')
        QUOTE = 'quote', _('Zitat')
        
        # Media Elements
        IMAGE = 'image', _('Bild')
        VIDEO = 'video', _('Video')
        ICON = 'icon', _('Icon')
        GALLERY = 'gallery', _('Galerie')
        
        # Interactive Elements
        BUTTON = 'button', _('Button')
        LINK = 'link', _('Link')
        FORM = 'form', _('Formular')
        MAP = 'map', _('Karte')
        
        # Business Elements
        CARD = 'card', _('Karte')
        TABLE = 'table', _('Tabelle')
        TIMELINE = 'timeline', _('Zeitlinie')
        STATS = 'stats', _('Statistiken')
        
        # Social Elements
        SOCIAL_SHARE = 'social_share', _('Social Share')
        COMMENTS = 'comments', _('Kommentare')
        RATING = 'rating', _('Bewertung')
        FOLLOW = 'follow', _('Follow')
        
        # Advanced Elements
        ACCORDION = 'accordion', _('Akkordeon')
        TABS = 'tabs', _('Tabs')
        MODAL = 'modal', _('Modal')
        SLIDER = 'slider', _('Slider')
        
        # Data Elements
        FILE_DOWNLOAD = 'file_download', _('Datei-Download')
        DOCUMENT_VIEWER = 'document_viewer', _('Dokument-Viewer')
        DATA_TABLE = 'data_table', _('Daten-Tabelle')
        PROGRESS_TRACKER = 'progress_tracker', _('Fortschritt-Tracker')
    
    class Category(models.TextChoices):
        LAYOUT = 'layout', _('Layout')
        TEXT = 'text', _('Text')
        MEDIA = 'media', _('Medien')
        INTERACTIVE = 'interactive', _('Interaktiv')
        BUSINESS = 'business', _('Business')
        SOCIAL = 'social', _('Social')
        ADVANCED = 'advanced', _('Erweitert')
        DATA = 'data', _('Daten & Dateien')
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Titel')
    )
    
    element_type = models.CharField(
        max_length=50,
        choices=ElementType.choices,
        verbose_name=_('Element-Typ')
    )
    
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        verbose_name=_('Kategorie')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Beschreibung')
    )
    
    html_template = models.TextField(
        verbose_name=_('HTML-Template'),
        help_text=_('HTML-Code für das Element')
    )
    
    css_styles = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('CSS-Styles'),
        help_text=_('Zusätzliche CSS-Styles')
    )
    
    javascript_code = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('JavaScript-Code'),
        help_text=_('JavaScript für Interaktivität')
    )
    
    # Daten-Integration
    data_source = models.CharField(
        max_length=50,
        choices=[
            ('static', _('Statisch')),
            ('deal_data', _('Deal-Daten')),
            ('file_library', _('Datei-Bibliothek')),
            ('content_blocks', _('Content-Blöcke')),
            ('media_library', _('Medien-Bibliothek')),
            ('custom', _('Benutzerdefiniert')),
        ],
        default='static',
        verbose_name=_('Datenquelle')
    )
    
    data_mapping = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Daten-Mapping'),
        help_text=_('Mapping für dynamische Daten')
    )
    
    # Datei-Integration
    file_types = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Unterstützte Dateitypen'),
        help_text=_('Liste der unterstützten Dateitypen')
    )
    
    file_upload_enabled = models.BooleanField(
        default=False,
        verbose_name=_('Datei-Upload aktiviert')
    )
    
    file_display_mode = models.CharField(
        max_length=20,
        choices=[
            ('inline', _('Inline')),
            ('download', _('Download')),
            ('preview', _('Vorschau')),
            ('gallery', _('Galerie')),
        ],
        default='inline',
        verbose_name=_('Datei-Anzeigemodus')
    )
    
    # Konfiguration
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Aktiv')
    )
    
    usage_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Verwendungsanzahl')
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Erstellt von')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Erstellt am')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Aktualisiert am')
    )
    
    class Meta:
        verbose_name = _('CMS-Element')
        verbose_name_plural = _('CMS-Elemente')
        ordering = ['category', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.get_element_type_display()})"
    
    def increment_usage(self):
        """Erhöht die Verwendungsanzahl"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
    
    def get_rendered_html(self, deal=None, context=None):
        """Rendert das HTML-Template mit Deal-Daten"""
        html = self.html_template
        
        if deal and self.data_source == 'deal_data':
            # Deal-spezifische Daten einsetzen
            html = html.replace('{{ deal.title }}', deal.title or '')
            html = html.replace('{{ deal.description }}', deal.description or '')
            html = html.replace('{{ deal.company_name }}', deal.company_name or '')
            html = html.replace('{{ deal.recipient_name }}', deal.recipient_name or '')
            html = html.replace('{{ deal.product_name }}', deal.product_name or '')
            html = html.replace('{{ deal.product_description }}', deal.product_description or '')
            html = html.replace('{{ deal.call_to_action }}', deal.call_to_action or '')
        
        if context:
            for key, value in context.items():
                html = html.replace(f'{{{{ {key} }}}}', str(value))
        
        return html
    
    def get_files_for_deal(self, deal):
        """Holt Dateien für das Element basierend auf Deal"""
        if self.data_source == 'file_library':
            return deal.get_assigned_files()
        elif self.data_source == 'media_library':
            return MediaLibrary.objects.filter(is_active=True)
        return []


# Erweitere das bestehende DealAnalyticsEvent Model
class DealAnalyticsEvent(models.Model):
    """
    DSGVO-konformes Analytics-Event für Deal-Aktivitäten
    """
    EVENT_TYPE_CHOICES = [
        ('created', 'Deal erstellt'),
        ('deleted', 'Deal gelöscht'),
        ('updated', 'Deal bearbeitet'),
        ('page_view', 'Seitenaufruf'),
        ('click', 'Klick'),
        ('scroll', 'Scroll'),
        ('download', 'Download'),
        ('form_submit', 'Formular-Submit'),
        ('time_spent', 'Zeit verbracht'),
        ('bounce', 'Bounce'),
    ]
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    deal = models.ForeignKey('Deal', on_delete=models.CASCADE, related_name='analytics_events')
    user = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(blank=True, null=True)
    
    # DSGVO-konforme Daten
    visitor_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_('Besucher IP'),
        help_text=_('Wird anonymisiert gespeichert')
    )
    
    page_views = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Seitenaufrufe')
    )
    
    time_spent = models.DurationField(
        null=True,
        blank=True,
        verbose_name=_('Verbrachte Zeit')
    )
    
    referrer = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Referrer')
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name=_('User Agent')
    )
    
    # Event-spezifische Daten
    element_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Element ID')
    )
    
    position_x = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('X-Position')
    )
    
    position_y = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('Y-Position')
    )
    
    # DSGVO-Compliance
    consent_given = models.BooleanField(
        default=False,
        verbose_name=_('Einverständnis erteilt')
    )
    
    anonymized = models.BooleanField(
        default=True,
        verbose_name=_('Anonymisiert')
    )
    
    # Session-Tracking
    session_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Session ID')
    )

    class Meta:
        verbose_name = 'Deal-Analytics-Event'
        verbose_name_plural = 'Deal-Analytics-Events'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['deal', 'event_type', 'timestamp']),
            models.Index(fields=['visitor_ip', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} ({self.deal.title}) am {self.timestamp:%d.%m.%Y %H:%M}"
    
    def anonymize_ip(self):
        """Anonymisiert IP-Adresse für DSGVO-Compliance"""
        if self.visitor_ip:
            ip_parts = str(self.visitor_ip).split('.')
            if len(ip_parts) == 4:
                return f"{ip_parts[0]}.{ip_parts[1]}.*.*"
        return self.visitor_ip
    
    def save(self, *args, **kwargs):
        """Speichert mit anonymisierter IP"""
        if self.anonymized and self.visitor_ip:
            self.visitor_ip = self.anonymize_ip()
        super().save(*args, **kwargs)
