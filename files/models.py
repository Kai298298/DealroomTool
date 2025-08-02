from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
import os

User = get_user_model()


class Folder(models.Model):
    """
    Ordner-Modell für die Dateiverwaltung
    """
    name = models.CharField(
        max_length=200,
        verbose_name=_('Name')
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Beschreibung')
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children',
        verbose_name=_('Übergeordneter Ordner')
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
    
    is_public = models.BooleanField(
        default=True,
        verbose_name=_('Öffentlich')
    )
    
    class Meta:
        verbose_name = _('Ordner')
        verbose_name_plural = _('Ordner')
        ordering = ['name']
        unique_together = ['name', 'parent']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name
    
    def get_absolute_url(self):
        return reverse('files:folder_detail', kwargs={'pk': self.pk})
    
    def get_full_path(self):
        """Gibt den vollständigen Pfad des Ordners zurück"""
        path_parts = []
        current = self
        while current:
            path_parts.insert(0, current.name)
            current = current.parent
        return ' / '.join(path_parts)
    
    def get_breadcrumbs(self):
        """Gibt Breadcrumbs für den Ordner zurück"""
        breadcrumbs = []
        current = self
        while current:
            breadcrumbs.insert(0, {
                'name': current.name,
                'url': current.get_absolute_url(),
                'pk': current.pk
            })
            current = current.parent
        return breadcrumbs
    
    def get_file_count(self):
        """Gibt die Anzahl der Dateien im Ordner zurück"""
        return self.files.count()
    
    def get_subfolder_count(self):
        """Gibt die Anzahl der Unterordner zurück"""
        return self.children.count()
    
    def get_total_size(self):
        """Gibt die Gesamtgröße aller Dateien im Ordner zurück"""
        total_size = 0
        for file in self.files.all():
            if file.file:
                total_size += file.file.size
        return total_size


class GlobalFile(models.Model):
    """
    Globale Datei-Modell für die zentrale Dateiverwaltung
    """
    
    class FileType(models.TextChoices):
        HERO_IMAGE = 'hero_image', _('Hero-Bild')
        LOGO = 'logo', _('Logo')
        GALLERY = 'gallery', _('Galerie')
        DOCUMENT = 'document', _('Dokument')
        VIDEO = 'video', _('Video')
        OTHER = 'other', _('Sonstiges')
    
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
        upload_to='global_files/',
        verbose_name=_('Datei')
    )
    
    file_type = models.CharField(
        max_length=20,
        choices=FileType.choices,
        default=FileType.OTHER,
        verbose_name=_('Dateityp')
    )
    
    folder = models.ForeignKey(
        Folder,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='files',
        verbose_name=_('Ordner')
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
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Aktualisiert am')
    )
    
    is_public = models.BooleanField(
        default=True,
        verbose_name=_('Öffentlich')
    )
    
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_('Primär (für Hero/Logo)')
    )
    
    class Meta:
        verbose_name = _('Globale Datei')
        verbose_name_plural = _('Globale Dateien')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        if self.folder:
            return f"{self.title} ({self.folder.name})"
        return self.title
    
    def get_absolute_url(self):
        return reverse('files:global_file_detail', kwargs={'pk': self.pk})
    
    def get_file_size(self):
        """Gibt die Dateigröße zurück"""
        try:
            size = self.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Unbekannt"
    
    def get_file_size_display(self):
        """Gibt die Dateigröße in einem benutzerfreundlichen Format zurück"""
        return self.get_file_size()
    
    def get_file_extension(self):
        """Gibt die Dateiendung zurück"""
        return os.path.splitext(self.file.name)[1].lower()
    
    def is_image(self):
        """Prüft ob es sich um ein Bild handelt"""
        ext = self.get_file_extension().lower()
        return ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    
    def is_document(self):
        """Prüft ob es sich um ein Dokument handelt"""
        ext = self.get_file_extension().lower()
        return ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']
    
    def is_video(self):
        """Prüft ob es sich um ein Video handelt"""
        ext = self.get_file_extension().lower()
        return ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
    
    def get_icon_class(self):
        """Gibt die Bootstrap-Icon-Klasse zurück"""
        if self.is_image():
            return 'bi-image'
        elif self.is_document():
            return 'bi-file-text'
        elif self.is_video():
            return 'bi-camera-video'
        else:
            return 'bi-file-earmark'
    
    def get_download_url(self):
        """Gibt die Download-URL zurück"""
        return reverse('files:global_file_download', kwargs={'pk': self.pk})
