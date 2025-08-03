"""
Views für die Users-App
"""
from django.views.generic import (
    TemplateView, CreateView, UpdateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import login, authenticate
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import CustomUser
from .forms import CustomUserCreationForm


class RegisterView(CreateView):
    """
    Conversion-optimierte Benutzerregistrierung mit Verkaufs-Features
    """
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('core:dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Verkaufs-Features für die Registrierung
        context['pricing_plans'] = [
            {
                'name': 'Starter',
                'price': '0',
                'currency': '€',
                'period': 'Monat',
                'features': [
                    '5 Dealrooms',
                    'Basis-Templates',
                    'E-Mail-Support',
                    'Standard-Features'
                ],
                'highlight': False,
                'cta': 'Kostenlos starten'
            },
            {
                'name': 'Professional',
                'price': '29',
                'currency': '€',
                'period': 'Monat',
                'features': [
                    'Unbegrenzte Dealrooms',
                    'Premium-Templates',
                    'Content-Bibliothek',
                    'Priority-Support',
                    'Analytics & Tracking',
                    'Custom Branding'
                ],
                'highlight': True,
                'cta': 'Jetzt upgraden'
            },
            {
                'name': 'Enterprise',
                'price': '99',
                'currency': '€',
                'period': 'Monat',
                'features': [
                    'Alles aus Professional',
                    'White-Label Lösung',
                    'API-Zugang',
                    'Dedicated Support',
                    'Custom Integration',
                    'SLA-Garantie'
                ],
                'highlight': False,
                'cta': 'Enterprise kontaktieren'
            }
        ]
        
        # Social Proof
        context['testimonials'] = [
            {
                'name': 'Sarah Müller',
                'company': 'TechStart GmbH',
                'text': 'Dealroom Dashboard hat unsere Verkaufsprozesse revolutioniert. 40% mehr Abschlüsse!',
                'rating': 5
            },
            {
                'name': 'Michael Weber',
                'company': 'Digital Solutions',
                'text': 'Endlich eine Lösung, die wirklich funktioniert. Kunden sind begeistert!',
                'rating': 5
            },
            {
                'name': 'Lisa Schmidt',
                'company': 'Innovation Labs',
                'text': 'Die beste Investition für unser Sales-Team. ROI in 2 Monaten!',
                'rating': 5
            }
        ]
        
        # Features-Highlights
        context['features'] = [
            {
                'icon': '🚀',
                'title': 'Schnelle Erstellung',
                'description': 'Dealrooms in 2 Minuten statt 2 Stunden'
            },
            {
                'icon': '📈',
                'title': 'Mehr Abschlüsse',
                'description': '40% höhere Conversion-Rate durch professionelle Landingpages'
            },
            {
                'icon': '🎨',
                'title': 'Design-Flexibilität',
                'description': 'Unbegrenzte Anpassungsmöglichkeiten für Ihr Branding'
            },
            {
                'icon': '📊',
                'title': 'Analytics & Tracking',
                'description': 'Vollständige Einblicke in Ihre Deal-Performance'
            }
        ]
        
        return context
    
    def form_valid(self, form):
        # Benutzer speichern und automatisch anmelden
        user = form.save()
        login(self.request, user)
        
        # Conversion-Tracking
        self.request.session['registration_completed'] = True
        self.request.session['user_plan'] = 'starter'
        
        # Upselling-Nachricht
        messages.success(self.request, _('🎉 Registrierung erfolgreich! Willkommen im Dealroom Dashboard.'))
        messages.info(self.request, _('💡 Tipp: Upgrade auf Professional für unbegrenzte Dealrooms und Premium-Features!'))
        
        return HttpResponseRedirect(reverse_lazy('core:dashboard'))


class UpgradeView(LoginRequiredMixin, TemplateView):
    """
    Upgrade-Seite für Upselling
    """
    template_name = 'users/upgrade.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Aktuelle Nutzung
        from deals.models import Deal
        user_deals = Deal.objects.filter(created_by=self.request.user)
        context['current_usage'] = {
            'total_deals': user_deals.count(),
            'active_deals': user_deals.filter(status='active').count(),
            'draft_deals': user_deals.filter(status='draft').count(),
        }
        
        # Upgrade-Optionen
        context['upgrade_options'] = [
            {
                'plan': 'Professional',
                'price': '29',
                'currency': '€',
                'period': 'Monat',
                'benefits': [
                    'Unbegrenzte Dealrooms (aktuell: 5 limitiert)',
                    'Premium-Templates & Layouts',
                    'Content-Bibliothek mit 100+ Vorlagen',
                    'Priority-Support (24h Antwort)',
                    'Analytics & Performance-Tracking',
                    'Custom Branding & White-Label'
                ],
                'cta': 'Jetzt upgraden',
                'popular': True
            },
            {
                'plan': 'Enterprise',
                'price': '99',
                'currency': '€',
                'period': 'Monat',
                'benefits': [
                    'Alles aus Professional',
                    'White-Label Lösung',
                    'API-Zugang für Integrationen',
                    'Dedicated Account Manager',
                    'Custom Integration Support',
                    'SLA-Garantie (99.9% Uptime)'
                ],
                'cta': 'Enterprise kontaktieren',
                'popular': False
            }
        ]
        
        return context


class PricingView(TemplateView):
    """
    Detaillierte Pricing-Seite
    """
    template_name = 'users/pricing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Vollständige Pricing-Matrix
        context['pricing_matrix'] = {
            'plans': [
                {
                    'name': 'Starter',
                    'price': '0',
                    'currency': '€',
                    'period': 'Monat',
                    'description': 'Perfekt für Einsteiger und kleine Teams',
                    'features': {
                        'dealrooms': '5 Dealrooms',
                        'templates': '10 Basis-Templates',
                        'support': 'E-Mail-Support',
                        'analytics': 'Basis-Analytics',
                        'branding': 'Standard-Branding',
                        'api': 'Kein API-Zugang',
                        'white_label': 'Kein White-Label'
                    },
                    'cta': 'Kostenlos starten',
                    'highlight': False
                },
                {
                    'name': 'Professional',
                    'price': '29',
                    'currency': '€',
                    'period': 'Monat',
                    'description': 'Ideal für wachsende Unternehmen',
                    'features': {
                        'dealrooms': 'Unbegrenzte Dealrooms',
                        'templates': '50+ Premium-Templates',
                        'support': 'Priority-Support (24h)',
                        'analytics': 'Vollständige Analytics',
                        'branding': 'Custom Branding',
                        'api': 'API-Zugang',
                        'white_label': 'White-Label Option'
                    },
                    'cta': 'Jetzt upgraden',
                    'highlight': True
                },
                {
                    'name': 'Enterprise',
                    'price': '99',
                    'currency': '€',
                    'period': 'Monat',
                    'description': 'Für große Teams und Unternehmen',
                    'features': {
                        'dealrooms': 'Unbegrenzte Dealrooms',
                        'templates': 'Alle Templates + Custom',
                        'support': 'Dedicated Support',
                        'analytics': 'Advanced Analytics',
                        'branding': 'Full White-Label',
                        'api': 'Unbegrenzter API-Zugang',
                        'white_label': 'Vollständiges White-Label'
                    },
                    'cta': 'Enterprise kontaktieren',
                    'highlight': False
                }
            ]
        }
        
        return context


class CustomLoginView(TemplateView):
    """
    Einfache Login-View die garantiert funktioniert
    """
    template_name = 'users/login.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"🔍 Login-Versuch: {username}")
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            print(f"🔍 Authentifizierung: {user}")
            
            if user is not None:
                login(request, user)
                print(f"✅ Login erfolgreich für: {username}")
                return HttpResponseRedirect('/')
            else:
                print(f"❌ Login fehlgeschlagen für: {username}")
                messages.error(request, 'Benutzername oder Passwort ist falsch.')
        else:
            print(f"❌ Fehlende Daten: username={username}")
            messages.error(request, 'Bitte geben Sie Benutzername und Passwort ein.')
        
        return render(request, self.template_name)


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Benutzerprofil-Ansicht
    """
    template_name = 'users/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """
    Benutzerprofil bearbeiten
    """
    model = CustomUser
    template_name = 'users/profile_edit.html'
    fields = ['first_name', 'last_name', 'email', 'phone', 'company', 'bio', 'avatar']
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, _('Profil erfolgreich aktualisiert.'))
        return super().form_valid(form)
