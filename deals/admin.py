"""
Admin-Konfiguration für die Deals-App
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html, mark_safe
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Deal, DealFile, DealFileAssignment, DealChangeLog, ContentBlock, MediaLibrary, LayoutTemplate, DealAnalyticsEvent
from django.contrib.admin.views.main import ChangeList
from django.utils.html import format_html
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Count
from django.utils import timezone


class DealFileInline(admin.TabularInline):
    """
    Inline-Admin für Deal-Dateien
    """
    model = DealFile
    extra = 1
    fields = ['title', 'file', 'file_type', 'is_public', 'is_primary', 'uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    """
    Admin-Konfiguration für Deals (Landingpages) mit Quick-Actions
    """
    list_display = ('title', 'recipient_name', 'status', 'template_type', 'theme_type', 'deal_status', 'deal_progress', 'created_by', 'created_at', 'is_published', 'quick_actions')
    list_filter = ('status', 'template_type', 'theme_type', 'deal_status', 'created_at')
    search_fields = ('title', 'recipient_name', 'recipient_email', 'customer_name', 'description', 'hero_title')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_accessed', 'access_count', 'website_status', 'last_generation')
    inlines = [DealFileInline]
    
    # Quick-Actions
    actions = ['activate_deals', 'deactivate_deals', 'regenerate_websites', 'apply_light_theme', 'apply_dark_theme', 'create_from_template', 'duplicate_deals']
    
    fieldsets = (
        (_('🚀 Quick Setup'), {
            'fields': ('title', 'slug', 'status', 'template_type', 'theme_type'),
            'classes': ('wide',)
        }),
        (_('👤 Kunden-Informationen'), {
            'fields': ('recipient_name', 'recipient_email', 'recipient_company', 'customer_name', 'customer_email', 'customer_info'),
            'classes': ('wide',)
        }),
        (_('📦 Produktbeschreibung'), {
            'fields': ('product_name', 'product_description', 'product_features', 'product_price', 'product_currency'),
            'classes': ('wide',)
        }),
        (_('📊 Deal-Status & Fortschritt'), {
            'fields': ('deal_status', 'deal_progress'),
            'classes': ('wide',)
        }),
        (_('🎨 Begrüßung & Personalisierung'), {
            'fields': ('welcome_message', 'customer_logo_url'),
            'classes': ('wide',)
        }),
        (_('✅ Aufgaben & To-Dos'), {
            'fields': ('customer_tasks',),
            'classes': ('wide',)
        }),
        (_('📞 Kommunikation'), {
            'fields': ('contact_person_name', 'contact_person_email', 'contact_person_phone'),
            'classes': ('wide',)
        }),
        (_('❓ FAQ & Hilfe'), {
            'fields': ('faq_items',),
            'classes': ('wide',)
        }),
        (_('📅 Timeline & Aktivitäten'), {
            'fields': ('timeline_events',),
            'classes': ('wide',)
        }),
        (_('📁 Dokumentenverwaltung'), {
            'fields': ('document_categories', 'document_access_levels'),
            'classes': ('wide',)
        }),
        (_('🎬 Video-Informationen'), {
            'fields': ('central_video_url', 'central_video_file'),
            'classes': ('wide',)
        }),
        (_('🏢 Firmeninformationen'), {
            'fields': ('company_name',),
            'classes': ('wide',)
        }),
        (_('🎯 Landingpage-Inhalt'), {
            'fields': ('hero_title', 'hero_subtitle', 'call_to_action'),
            'classes': ('wide',)
        }),
        (_('🎨 Design'), {
            'fields': ('primary_color', 'secondary_color'),
            'classes': ('wide',)
        }),
        (_('🔍 SEO & URLs'), {
            'fields': ('meta_title', 'meta_description', 'public_url'),
            'classes': ('wide',)
        }),
        (_('📈 Website-Generator'), {
            'fields': ('website_status', 'last_generation', 'generation_error', 'local_website_url'),
            'classes': ('wide', 'collapse'),
        }),
        (_('🔧 HTML-Editor'), {
            'fields': ('html_editor_mode', 'custom_html_header', 'custom_html_body_start', 'custom_html_content', 'custom_html_body_end', 'custom_css', 'custom_javascript', 'last_html_edit', 'html_edit_count'),
            'classes': ('wide', 'collapse'),
        }),
        (_('🔒 Passwortschutz'), {
            'fields': ('password_protection_enabled', 'password_protection_password', 'password_protection_message', 'password_protection_max_attempts', 'password_protection_block_duration', 'password_protection_log_attempts', 'password_protection_attempts', 'password_protection_last_attempt', 'password_protection_blocked_until'),
            'classes': ('wide', 'collapse'),
        }),
        (_('📊 Zugriffs-Tracking'), {
            'fields': ('last_accessed', 'access_count'),
            'classes': ('wide', 'collapse'),
        }),
        (_('👤 Benutzer'), {
            'fields': ('created_by', 'updated_by'),
            'classes': ('wide', 'collapse'),
        }),
        (_('⏰ Zeitstempel'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def quick_actions(self, obj):
        """Quick-Actions für Dealroom"""
        actions = []
        
        # Anzeigen
        if obj.is_published():
            actions.append(f'<a href="{obj.get_landingpage_url()}" class="button" target="_blank">👁️ Anzeigen</a>')
        
        # Regenerieren
        actions.append(f'<a href="?action=regenerate&deal_id={obj.id}" class="button">🔄 Regenerieren</a>')
        
        # Bearbeiten
        actions.append(f'<a href="?action=edit&deal_id={obj.id}" class="button">✏️ Bearbeiten</a>')
        
        # HTML-Editor
        actions.append(f'<a href="?action=html_editor&deal_id={obj.id}" class="button">🔧 HTML-Editor</a>')
        
        # Passwortschutz
        actions.append(f'<a href="?action=password_protection&deal_id={obj.id}" class="button">🔒 Passwortschutz</a>')
        
        # Landingpage-Builder
        actions.append(f'<a href="/dealrooms/{obj.id}/builder/" class="button" style="background: #667eea; color: white;">🎨 Builder</a>')
        
        # Duplizieren
        actions.append(f'<a href="/dealrooms/{obj.id}/duplicate/" class="button" style="background: #28a745; color: white;">🔄 Duplizieren</a>')
        
        return mark_safe(' '.join(actions))
    quick_actions.short_description = 'Quick-Actions'
    quick_actions.allow_tags = True
    
    def is_published(self, obj):
        """Zeigt an ob der Deal veröffentlicht ist"""
        return obj.status == 'active'
    is_published.boolean = True
    is_published.short_description = _('Veröffentlicht')
    
    # Quick-Action Methoden
    def activate_deals(self, request, queryset):
        """Aktiviert ausgewählte Deals"""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} Deal(s) wurden aktiviert.')
    activate_deals.short_description = "Ausgewählte Deals aktivieren"
    
    def deactivate_deals(self, request, queryset):
        """Deaktiviert ausgewählte Deals"""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'{updated} Deal(s) wurden deaktiviert.')
    deactivate_deals.short_description = "Ausgewählte Deals deaktivieren"
    
    def regenerate_websites(self, request, queryset):
        """Regeneriert Websites für ausgewählte Deals"""
        from .views import RegenerateWebsiteView
        count = 0
        for deal in queryset:
            try:
                view = RegenerateWebsiteView()
                view.regenerate_website(deal)
                count += 1
            except Exception as e:
                self.message_user(request, f'Fehler bei Deal {deal.title}: {str(e)}', level=messages.ERROR)
        self.message_user(request, f'{count} Website(s) wurden regeneriert.')
    regenerate_websites.short_description = "Websites regenerieren"
    
    def apply_light_theme(self, request, queryset):
        """Wendet Light Theme auf ausgewählte Deals an"""
        updated = queryset.update(theme_type='light')
        self.message_user(request, f'{updated} Deal(s) auf Light Theme gesetzt.')
    apply_light_theme.short_description = "Light Theme anwenden"
    
    def apply_dark_theme(self, request, queryset):
        """Wendet Dark Theme auf ausgewählte Deals an"""
        updated = queryset.update(theme_type='dark')
        self.message_user(request, f'{updated} Deal(s) auf Dark Theme gesetzt.')
    apply_dark_theme.short_description = "Dark Theme anwenden"
    
    def create_from_template(self, request, queryset):
        """Erstellt neue Deals aus Templates"""
        # Diese Action wird nur für die Template-Auswahl verwendet
        # Die eigentliche Erstellung erfolgt über eine separate View
        self.message_user(request, 'Bitte verwenden Sie "Deal hinzufügen" und wählen Sie ein Template aus.')
    create_from_template.short_description = "Aus Template erstellen"
    
    def duplicate_deals(self, request, queryset):
        """Dupliziert ausgewählte Deals"""
        duplicated_count = 0
        for deal in queryset:
            try:
                new_deal = deal.duplicate(
                    new_title=f"{deal.title} (Kopie)",
                    include_files=True,
                    include_content=True
                )
                duplicated_count += 1
                self.message_user(request, f'Deal "{deal.title}" wurde dupliziert zu "{new_deal.title}"')
            except Exception as e:
                self.message_user(request, f'Fehler beim Duplizieren von "{deal.title}": {str(e)}', level=messages.ERROR)
        
        if duplicated_count > 0:
            self.message_user(request, f'{duplicated_count} Deal(s) wurden erfolgreich dupliziert!')
        else:
            self.message_user(request, 'Keine Deals konnten dupliziert werden.', level=messages.WARNING)
    duplicate_deals.short_description = "Ausgewählte Deals duplizieren"
    
    def save_model(self, request, obj, form, change):
        """Speichert den aktualisierenden Benutzer"""
        if not change:  # Neuer Deal
            obj.created_by = request.user
        else:  # Bestehender Deal
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def response_add(self, request, obj, post_url_continue=None):
        """Nach dem Hinzufügen eines Deals"""
        messages.success(request, f'Deal "{obj.title}" wurde erfolgreich erstellt!')
        return super().response_add(request, obj, post_url_continue)
    
    def response_change(self, request, obj):
        """Nach dem Ändern eines Deals"""
        messages.success(request, f'Deal "{obj.title}" wurde erfolgreich aktualisiert!')
        return super().response_change(request, obj)
    
    def changelist_view(self, request, extra_context=None):
        """Erweitert die Changelist-View um Quick-Setup Button"""
        extra_context = extra_context or {}
        extra_context['show_quick_setup'] = True
        return super().changelist_view(request, extra_context)


@admin.register(DealFile)
class DealFileAdmin(admin.ModelAdmin):
    """
    Admin-Konfiguration für Deal-Dateien mit erweiterten Features
    """
    list_display = ('title', 'deal', 'file_type', 'document_category', 'document_access_level', 'uploaded_by', 'uploaded_at', 'is_public', 'is_primary')
    list_filter = ('file_type', 'document_category', 'document_access_level', 'is_public', 'is_primary', 'uploaded_at')
    search_fields = ('title', 'description', 'deal__title')
    readonly_fields = ('uploaded_at', 'uploaded_by')
    ordering = ('-uploaded_at',)
    
    # Bulk-Actions für Dokumentenverwaltung
    actions = ['make_public', 'make_private', 'require_signature', 'remove_signature_requirement']
    
    fieldsets = (
        (_('📁 Grundinformationen'), {
            'fields': ('deal', 'title', 'description', 'file', 'file_type'),
            'classes': ('wide',)
        }),
        (_('📋 Dokumentenverwaltung'), {
            'fields': ('document_category', 'document_version', 'document_access_level', 'document_expiry_date', 'document_requires_signature'),
            'classes': ('wide',)
        }),
        (_('🔒 Zugriff & Sichtbarkeit'), {
            'fields': ('is_public', 'is_primary'),
            'classes': ('wide',)
        }),
        (_('👤 Benutzer & Zeitstempel'), {
            'fields': ('uploaded_by', 'uploaded_at'),
            'classes': ('wide',)
        }),
    )
    
    def make_public(self, request, queryset):
        """Macht alle ausgewählten Dateien öffentlich"""
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} Dateien wurden öffentlich gemacht.')
    make_public.short_description = "Ausgewählte Dateien öffentlich machen"
    
    def make_private(self, request, queryset):
        """Macht alle ausgewählten Dateien privat"""
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} Dateien wurden privat gemacht.')
    make_private.short_description = "Ausgewählte Dateien privat machen"
    
    def require_signature(self, request, queryset):
        """Macht Unterschrift für alle ausgewählten Dateien erforderlich"""
        updated = queryset.update(document_requires_signature=True)
        self.message_user(request, f'{updated} Dateien erfordern jetzt eine Unterschrift.')
    require_signature.short_description = "Unterschrift für ausgewählte Dateien erforderlich machen"
    
    def remove_signature_requirement(self, request, queryset):
        """Entfernt Unterschrift-Anforderung für alle ausgewählten Dateien"""
        updated = queryset.update(document_requires_signature=False)
        self.message_user(request, f'{updated} Dateien erfordern keine Unterschrift mehr.')
    remove_signature_requirement.short_description = "Unterschrift-Anforderung für ausgewählte Dateien entfernen"


# Content-Bibliothek Admin
@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    """
    Admin-Konfiguration für Content-Blöcke
    """
    list_display = ('title', 'content_type', 'category', 'usage_count', 'is_active', 'created_by', 'created_at')
    list_filter = ('content_type', 'category', 'is_active', 'created_at')
    search_fields = ('title', 'content', 'description')
    readonly_fields = ('usage_count', 'created_at', 'updated_at')
    ordering = ('category', 'title')
    
    fieldsets = (
        (_('📝 Grundinformationen'), {
            'fields': ('title', 'content_type', 'category', 'content', 'description'),
            'classes': ('wide',)
        }),
        (_('🏷️ Kategorisierung'), {
            'fields': ('tags', 'is_active'),
            'classes': ('wide',)
        }),
        (_('📊 Statistiken'), {
            'fields': ('usage_count', 'created_by', 'created_at', 'updated_at'),
            'classes': ('wide',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Nur bei neuen Objekten
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MediaLibrary)
class MediaLibraryAdmin(admin.ModelAdmin):
    """
    Admin-Konfiguration für Medien-Bibliothek
    """
    list_display = ('title', 'media_type', 'category', 'usage_count', 'is_active', 'created_by', 'created_at')
    list_filter = ('media_type', 'category', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'alt_text')
    readonly_fields = ('usage_count', 'created_at')
    ordering = ('category', 'title')
    
    fieldsets = (
        (_('🖼️ Grundinformationen'), {
            'fields': ('title', 'media_type', 'category', 'file', 'description', 'alt_text'),
            'classes': ('wide',)
        }),
        (_('🏷️ Kategorisierung'), {
            'fields': ('tags', 'is_active'),
            'classes': ('wide',)
        }),
        (_('📊 Statistiken'), {
            'fields': ('usage_count', 'created_by', 'created_at'),
            'classes': ('wide',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Nur bei neuen Objekten
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(LayoutTemplate)
class LayoutTemplateAdmin(admin.ModelAdmin):
    """
    Admin-Konfiguration für Layout-Vorlagen
    """
    list_display = ('title', 'layout_type', 'category', 'usage_count', 'is_active', 'created_by', 'created_at')
    list_filter = ('layout_type', 'category', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'css_classes', 'html_structure')
    readonly_fields = ('usage_count', 'created_at')
    ordering = ('category', 'title')
    
    fieldsets = (
        (_('🎨 Grundinformationen'), {
            'fields': ('title', 'layout_type', 'category', 'description'),
            'classes': ('wide',)
        }),
        (_('💻 Code & Struktur'), {
            'fields': ('css_classes', 'html_structure'),
            'classes': ('wide',)
        }),
        (_('🖼️ Vorschau'), {
            'fields': ('preview_image',),
            'classes': ('wide',)
        }),
        (_('📊 Statistiken'), {
            'fields': ('usage_count', 'is_active', 'created_by', 'created_at'),
            'classes': ('wide',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Nur bei neuen Objekten
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class DealAnalyticsAdmin(admin.ModelAdmin):
    change_list_template = 'admin/deals/analytics_dashboard.html'
    model = DealAnalyticsEvent
    
    def changelist_view(self, request, extra_context=None):
        # Gesamtzahl Deals
        total_deals = Deal.objects.count()
        # Deals pro Tag (letzte 30 Tage)
        today = timezone.now().date()
        last_30 = [today - timezone.timedelta(days=i) for i in range(29, -1, -1)]
        deals_per_day = [
            Deal.objects.filter(created_at__date=day).count() for day in last_30
        ]
        # Top-User
        top_users = Deal.objects.values('created_by__username').annotate(
            count=Count('id')).order_by('-count')[:5]
        # Events gesamt
        total_events = DealAnalyticsEvent.objects.count()
        # Events pro Typ
        events_by_type = DealAnalyticsEvent.objects.values('event_type').annotate(
            count=Count('id')).order_by('-count')
        extra_context = extra_context or {}
        extra_context.update({
            'total_deals': total_deals,
            'deals_per_day': list(zip(last_30, deals_per_day)),
            'top_users': top_users,
            'total_events': total_events,
            'events_by_type': events_by_type,
        })
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(DealAnalyticsEvent, DealAnalyticsAdmin)
