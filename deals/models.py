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
        if self.description:
            return self.description
        
        if self.change_type == self.ChangeType.CREATED:
            return f"Dealroom '{self.deal.title}' wurde erstellt"
        elif self.change_type == self.ChangeType.UPDATED:
            if self.field_name:
                return f"Feld '{self.field_name}' wurde geändert"
            return "Dealroom wurde aktualisiert"
        elif self.change_type == self.ChangeType.STATUS_CHANGED:
            return f"Status geändert von '{self.old_value}' zu '{self.new_value}'"
        elif self.change_type == self.ChangeType.FILE_ASSIGNED:
            return f"Datei '{self.new_value}' wurde zugeordnet"
        elif self.change_type == self.ChangeType.FILE_UNASSIGNED:
            return f"Datei '{self.old_value}' wurde entfernt"
        elif self.change_type == self.ChangeType.WEBSITE_GENERATED:
            return "Website wurde generiert"
        elif self.change_type == self.ChangeType.WEBSITE_DELETED:
            return "Website wurde gelöscht"
        
        return self.get_change_type_display()
