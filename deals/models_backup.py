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
    
    class ThemeType(models.TextChoices):
        LIGHT = 'light', _('Hell')
        DARK = 'dark', _('Dunkel')
        AUTO = 'auto', _('Automatisch (System)')
    
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
    
    class Meta:
        verbose_name = _('Deal')
        verbose_name_plural = _('Deals')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('dealrooms:dealroom_detail', kwargs={'pk': self.pk})
    
    def get_landingpage_url(self):
        """Gibt die öffentliche Landingpage-URL zurück"""
        if self.public_url:
            return self.public_url
        return f"/landingpage/{self.slug}/"
    
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
    
    def get_hero_images(self):
        """Gibt alle Hero-Bilder zurück"""
        return self.get_assigned_files(role='hero_image')
    
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
        """Gibt die Dateigröße in einem benutzerfreundlichen Format zurück"""
        return self.get_file_size()


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
        return f"{self.deal.title} - {self.get_change_type_display()} ({self.changed_at.strftime('%d.%m.%Y %H:%M')})"
    
    def get_change_description(self):
        """Gibt eine benutzerfreundliche Beschreibung der Änderung zurück"""
        return f"{self.get_change_type_display()} - {self.field_name or 'Allgemein'}"


# Template-Methoden für Deal-Klasse
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
    };
    
    if template_name not in templates:
        raise ValueError(f"Template '{template_name}' nicht gefunden. Verfügbare Templates: {list(templates.keys())}")
    
    # Template-Daten mit kwargs überschreiben
    template_data = templates[template_name].copy()
    template_data.update(kwargs)
    
    return cls.objects.create(**template_data)

def get_available_templates(cls):
    """Gibt verfügbare Templates zurück"""
    return {
        'software_offer': 'Software-Angebot',
        'consulting_project': 'Beratungsprojekt',
        'marketing_campaign': 'Marketing-Kampagne'
    }

# Template-Methoden zur Deal-Klasse hinzufügen
Deal.create_from_template = classmethod(create_from_template)
Deal.get_available_templates = classmethod(get_available_templates)
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
            raise ValueError(f"Template '{template_name}' nicht gefunden. Verfügbare Templates: {list(templates.keys())}")
        
        # Template-Daten mit kwargs überschreiben
        template_data = templates[template_name].copy()
        template_data.update(kwargs)
        
        return cls.objects.create(**template_data)
    
    @classmethod
    def get_available_templates(cls):
        """Gibt verfügbare Templates zurück"""
        return {
            'software_offer': 'Software-Angebot',
            'consulting_project': 'Beratungsprojekt',
            'marketing_campaign': 'Marketing-Kampagne'
        }
