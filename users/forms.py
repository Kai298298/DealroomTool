"""
Forms für die Users-App
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """
    Benutzerdefiniertes Formular für die Benutzerregistrierung
    """
    email = forms.EmailField(
        required=True,
        help_text=_('Bitte geben Sie eine gültige E-Mail-Adresse ein.')
    )
    first_name = forms.CharField(
        required=True,
        label=_('Vorname')
    )
    last_name = forms.CharField(
        required=True,
        label=_('Nachname')
    )
    role = forms.ChoiceField(
        choices=CustomUser.UserRole.choices,
        required=True,
        label=_('Rolle'),
        initial=CustomUser.UserRole.VIEWER
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Felder als erforderlich markieren
        self.fields['username'].help_text = _('Benötigt. 150 Zeichen oder weniger. Nur Buchstaben, Ziffern und @/./+/-/_ erlaubt.')
        self.fields['password1'].help_text = _('Ihr Passwort muss mindestens 8 Zeichen lang sein und darf nicht zu einfach sein.')
        self.fields['password2'].help_text = _('Geben Sie dasselbe Passwort wie oben ein, zur Überprüfung.')
        self.fields['username'].label = _('Benutzername')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user



class CustomUserChangeForm(UserChangeForm):
    """
    Benutzerdefiniertes Formular für die Benutzerbearbeitung
    """
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'company', 'phone', 'bio', 'avatar')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Labels anpassen
        self.fields['username'].label = _('Benutzername')
        self.fields['email'].label = _('E-Mail')
        self.fields['first_name'].label = _('Vorname')
        self.fields['last_name'].label = _('Nachname')
        self.fields['role'].label = _('Rolle')
        self.fields['company'].label = _('Unternehmen')
        self.fields['phone'].label = _('Telefonnummer')
        self.fields['bio'].label = _('Biografie')
        self.fields['avatar'].label = _('Profilbild')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Prüfe ob E-Mail bereits von einem anderen Benutzer verwendet wird
            existing_user = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise forms.ValidationError(_('Diese E-Mail-Adresse wird bereits verwendet.'))
        return email


class ProfileEditForm(forms.ModelForm):
    """
    Formular für die Bearbeitung des eigenen Profils
    """
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'company', 'bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Labels anpassen
        self.fields['first_name'].label = _('Vorname')
        self.fields['last_name'].label = _('Nachname')
        self.fields['email'].label = _('E-Mail')
        self.fields['phone'].label = _('Telefonnummer')
        self.fields['company'].label = _('Unternehmen')
        self.fields['bio'].label = _('Biografie')
        self.fields['avatar'].label = _('Profilbild')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Prüfe ob E-Mail bereits von einem anderen Benutzer verwendet wird
            existing_user = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise forms.ValidationError(_('Diese E-Mail-Adresse wird bereits verwendet.'))
        return email 