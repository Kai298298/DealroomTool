"""
Forms für die Deals-App
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Deal, DealFile
from files.models import GlobalFile


class DealForm(forms.ModelForm):
    """
    Formular für Dealroom-Erstellung und -Bearbeitung
    """
    class Meta:
        model = Deal
        fields = [
            'title', 'slug', 'description', 'status', 'template_type',
            'company_name', 'recipient_name', 'recipient_email', 'recipient_company',
            'customer_name', 'customer_email', 'customer_info',
            'central_video_url', 'central_video_file',
            'hero_title', 'hero_subtitle', 'call_to_action',
            'primary_color', 'secondary_color',
            'meta_title', 'meta_description'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'customer_info': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'hero_subtitle': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap-Klassen hinzufügen
        for field in self.fields.values():
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.URLInput, forms.Select)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})


class DealFileForm(forms.ModelForm):
    """
    Formular für Deal-Dateien mit Option für globale Dateien
    """
    class Meta:
        model = DealFile
        fields = ['title', 'description', 'file', 'file_type', 'is_public', 'is_primary']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    # Neue Felder für globale Dateien
    use_global_file = forms.BooleanField(
        required=False,
        initial=False,
        label=_('Globale Datei verwenden'),
        help_text=_('Wählen Sie eine Datei aus der globalen Datei-Verwaltung')
    )
    
    global_file_id = forms.ModelChoiceField(
        queryset=GlobalFile.objects.filter(is_public=True),
        required=False,
        empty_label=_('Globale Datei auswählen...'),
        label=_('Globale Datei'),
        help_text=_('Wählen Sie eine Datei aus der globalen Datei-Verwaltung')
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Bootstrap-Klassen hinzufügen
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.URLInput, forms.Select)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
        
        # JavaScript für Toggle-Funktionalität
        self.fields['use_global_file'].widget.attrs.update({
            'onchange': 'toggleFileInputs()',
            'class': 'form-check-input'
        })
        
        # Initial-Werte setzen
        if self.instance and self.instance.pk:
            if self.instance.file_source == self.instance.FileSource.GLOBAL_ASSIGNED:
                self.fields['use_global_file'].initial = True
                self.fields['global_file_id'].initial = self.instance.global_file
    
    def clean(self):
        cleaned_data = super().clean()
        use_global_file = cleaned_data.get('use_global_file')
        global_file_id = cleaned_data.get('global_file_id')
        file = cleaned_data.get('file')
        
        if use_global_file:
            if not global_file_id:
                raise forms.ValidationError(_('Bitte wählen Sie eine globale Datei aus.'))
            # Datei-Feld leeren wenn globale Datei verwendet wird
            cleaned_data['file'] = None
        else:
            if not file:
                raise forms.ValidationError(_('Bitte laden Sie eine Datei hoch oder wählen Sie eine globale Datei.'))
            # Globale Datei-Felder leeren
            cleaned_data['global_file_id'] = None
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.cleaned_data.get('use_global_file'):
            instance.file_source = instance.FileSource.GLOBAL_ASSIGNED
            instance.global_file = self.cleaned_data.get('global_file_id')
            instance.file = None  # Direkte Datei löschen
        else:
            instance.file_source = instance.FileSource.UPLOADED
            instance.global_file = None  # Globale Referenz löschen
        
        if commit:
            instance.save()
        return instance


class DealFileAssignmentForm(forms.Form):
    """
    Formular für die Zuordnung globaler Dateien zu Dealrooms
    """
    global_file = forms.ModelChoiceField(
        queryset=GlobalFile.objects.filter(is_public=True),
        empty_label=_('Globale Datei auswählen...'),
        label=_('Globale Datei'),
        help_text=_('Wählen Sie eine Datei aus der globalen Datei-Verwaltung')
    )
    
    file_type = forms.ChoiceField(
        choices=DealFile.FileType.choices,
        label=_('Dateityp'),
        help_text=_('Kategorisieren Sie die Datei')
    )
    
    title = forms.CharField(
        max_length=200,
        label=_('Titel'),
        help_text=_('Titel für die Datei im Dealroom')
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label=_('Beschreibung'),
        help_text=_('Optionale Beschreibung der Datei')
    )
    
    is_public = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Öffentlich'),
        help_text=_('Datei ist öffentlich sichtbar')
    )
    
    is_primary = forms.BooleanField(
        required=False,
        initial=False,
        label=_('Primär (für Hero/Logo)'),
        help_text=_('Datei als primäres Hero-Bild oder Logo verwenden')
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Bootstrap-Klassen hinzufügen
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Select)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'}) 