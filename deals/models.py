"""
Models für das Dealroom-Dashboard - Deals als Landingpages
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
import os

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
    
    # Grundlegende Informationen
    title = models.CharField(
        max_length=200,
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
        return reverse('deals:deal_detail', kwargs={'pk': self.pk})
    
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


# Signal-Handler für automatische Website-Generierung
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
import threading
import time

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
    
    # Nur für aktive Dealrooms
    if instance.status == 'active':
        try:
            from generator.renderer import DealroomGenerator
            
            # Asynchrone Ausführung um Performance zu optimieren
            def delayed_generation():
                """Verzögerte Generierung um Race Conditions zu vermeiden"""
                time.sleep(2)  # 2 Sekunden warten
                try:
                    print(f"🔄 Starte automatische Website-Generierung für '{instance.title}'...")
                    
                    # Generator initialisieren und Website erstellen
                    generator = DealroomGenerator(instance)
                    website_url = generator.generate_website()
                    
                    print(f"✅ Website für '{instance.title}' automatisch generiert: {website_url}")
                    
                except Exception as e:
                    print(f"❌ Fehler bei automatischer Website-Generierung für '{instance.title}': {e}")
                    # Fehler im Model speichern
                    instance.website_status = 'failed'
                    instance.generation_error = str(e)
                    instance.save(update_fields=['website_status', 'generation_error'])
            
            # Thread für asynchrone Ausführung starten
            thread = threading.Thread(target=delayed_generation)
            thread.daemon = True  # Thread wird beendet wenn Hauptprogramm endet
            thread.start()
            
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
            
            def delayed_regeneration():
                """Verzögerte Regenerierung um Race Conditions zu vermeiden"""
                time.sleep(3)  # 3 Sekunden warten
                try:
                    print(f"🔄 Regeneriere Website für '{instance.deal.title}' nach Datei-Änderung...")
                    
                    # Generator initialisieren und Website neu generieren
                    generator = DealroomGenerator(instance.deal)
                    website_url = generator.regenerate_website()
                    
                    print(f"✅ Website für '{instance.deal.title}' nach Datei-Änderung regeneriert: {website_url}")
                    
                except Exception as e:
                    print(f"❌ Fehler bei Website-Regenerierung nach Datei-Änderung: {e}")
            
            # Thread für asynchrone Ausführung starten
            thread = threading.Thread(target=delayed_regeneration)
            thread.daemon = True
            thread.start()
            
    except Exception as e:
        print(f"❌ Fehler beim Starten der Website-Regenerierung nach Datei-Änderung: {e}")

# Signal für Datei-Löschungen
@receiver(post_delete, sender='deals.DealFile')
def regenerate_website_on_file_delete(sender, instance, **kwargs):
    """
    Regeneriert Website wenn Dateien gelöscht werden
    """
    
    try:
        # Nur für aktive Dealrooms
        if instance.deal.status == 'active':
            from generator.renderer import DealroomGenerator
            
            def delayed_regeneration():
                """Verzögerte Regenerierung um Race Conditions zu vermeiden"""
                time.sleep(3)  # 3 Sekunden warten
                try:
                    print(f"🔄 Regeneriere Website für '{instance.deal.title}' nach Datei-Löschung...")
                    
                    # Generator initialisieren und Website neu generieren
                    generator = DealroomGenerator(instance.deal)
                    website_url = generator.regenerate_website()
                    
                    print(f"✅ Website für '{instance.deal.title}' nach Datei-Löschung regeneriert: {website_url}")
                    
                except Exception as e:
                    print(f"❌ Fehler bei Website-Regenerierung nach Datei-Löschung: {e}")
            
            # Thread für asynchrone Ausführung starten
            thread = threading.Thread(target=delayed_regeneration)
            thread.daemon = True
            thread.start()
            
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
        VIDEO = 'video', _('Video')
        OTHER = 'other', _('Sonstiges')
    
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
    
    file = models.FileField(
        upload_to='deal_files/',
        verbose_name=_('Datei')
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
    
    class Meta:
        verbose_name = _('Deal-Datei')
        verbose_name_plural = _('Deal-Dateien')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.deal.title}"
    
    def get_file_size(self):
        """Gibt die Dateigröße zurück"""
        if self.file:
            return self.file.size
        return 0
    
    def get_file_extension(self):
        """Gibt die Dateiendung zurück"""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ''
    
    def is_image(self):
        """Prüft ob es sich um ein Bild handelt"""
        return self.file_type in [self.FileType.HERO_IMAGE, self.FileType.LOGO, self.FileType.GALLERY]
    
    def is_document(self):
        """Prüft ob es sich um ein Dokument handelt"""
        return self.file_type == self.FileType.DOCUMENT
