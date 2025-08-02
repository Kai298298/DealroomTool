"""
Models für die Users-App
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class CustomUser(AbstractUser):
    """
    Erweiterte Benutzer-Model mit SaaS-Features
    """
    # SaaS-Plan Management
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='free',
        verbose_name=_('Plan')
    )
    
    # Admin Account für Abrechnung
    is_admin_account = models.BooleanField(
        default=False,
        verbose_name=_('Admin Account für Abrechnung')
    )
    
    # Plan Limits
    dealroom_limit = models.PositiveIntegerField(
        default=3,
        verbose_name=_('Dealroom Limit')
    )
    
    # Billing Information
    company_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Firmenname')
    )
    
    billing_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Abrechnungs-E-Mail')
    )
    
    vat_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('USt-IdNr.')
    )
    
    # Plan Features
    can_use_premium_templates = models.BooleanField(
        default=False,
        verbose_name=_('Premium Templates verfügbar')
    )
    
    can_use_content_library = models.BooleanField(
        default=False,
        verbose_name=_('Content-Bibliothek verfügbar')
    )
    
    can_use_analytics = models.BooleanField(
        default=False,
        verbose_name=_('Analytics verfügbar')
    )
    
    can_use_white_label = models.BooleanField(
        default=False,
        verbose_name=_('White-Label verfügbar')
    )
    
    can_use_api = models.BooleanField(
        default=False,
        verbose_name=_('API-Zugang verfügbar')
    )
    
    # DSGVO Analytics Opt-In
    analytics_opt_in = models.BooleanField(
        default=False,
        verbose_name=_('Analytics-Opt-In (DSGVO-konform)'),
        help_text=_('Ich stimme zu, dass anonymisierte Nutzungsdaten für die Produktoptimierung verwendet werden dürfen.')
    )
    
    # Plan Dates
    plan_start_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Plan Start Datum')
    )
    
    plan_end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Plan End Datum')
    )
    
    # Additional Fields
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Telefon')
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
        verbose_name=_('Avatar')
    )
    
    class Meta:
        verbose_name = _('Benutzer')
        verbose_name_plural = _('Benutzer')
    
    def __str__(self):
        return f"{self.username} ({self.get_plan_display()})"
    
    def get_plan_info(self):
        """Gibt Plan-Informationen zurück"""
        plan_configs = {
            'free': {
                'name': 'Free',
                'price': 0,
                'dealroom_limit': 3,
                'features': [
                    '3 Dealrooms',
                    'Basis-Templates',
                    'E-Mail-Support',
                    'Standard-Features'
                ],
                'can_use_premium_templates': False,
                'can_use_content_library': False,
                'can_use_analytics': False,
                'can_use_white_label': False,
                'can_use_api': False,
            },
            'starter': {
                'name': 'Starter',
                'price': 29,
                'dealroom_limit': 10,
                'features': [
                    '10 Dealrooms',
                    'Premium-Templates',
                    'Content-Bibliothek',
                    'Priority-Support',
                    'Analytics & Tracking'
                ],
                'can_use_premium_templates': True,
                'can_use_content_library': True,
                'can_use_analytics': True,
                'can_use_white_label': False,
                'can_use_api': False,
            },
            'professional': {
                'name': 'Professional',
                'price': 99,
                'dealroom_limit': 50,
                'features': [
                    '50 Dealrooms',
                    'Alle Templates',
                    'Vollständige Content-Bibliothek',
                    'Priority-Support (24h)',
                    'Advanced Analytics',
                    'Custom Branding',
                    'API-Zugang'
                ],
                'can_use_premium_templates': True,
                'can_use_content_library': True,
                'can_use_analytics': True,
                'can_use_white_label': True,
                'can_use_api': True,
            },
            'enterprise': {
                'name': 'Enterprise',
                'price': 299,
                'dealroom_limit': -1,  # Unbegrenzt
                'features': [
                    'Unbegrenzte Dealrooms',
                    'Alle Templates + Custom',
                    'Unbegrenzte Content-Bibliothek',
                    'Dedicated Support',
                    'Advanced Analytics',
                    'Full White-Label',
                    'Unbegrenzter API-Zugang',
                    'SLA-Garantie'
                ],
                'can_use_premium_templates': True,
                'can_use_content_library': True,
                'can_use_analytics': True,
                'can_use_white_label': True,
                'can_use_api': True,
            }
        }
        return plan_configs.get(self.plan, plan_configs['free'])
    
    def can_create_dealroom(self):
        """Prüft ob Benutzer einen neuen Dealroom erstellen kann"""
        from deals.models import Deal
        
        if self.plan == 'enterprise':
            return True
        
        current_dealrooms = Deal.objects.filter(created_by=self).count()
        plan_info = self.get_plan_info()
        limit = plan_info['dealroom_limit']
        
        return current_dealrooms < limit
    
    def get_remaining_dealrooms(self):
        """Gibt die Anzahl der verbleibenden Dealrooms zurück"""
        from deals.models import Deal
        
        if self.plan == 'enterprise':
            return 'Unbegrenzt'
        
        current_dealrooms = Deal.objects.filter(created_by=self).count()
        plan_info = self.get_plan_info()
        limit = plan_info['dealroom_limit']
        
        remaining = limit - current_dealrooms
        return max(0, remaining)
    
    def is_plan_expired(self):
        """Prüft ob der Plan abgelaufen ist"""
        if not self.plan_end_date:
            return False
        from django.utils import timezone
        return timezone.now() > self.plan_end_date
    
    def needs_upgrade(self):
        """Prüft ob ein Upgrade nötig ist"""
        return not self.can_create_dealroom() or self.is_plan_expired()
    
    def get_upgrade_url(self):
        """Gibt die Upgrade-URL zurück"""
        return '/users/upgrade/'
    
    def get_plan_display_name(self):
        """Gibt den Anzeigenamen des Plans zurück"""
        plan_info = self.get_plan_info()
        return plan_info['name']
    
    def get_plan_price(self):
        """Gibt den Preis des Plans zurück"""
        plan_info = self.get_plan_info()
        return plan_info['price']
    
    def get_plan_features(self):
        """Gibt die Features des Plans zurück"""
        plan_info = self.get_plan_info()
        return plan_info['features']
