"""
Benutzerdefiniertes Benutzermodell für das Dealroom-Dashboard
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Erweitertes Benutzermodell mit Rollen für das Dealroom-Dashboard
    """
    
    class UserRole(models.TextChoices):
        ADMIN = 'admin', _('Administrator')
        MANAGER = 'manager', _('Manager')
        EDITOR = 'editor', _('Editor')
        VIEWER = 'viewer', _('Viewer')
    
    # Erweiterte Felder
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.VIEWER,
        verbose_name=_('Rolle')
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Telefonnummer')
    )
    
    company = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Unternehmen')
    )
    
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Biografie')
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name=_('Profilbild')
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
        verbose_name = _('Benutzer')
        verbose_name_plural = _('Benutzer')
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        """Prüft ob der Benutzer Administrator ist"""
        return self.role == self.UserRole.ADMIN
    
    def is_manager(self):
        """Prüft ob der Benutzer Manager ist"""
        return self.role in [self.UserRole.ADMIN, self.UserRole.MANAGER]
    
    def is_editor(self):
        """Prüft ob der Benutzer Editor ist"""
        return self.role in [self.UserRole.ADMIN, self.UserRole.MANAGER, self.UserRole.EDITOR]
    
    def can_edit_deals(self):
        """Prüft ob der Benutzer Deals bearbeiten kann"""
        return self.is_editor()
    
    def can_manage_users(self):
        """Prüft ob der Benutzer andere Benutzer verwalten kann"""
        return self.is_manager()
