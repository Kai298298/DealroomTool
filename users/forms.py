"""
Forms für die Users-App
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

CustomUser = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    Formular für die Benutzerregistrierung mit SaaS-Features
    """
    # SaaS-spezifische Felder
    company_name = forms.CharField(
        max_length=200,
        required=False,
        label=_('Firmenname'),
        help_text=_('Optional: Für Abrechnungszwecke')
    )
    
    billing_email = forms.EmailField(
        required=False,
        label=_('Abrechnungs-E-Mail'),
        help_text=_('Optional: Für Rechnungen und Support')
    )
    
    is_admin_account = forms.BooleanField(
        required=False,
        label=_('Admin Account für Abrechnung'),
        help_text=_('Dieser Account ist für die Abrechnung zuständig')
    )
    
    # Plan-Auswahl (nur für Admin-Accounts)
    plan = forms.ChoiceField(
        choices=CustomUser.PLAN_CHOICES,
        initial='free',
        label=_('Plan'),
        help_text=_('Wählen Sie Ihren SaaS-Plan')
    )
    
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'password1', 'password2', 'company_name', 'billing_email',
            'is_admin_account', 'plan'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Nur Free-Plan für neue Registrierungen
        self.fields['plan'].initial = 'free'
        self.fields['plan'].widget.attrs['readonly'] = True
        self.fields['plan'].help_text = _('Neue Benutzer starten mit dem Free-Plan')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Setze Standard-Plan für neue Benutzer
        user.plan = 'free'
        
        # Aktualisiere Plan-Features basierend auf dem Plan
        plan_info = user.get_plan_info()
        user.can_use_premium_templates = plan_info['can_use_premium_templates']
        user.can_use_content_library = plan_info['can_use_content_library']
        user.can_use_analytics = plan_info['can_use_analytics']
        user.can_use_white_label = plan_info['can_use_white_label']
        user.can_use_api = plan_info['can_use_api']
        
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """
    Formular für die Benutzerbearbeitung
    """
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'company_name', 'billing_email', 'phone', 'bio',
            'avatar', 'plan', 'is_admin_account', 'analytics_opt_in'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Nur Admin-Accounts können den Plan ändern
        if not self.instance.is_admin_account:
            self.fields['plan'].widget.attrs['readonly'] = True
            self.fields['plan'].help_text = _('Nur Admin-Accounts können den Plan ändern')
        
        # DSGVO-Hinweis für Analytics-Opt-In
        self.fields['analytics_opt_in'].help_text = _(
            'Ich stimme zu, dass anonymisierte Nutzungsdaten für die Produktoptimierung von DealShare verwendet werden dürfen. '
            'Keine personenbezogenen Daten werden gespeichert. Sie können diese Einwilligung jederzeit widerrufen.'
        )


class PlanUpgradeForm(forms.Form):
    """
    Formular für Plan-Upgrades
    """
    plan = forms.ChoiceField(
        choices=CustomUser.PLAN_CHOICES,
        label=_('Neuer Plan'),
        help_text=_('Wählen Sie Ihren neuen Plan')
    )
    
    billing_cycle = forms.ChoiceField(
        choices=[
            ('monthly', 'Monatlich'),
            ('yearly', 'Jährlich (20% Rabatt)'),
        ],
        initial='monthly',
        label=_('Abrechnungszyklus'),
        help_text=_('Jährliche Abrechnung spart 20%')
    )
    
    company_name = forms.CharField(
        max_length=200,
        required=False,
        label=_('Firmenname'),
        help_text=_('Für Rechnungsstellung')
    )
    
    billing_email = forms.EmailField(
        required=True,
        label=_('Abrechnungs-E-Mail'),
        help_text=_('Rechnungen werden an diese E-Mail gesendet')
    )
    
    vat_number = forms.CharField(
        max_length=50,
        required=False,
        label=_('USt-IdNr.'),
        help_text=_('Optional: Für EU-Rechnungen')
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        label=_('Ich akzeptiere die AGB und Datenschutzerklärung'),
        help_text=_('Erforderlich für das Upgrade')
    )
    
    def clean_plan(self):
        plan = self.cleaned_data['plan']
        if plan == 'free':
            raise forms.ValidationError(_('Sie können nicht zum Free-Plan downgraden.'))
        return plan 