"""
Forms für die Deals-App
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Deal, DealFile


class DealForm(forms.ModelForm):
    """
    Formular für Dealrooms - Vereinfacht für bessere UX
    """
    class Meta:
        model = Deal
        fields = [
            'title', 'slug', 'description', 'status', 'template_type',
            'recipient_name', 'recipient_email',
            'central_video_url', 'central_video_file',
            'hero_title', 'hero_subtitle', 'call_to_action',
            'primary_color', 'secondary_color'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'hero_subtitle': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Labels anpassen
        self.fields['title'].label = _('Dealroom-Titel')
        self.fields['slug'].label = _('URL-Slug')
        self.fields['description'].label = _('Beschreibung')
        self.fields['status'].label = _('Status')
        self.fields['template_type'].label = _('Designvorlage')
        self.fields['recipient_name'].label = _('Empfänger Name')
        self.fields['recipient_email'].label = _('Empfänger E-Mail')
        self.fields['central_video_url'].label = _('Zentrales Video (YouTube/Vimeo)')
        self.fields['central_video_file'].label = _('Zentrales Video (Datei)')
        self.fields['hero_title'].label = _('Hero-Titel')
        self.fields['hero_subtitle'].label = _('Hero-Untertitel')
        self.fields['call_to_action'].label = _('Call-to-Action Text')
        self.fields['primary_color'].label = _('Primärfarbe')
        self.fields['secondary_color'].label = _('Sekundärfarbe')
        
        # Pflichtfelder markieren
        self.fields['title'].required = True
        self.fields['slug'].required = True
        self.fields['recipient_email'].required = True
        
        # Hilfe-Texte
        self.fields['slug'].help_text = _('URL-freundlicher Name für den Dealroom (z.B. "mein-dealroom-2024")')
        self.fields['recipient_name'].help_text = _('Name des Empfängers (z.B. "Max Mustermann")')
        self.fields['recipient_email'].help_text = _('E-Mail-Adresse des Empfängers')
        self.fields['central_video_url'].help_text = _('YouTube oder Vimeo Link (z.B. https://youtube.com/watch?v=...)')
        self.fields['central_video_file'].help_text = _('Video-Datei hochladen (MP4, AVI, MOV)')
        self.fields['hero_title'].help_text = _('Haupttitel des Dealrooms (wird prominent angezeigt)')
        self.fields['hero_subtitle'].help_text = _('Untertitel oder Beschreibung unter dem Haupttitel')
        self.fields['call_to_action'].help_text = _('Text für den Haupt-Button (z.B. "Jetzt kontaktieren")')
        
        # Bootstrap-Klassen hinzufügen
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs = {'class': 'form-control'}


class DealFileForm(forms.ModelForm):
    """
    Formular für Deal-Dateien
    """
    class Meta:
        model = DealFile
        fields = ['title', 'description', 'file', 'file_type', 'is_public', 'is_primary']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Labels anpassen
        self.fields['title'].label = _('Titel')
        self.fields['description'].label = _('Beschreibung')
        self.fields['file'].label = _('Datei')
        self.fields['file_type'].label = _('Dateityp')
        self.fields['is_public'].label = _('Öffentlich')
        self.fields['is_primary'].label = _('Primär (für Hero/Logo)')
        
        # Hilfe-Texte
        self.fields['file'].help_text = _('Wählen Sie eine Datei zum Hochladen aus')
        self.fields['file_type'].help_text = _('Kategorisieren Sie die Datei für bessere Organisation')
        self.fields['is_public'].help_text = _('Öffentliche Dateien sind für alle Benutzer sichtbar')
        self.fields['is_primary'].help_text = _('Primäre Dateien werden als Hero-Bild oder Logo verwendet')
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Dateigröße prüfen (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError(_('Datei ist zu groß. Maximale Größe: 10MB'))
            
            # Dateityp prüfen
            allowed_types = [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp',
                'application/pdf', 'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'video/mp4', 'video/avi', 'video/mov'
            ]
            
            if hasattr(file, 'content_type') and file.content_type not in allowed_types:
                raise forms.ValidationError(_('Dateityp nicht erlaubt. Erlaubte Typen: Bilder, PDF, Word, Videos'))
        
        return file 