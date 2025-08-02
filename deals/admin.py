"""
Admin-Konfiguration für die Deals-App
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Deal, DealFile


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
    Admin-Konfiguration für Deals (Landingpages)
    """
    list_display = ('title', 'recipient_name', 'recipient_email', 'status', 'template_type', 'created_by', 'created_at', 'is_published')
    list_filter = ('status', 'template_type', 'created_at')
    search_fields = ('title', 'recipient_name', 'recipient_email', 'customer_name', 'description', 'hero_title')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_accessed', 'access_count')
    inlines = [DealFileInline]
    
    fieldsets = (
        (_('Grundlegende Informationen'), {
            'fields': ('title', 'slug', 'description', 'status', 'template_type')
        }),
        (_('Empfänger-Informationen'), {
            'fields': ('recipient_name', 'recipient_email', 'recipient_company')
        }),
        (_('Kunden-Informationen'), {
            'fields': ('customer_name', 'customer_email', 'customer_info')
        }),
        (_('Video-Informationen'), {
            'fields': ('central_video_url', 'central_video_file')
        }),
        (_('Firmeninformationen'), {
            'fields': ('company_name',)
        }),
        (_('Landingpage-Inhalt'), {
            'fields': ('hero_title', 'hero_subtitle', 'call_to_action')
        }),
        (_('Design'), {
            'fields': ('primary_color', 'secondary_color')
        }),
        (_('SEO & URLs'), {
            'fields': ('meta_title', 'meta_description', 'public_url')
        }),
        (_('Zugriffs-Tracking'), {
            'fields': ('last_accessed', 'access_count')
        }),
        (_('Benutzer'), {
            'fields': ('created_by', 'updated_by')
        }),
        (_('Zeitstempel'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_published(self, obj):
        """Zeigt an ob der Deal veröffentlicht ist"""
        return obj.status == 'active'
    is_published.boolean = True
    is_published.short_description = _('Veröffentlicht')
    
    def save_model(self, request, obj, form, change):
        """Speichert den aktualisierenden Benutzer"""
        if not change:  # Neuer Deal
            obj.created_by = request.user
        else:  # Bestehender Deal
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(DealFile)
class DealFileAdmin(admin.ModelAdmin):
    """
    Admin-Konfiguration für Deal-Dateien
    """
    list_display = ('title', 'deal', 'file_type', 'uploaded_by', 'uploaded_at', 'is_public', 'is_primary')
    list_filter = ('file_type', 'is_public', 'is_primary', 'uploaded_at')
    search_fields = ('title', 'description', 'deal__title', 'uploaded_by__username')
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_at',)
    
    fieldsets = (
        (_('Grundlegende Informationen'), {
            'fields': ('deal', 'title', 'description')
        }),
        (_('Datei'), {
            'fields': ('file', 'file_type')
        }),
        (_('Einstellungen'), {
            'fields': ('is_public', 'is_primary')
        }),
        (_('Benutzer'), {
            'fields': ('uploaded_by',)
        }),
        (_('Zeitstempel'), {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Speichert den hochladenden Benutzer"""
        if not change:  # Neue Datei
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
