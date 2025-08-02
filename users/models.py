"""
Models für die Users-App
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


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
        default=timezone.now,
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
        return f"{self.get_full_name()} ({self.username})"
    
    def get_plan_info(self):
        """
        Gibt Informationen über den aktuellen Plan zurück
        """
        plan_info = {
            'free': {
                'name': 'Free',
                'price': 0,
                'dealrooms': 3,
                'features': ['Grundlegende Templates', 'Basis-Support'],
                'description': 'Perfekt zum Einstieg'
            },
            'starter': {
                'name': 'Starter',
                'price': 29,
                'dealrooms': 10,
                'features': ['Premium Templates', 'Content-Bibliothek', 'E-Mail Support'],
                'description': 'Für wachsende Teams'
            },
            'professional': {
                'name': 'Professional',
                'price': 79,
                'dealrooms': 50,
                'features': ['Alle Starter Features', 'Analytics', 'White-Label', 'Priority Support'],
                'description': 'Für professionelle Nutzung'
            },
            'enterprise': {
                'name': 'Enterprise',
                'price': 199,
                'dealrooms': -1,  # Unbegrenzt
                'features': ['Alle Professional Features', 'API-Zugang', 'Dedicated Support', 'Custom Features'],
                'description': 'Für große Unternehmen'
            }
        }
        
        return plan_info.get(self.plan, plan_info['free'])
    
    def can_create_dealroom(self):
        """
        Prüft ob der User noch einen Dealroom erstellen kann
        """
        if self.plan == 'enterprise':
            return True
        
        current_count = self.created_deals.count()
        return current_count < self.dealroom_limit
    
    def get_remaining_dealrooms(self):
        """
        Gibt die Anzahl der verbleibenden Dealrooms zurück
        """
        if self.plan == 'enterprise':
            return 'Unbegrenzt'
        
        current_count = self.created_deals.count()
        remaining = self.dealroom_limit - current_count
        return max(0, remaining)
    
    def is_plan_expired(self):
        """
        Prüft ob der Plan abgelaufen ist
        """
        return self.plan_end_date and self.plan_end_date < timezone.now()
    
    def needs_upgrade(self):
        """
        Prüft ob ein Upgrade empfohlen wird
        """
        return self.plan == 'free' and self.created_deals.count() >= 2
    
    def get_upgrade_url(self):
        """
        Gibt die Upgrade-URL zurück
        """
        return '/users/upgrade/'
    
    def get_plan_display_name(self):
        """
        Gibt den Anzeigenamen des Plans zurück
        """
        return dict(self.PLAN_CHOICES).get(self.plan, 'Free')
    
    def get_plan_price(self):
        """
        Gibt den Preis des Plans zurück
        """
        plan_info = self.get_plan_info()
        return plan_info.get('price', 0)
    
    def get_plan_features(self):
        """
        Gibt die Features des Plans zurück
        """
        plan_info = self.get_plan_info()
        return plan_info.get('features', [])


@receiver(post_save, sender=CustomUser)
def create_welcome_dealroom(sender, instance, created, **kwargs):
    """
    Erstellt automatisch einen Werbe-Dealroom für neue User
    """
    if created and not instance.is_superuser:
        try:
            from deals.models import Deal
            
            # Werbe-Dealroom für das Dealroom-Tool erstellen
            welcome_deal = Deal.objects.create(
                title='Willkommen bei DealShare',
                slug='welcome-dealshare',
                company_name='DealShare',
                description='Entdecken Sie die Möglichkeiten von DealShare - der modernsten Plattform für professionelle Dealrooms und Landingpages.',
                hero_title='Die Zukunft der Dealroom-Erstellung',
                hero_subtitle='Erstellen Sie beeindruckende Landingpages in Minuten, nicht in Stunden',
                deal_progress=100,
                status='active',
                template_type='modern',
                theme_type='light',
                created_by=instance,
                # Marketing-spezifische Felder
                welcome_message='Willkommen bei DealShare! Entdecken Sie, wie einfach es ist, professionelle Dealrooms zu erstellen.',
                call_to_action='Jetzt Dealroom erstellen',
                # SEO-Felder
                meta_title='DealShare - Professionelle Dealroom-Erstellung',
                meta_description='Erstellen Sie beeindruckende Landingpages für Ihre Deals mit DealShare. Modern, schnell und professionell.',
                # Custom HTML für Marketing
                custom_html_content='''
                <div class="welcome-section">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-8 mx-auto text-center">
                                <h2 class="display-4 mb-4">🚀 Willkommen bei DealShare</h2>
                                <p class="lead mb-4">
                                    Erstellen Sie professionelle Dealrooms und Landingpages in wenigen Minuten. 
                                    Keine Programmierkenntnisse erforderlich!
                                </p>
                                
                                <div class="features-grid mt-5">
                                    <div class="row">
                                        <div class="col-md-4">
                                            <div class="feature-card">
                                                <i class="bi bi-lightning-charge text-primary fs-1"></i>
                                                <h4>Schnell & Einfach</h4>
                                                <p>Erstellen Sie Landingpages in Minuten</p>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="feature-card">
                                                <i class="bi bi-palette text-success fs-1"></i>
                                                <h4>Professionelle Templates</h4>
                                                <p>Moderne Designs für jeden Anlass</p>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="feature-card">
                                                <i class="bi bi-shield-check text-warning fs-1"></i>
                                                <h4>Sicher & DSGVO-konform</h4>
                                                <p>Ihre Daten sind bei uns sicher</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="cta-section mt-5">
                                    <a href="/deals/create/" class="btn btn-primary btn-lg me-3">
                                        <i class="bi bi-plus-circle me-2"></i>Ersten Dealroom erstellen
                                    </a>
                                    <a href="/users/pricing/" class="btn btn-outline-primary btn-lg">
                                        <i class="bi bi-credit-card me-2"></i>Pläne ansehen
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                ''',
                custom_css='''
                .welcome-section {
                    padding: 4rem 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .feature-card {
                    text-align: center;
                    padding: 2rem 1rem;
                    background: rgba(255,255,255,0.1);
                    border-radius: 10px;
                    margin-bottom: 1rem;
                }
                .feature-card h4 {
                    margin: 1rem 0;
                    color: white;
                }
                .feature-card p {
                    color: rgba(255,255,255,0.8);
                }
                .cta-section {
                    margin-top: 3rem;
                }
                '''
            )
            
            print(f"✅ Willkommens-Dealroom für {instance.username} erstellt: {welcome_deal.title}")
            
        except Exception as e:
            print(f"❌ Fehler beim Erstellen des Willkommens-Dealrooms für {instance.username}: {e}")
