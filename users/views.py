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
    Benutzerregistrierung ohne E-Mail-Bestätigung
    """
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('core:dashboard')
    
    def form_valid(self, form):
        # Benutzer speichern und automatisch anmelden
        user = form.save()
        login(self.request, user)
        messages.success(self.request, _('Registrierung erfolgreich! Willkommen im Dealroom Dashboard.'))
        return redirect('core:dashboard')


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
                return HttpResponseRedirect('/dashboard/')
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
