from django import forms
from django.utils.translation import gettext_lazy as _
from .models import GlobalFile


class GlobalFileForm(forms.ModelForm):
    """
    Formular für globale Dateien
    """
    class Meta:
        model = GlobalFile
        fields = ['title', 'description', 'file', 'file_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Labels anpassen
        self.fields['title'].label = _('Titel')
        self.fields['description'].label = _('Beschreibung')
        self.fields['file'].label = _('Datei')
        self.fields['file_type'].label = _('Dateityp')
        
        # Hilfe-Texte
        self.fields['file'].help_text = _('Wählen Sie eine Datei zum Hochladen aus')
        self.fields['file_type'].help_text = _('Kategorisieren Sie die Datei für bessere Organisation')
        
        # Bootstrap-Klassen hinzufügen
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs = {'class': 'form-control'}
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Dateigröße prüfen (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError(_('Datei ist zu groß. Maximale Größe: 10MB'))
            
            # Dateityp prüfen
            allowed_types = [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
                'application/pdf', 'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.ms-powerpoint',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'text/plain', 'text/csv',
                'video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/flv', 'video/webm'
            ]
            
            if hasattr(file, 'content_type') and file.content_type not in allowed_types:
                raise forms.ValidationError(_('Dateityp nicht unterstützt. Erlaubte Formate: Bilder, Dokumente, Videos'))
        
        return file 