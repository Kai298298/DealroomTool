"""
Admin-Konfiguration für die Users-App
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    """
    Admin-Konfiguration für das erweiterte Benutzermodell
    """
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    
    # Listen-Anzeige
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'plan', 'company_name', 'is_admin_account', 'is_active'
    ]
    
    # Filter
    list_filter = [
        'plan', 'is_admin_account', 'is_active', 'is_staff',
        'can_use_premium_templates', 'can_use_content_library',
        'can_use_analytics', 'can_use_white_label', 'can_use_api'
    ]
    
    # Suchfelder
    search_fields = ['username', 'email', 'first_name', 'last_name', 'company_name']
    
    # Sortierung
    ordering = ['username']
    
    # Readonly-Felder
    readonly_fields = ['plan_start_date', 'plan_end_date']
    
    # Feldsets
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Persönliche Informationen'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'bio', 'avatar')
        }),
        (_('SaaS-Plan'), {
            'fields': (
                'plan', 'is_admin_account', 'dealroom_limit',
                'can_use_premium_templates', 'can_use_content_library',
                'can_use_analytics', 'can_use_white_label', 'can_use_api',
                'plan_start_date', 'plan_end_date'
            ),
            'classes': ('wide',)
        }),
        (_('Abrechnung'), {
            'fields': ('company_name', 'billing_email', 'vat_number'),
            'classes': ('wide',)
        }),
        (_('DSGVO & Datenschutz'), {
            'fields': ('analytics_opt_in',),
            'classes': ('wide',),
            'description': _('DSGVO-konforme Einwilligungen für Analytics und Datenschutz')
        }),
        (_('Berechtigungen'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('wide',)
        }),
        (_('Wichtige Daten'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('wide',)
        }),
    )
    
    # Add-Fieldsets
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'first_name', 'last_name', 'company_name', 'billing_email',
                'is_admin_account', 'plan'
            ),
        }),
    )
    
    # Admin-Actions
    actions = ['upgrade_to_starter', 'upgrade_to_professional', 'upgrade_to_enterprise', 'downgrade_to_free']
    
    def upgrade_to_starter(self, request, queryset):
        """Upgrade auf Starter-Plan"""
        for user in queryset:
            user.plan = 'starter'
            plan_info = user.get_plan_info()
            user.can_use_premium_templates = plan_info['can_use_premium_templates']
            user.can_use_content_library = plan_info['can_use_content_library']
            user.can_use_analytics = plan_info['can_use_analytics']
            user.can_use_white_label = plan_info['can_use_white_label']
            user.can_use_api = plan_info['can_use_api']
            user.save()
        
        self.message_user(request, f'{queryset.count()} Benutzer auf Starter-Plan upgegradet.')
    upgrade_to_starter.short_description = "Auf Starter-Plan upgraden"
    
    def upgrade_to_professional(self, request, queryset):
        """Upgrade auf Professional-Plan"""
        for user in queryset:
            user.plan = 'professional'
            plan_info = user.get_plan_info()
            user.can_use_premium_templates = plan_info['can_use_premium_templates']
            user.can_use_content_library = plan_info['can_use_content_library']
            user.can_use_analytics = plan_info['can_use_analytics']
            user.can_use_white_label = plan_info['can_use_white_label']
            user.can_use_api = plan_info['can_use_api']
            user.save()
        
        self.message_user(request, f'{queryset.count()} Benutzer auf Professional-Plan upgegradet.')
    upgrade_to_professional.short_description = "Auf Professional-Plan upgraden"
    
    def upgrade_to_enterprise(self, request, queryset):
        """Upgrade auf Enterprise-Plan"""
        for user in queryset:
            user.plan = 'enterprise'
            plan_info = user.get_plan_info()
            user.can_use_premium_templates = plan_info['can_use_premium_templates']
            user.can_use_content_library = plan_info['can_use_content_library']
            user.can_use_analytics = plan_info['can_use_analytics']
            user.can_use_white_label = plan_info['can_use_white_label']
            user.can_use_api = plan_info['can_use_api']
            user.save()
        
        self.message_user(request, f'{queryset.count()} Benutzer auf Enterprise-Plan upgegradet.')
    upgrade_to_enterprise.short_description = "Auf Enterprise-Plan upgraden"
    
    def downgrade_to_free(self, request, queryset):
        """Downgrade auf Free-Plan"""
        for user in queryset:
            user.plan = 'free'
            plan_info = user.get_plan_info()
            user.can_use_premium_templates = plan_info['can_use_premium_templates']
            user.can_use_content_library = plan_info['can_use_content_library']
            user.can_use_analytics = plan_info['can_use_analytics']
            user.can_use_white_label = plan_info['can_use_white_label']
            user.can_use_api = plan_info['can_use_api']
            user.save()
        
        self.message_user(request, f'{queryset.count()} Benutzer auf Free-Plan downgraded.')
    downgrade_to_free.short_description = "Auf Free-Plan downgraden"
    
    def get_plan_display(self, obj):
        """Anzeige des Plans mit Preis"""
        plan_info = obj.get_plan_info()
        return f"{plan_info['name']} (€{plan_info['price']}/Monat)"
    get_plan_display.short_description = "Plan"
    
    def get_remaining_dealrooms(self, obj):
        """Anzeige der verbleibenden Dealrooms"""
        return obj.get_remaining_dealrooms()
    get_remaining_dealrooms.short_description = "Verbleibende Dealrooms"


# Admin registrieren
admin.site.register(CustomUser, CustomUserAdmin)
