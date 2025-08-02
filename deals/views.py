"""
Views für die Dealrooms-App
"""
import csv
import io
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Deal, DealFile, DealFileAssignment
from .forms import DealForm, DealFileForm, ModernDealForm
from files.models import GlobalFile
from .utils import (
    log_deal_creation, log_deal_update, log_status_change,
    log_file_assignment, log_file_unassignment,
    log_website_generation, log_website_deletion
)
from django.utils import timezone
from django.utils import timezone as django_timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .models import Deal, DealFile, DealFileAssignment
from .forms import DealForm
from django.contrib.auth.hashers import check_password
from .models import ContentBlock, MediaLibrary


# Dealroom Views
class QuickSetupView(View):
    """Quick-Setup View für schnelle Dealroom-Erstellung"""
    
    def get(self, request):
        """Zeigt Template-Auswahl"""
        templates = Deal.get_available_templates()
        return render(request, 'deals/quick_setup.html', {
            'templates': templates
        })
    
    def post(self, request):
        """Erstellt Dealroom aus Template"""
        template_name = request.POST.get('template')
        title = request.POST.get('title')
        recipient_name = request.POST.get('recipient_name')
        recipient_email = request.POST.get('recipient_email')
        
        if not all([template_name, title, recipient_name, recipient_email]):
            messages.error(request, 'Bitte füllen Sie alle Pflichtfelder aus.')
            return redirect('deals:quick_setup')
        
        try:
            # Deal aus Template erstellen
            deal = Deal.create_from_template(
                template_name=template_name,
                title=title,
                recipient_name=recipient_name,
                recipient_email=recipient_email,
                created_by=request.user,
                status='active'
            )
            
            messages.success(request, f'Dealroom "{title}" wurde erfolgreich aus Template erstellt!')
            return redirect('admin:deals_deal_change', deal.id)
            
        except Exception as e:
            messages.error(request, f'Fehler beim Erstellen des Dealrooms: {str(e)}')
            return redirect('deals:quick_setup')


class DealListView(LoginRequiredMixin, ListView):
    """
    Liste aller Dealrooms
    """
    model = Deal
    template_name = 'deals/deal_list.html'
    context_object_name = 'deals'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Deal.objects.select_related('created_by').order_by('-created_at')
        
        # Suchfunktion
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(company_name__icontains=search) |
                Q(description__icontains=search) |
                Q(hero_title__icontains=search)
            )
        
        # Filter nach Status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['status_choices'] = Deal.DealStatus.choices
        return context


class DealDetailView(LoginRequiredMixin, DetailView):
    """
    Detailansicht eines Dealrooms
    """
    model = Deal
    template_name = 'deals/deal_detail.html'
    context_object_name = 'deal'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['files'] = self.object.files.all().order_by('-uploaded_at')
        context['hero_image'] = self.object.files.filter(file_type='hero_image', is_primary=True).first()
        context['logo'] = self.object.files.filter(file_type='logo', is_primary=True).first()
        
        # Änderungsprotokoll hinzufügen
        context['change_logs'] = self.object.change_logs.select_related('changed_by').order_by('-changed_at')[:20]
        
        return context


class DealCreateView(LoginRequiredMixin, CreateView):
    """
    Neuen Dealroom erstellen
    """
    model = Deal
    form_class = DealForm
    template_name = 'deals/deal_form.html'
    success_url = reverse_lazy('core:dashboard')
    
    @transaction.atomic
    def form_valid(self, form):
        """Speichert den Dealroom mit atomarer Transaktion"""
        try:
            # Zusätzliche Validierung für parallele Konflikte
            title = form.cleaned_data.get('title')
            slug = form.cleaned_data.get('slug')
            
            # Prüfe ob Titel/Slug bereits existiert (mit SELECT FOR UPDATE)
            if Deal.objects.select_for_update().filter(title=title).exists():
                form.add_error('title', 'Ein Dealroom mit diesem Titel existiert bereits.')
                return self.form_invalid(form)
            
            if Deal.objects.select_for_update().filter(slug=slug).exists():
                form.add_error('slug', 'Ein Dealroom mit diesem Slug existiert bereits.')
                return self.form_invalid(form)
            
            # Dealroom erstellen
            dealroom = form.save(commit=False)
            dealroom.created_by = self.request.user
            dealroom.save()
            
            # Dateien verarbeiten
            self._process_files(dealroom)
            
            messages.success(
                self.request,
                f"Dealroom '{dealroom.title}' erfolgreich erstellt."
            )
            
            return super().form_valid(form)
            
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(None, f"Fehler beim Erstellen des Dealrooms: {str(e)}")
            return self.form_invalid(form)
    
    def _process_files(self, dealroom):
        """Verarbeitet Dateien (Logo, Globale Dateien, Direkte Uploads)"""
        logo_file = self.request.FILES.get('logo_upload')
        if logo_file:
            deal_file = DealFile.objects.create(
                deal=dealroom,
                title=f"Logo - {dealroom.title}",
                description="Logo für diesen Dealroom",
                file=logo_file,
                file_type='logo',
                uploaded_by=self.request.user,
                is_primary=True
            )
        
        # Globale Datei zuordnen
        global_file_id = self.request.POST.get('global_file_select')
        if global_file_id:
            try:
                global_file = GlobalFile.objects.get(id=global_file_id)
                DealFileAssignment.objects.create(
                    deal=dealroom,
                    global_file=global_file,
                    role='other',
                    assigned_by=self.request.user
                )
            except GlobalFile.DoesNotExist:
                pass
        
        # Direkte Datei-Upload verarbeiten
        uploaded_file = self.request.FILES.get('file_upload')
        if uploaded_file:
            file_title = self.request.POST.get('file_title', 'Hochgeladene Datei')
            file_description = self.request.POST.get('file_description', '')
            file_type = self.request.POST.get('file_type', 'other')
            
            DealFile.objects.create(
                deal=dealroom,
                title=file_title,
                description=file_description,
                file=uploaded_file,
                file_type=file_type,
                uploaded_by=self.request.user
            )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Globale Dateien für die Auswahl hinzufügen
        context['global_files'] = GlobalFile.objects.filter(is_public=True).order_by('-uploaded_at')[:20]
        return context


class DealBatchCreateView(LoginRequiredMixin, TemplateView):
    """
    Batch-Erstellung von Dealrooms via CSV-Upload
    """
    template_name = 'deals/deal_batch_create.html'
    
    def post(self, request, *args, **kwargs):
        if 'csv_file' not in request.FILES:
            messages.error(request, _('Bitte wählen Sie eine CSV-Datei aus.'))
            return self.get(request, *args, **kwargs)
        
        csv_file = request.FILES['csv_file']
        
        # CSV-Datei validieren
        if not csv_file.name.endswith('.csv'):
            messages.error(request, _('Bitte laden Sie eine gültige CSV-Datei hoch.'))
            return self.get(request, *args, **kwargs)
        
        try:
            # CSV einlesen
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            
            created_count = 0
            error_count = 0
            errors = []
            
            with transaction.atomic():
                for row_num, row in enumerate(csv_data, start=2):  # Start bei 2 (Header ist Zeile 1)
                    try:
                        # Pflichtfelder prüfen
                        if not row.get('title') or not row.get('slug') or not row.get('recipient_email'):
                            errors.append(f"Zeile {row_num}: Titel, Slug und Empfänger-E-Mail sind Pflichtfelder")
                            error_count += 1
                            continue
                        
                        # Deal erstellen
                        deal = Deal.objects.create(
                            title=row.get('title', '').strip(),
                            slug=row.get('slug', '').strip(),
                            description=row.get('description', '').strip(),
                            recipient_name=row.get('recipient_name', '').strip(),
                            recipient_email=row.get('recipient_email', '').strip(),
                            status=row.get('status', 'active'),
                            template_type=row.get('template_type', 'modern'),
                            hero_title=row.get('hero_title', '').strip(),
                            hero_subtitle=row.get('hero_subtitle', '').strip(),
                            call_to_action=row.get('call_to_action', '').strip(),
                            primary_color=row.get('primary_color', '#007bff'),
                            secondary_color=row.get('secondary_color', '#6c757d'),
                            created_by=request.user
                        )
                        created_count += 1
                        
                    except Exception as e:
                        errors.append(f"Zeile {row_num}: {str(e)}")
                        error_count += 1
            
            # Erfolgsmeldung
            if created_count > 0:
                messages.success(request, _('{} Dealrooms erfolgreich erstellt.').format(created_count))
            
            if error_count > 0:
                messages.warning(request, _('{} Fehler aufgetreten. Bitte überprüfen Sie die CSV-Datei.').format(error_count))
                # Fehler in Session speichern für Anzeige
                request.session['batch_errors'] = errors[:10]  # Max 10 Fehler anzeigen
            
            return redirect('dealrooms:dealroom_list')
            
        except Exception as e:
            messages.error(request, _('Fehler beim Verarbeiten der CSV-Datei: {}').format(str(e)))
            return self.get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['batch_errors'] = self.request.session.get('batch_errors', [])
        # Fehler aus Session löschen
        if 'batch_errors' in self.request.session:
            del self.request.session['batch_errors']
        return context


class DealUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Dealroom bearbeiten
    """
    model = Deal
    form_class = DealForm
    template_name = 'deals/deal_form.html'
    
    def test_func(self):
        deal = self.get_object()
        return self.request.user.can_edit_deals() or deal.created_by == self.request.user
    
    @transaction.atomic
    def form_valid(self, form):
        """Speichert den Dealroom mit atomarer Transaktion"""
        try:
            # Zusätzliche Validierung für parallele Konflikte
            title = form.cleaned_data.get('title')
            slug = form.cleaned_data.get('slug')
            
            # Prüfe ob Titel/Slug bereits existiert (außer diesem Dealroom)
            if Deal.objects.select_for_update().filter(title=title).exclude(pk=self.object.pk).exists():
                form.add_error('title', 'Ein Dealroom mit diesem Titel existiert bereits.')
                return self.form_invalid(form)
            
            if Deal.objects.select_for_update().filter(slug=slug).exclude(pk=self.object.pk).exists():
                form.add_error('slug', 'Ein Dealroom mit diesem Slug existiert bereits.')
                return self.form_invalid(form)
            
            # Dealroom aktualisieren
            dealroom = form.save(commit=False)
            dealroom.updated_by = self.request.user
            dealroom.save()
            
            # Dateien verarbeiten
            self._process_files(dealroom)
            
            messages.success(
                self.request,
                f"Dealroom '{dealroom.title}' erfolgreich aktualisiert."
            )
            
            return super().form_valid(form)
            
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(None, f"Fehler beim Aktualisieren des Dealrooms: {str(e)}")
            return self.form_invalid(form)
    
    def _process_files(self, dealroom):
        """Verarbeitet Dateien (Logo, Globale Dateien, Direkte Uploads)"""
        logo_file = self.request.FILES.get('logo_upload')
        if logo_file:
            deal_file = DealFile.objects.create(
                deal=dealroom,
                title=f"Logo - {dealroom.title}",
                description="Logo für diesen Dealroom",
                file=logo_file,
                file_type='logo',
                uploaded_by=self.request.user,
                is_primary=True
            )
        
        # Globale Datei zuordnen
        global_file_id = self.request.POST.get('global_file_select')
        if global_file_id:
            try:
                global_file = GlobalFile.objects.get(id=global_file_id)
                # Prüfen ob bereits zugeordnet
                existing_assignment = DealFileAssignment.objects.filter(
                    deal=self.object,
                    global_file=global_file
                ).first()
                
                if not existing_assignment:
                    DealFileAssignment.objects.create(
                        deal=self.object,
                        global_file=global_file,
                        role='other',
                        assigned_by=self.request.user
                    )
            except GlobalFile.DoesNotExist:
                pass
        
        # Direkte Datei-Upload verarbeiten
        uploaded_file = self.request.FILES.get('file_upload')
        if uploaded_file:
            file_title = self.request.POST.get('file_title', 'Hochgeladene Datei')
            file_description = self.request.POST.get('file_description', '')
            file_type = self.request.POST.get('file_type', 'other')
            
            DealFile.objects.create(
                deal=self.object,
                title=file_title,
                description=file_description,
                file=uploaded_file,
                file_type=file_type,
                uploaded_by=self.request.user
            )
        
        messages.success(self.request, f'Dealroom "{self.object.title}" wurde erfolgreich aktualisiert.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Globale Dateien für die Auswahl hinzufügen
        context['global_files'] = GlobalFile.objects.filter(is_public=True).order_by('-uploaded_at')[:20]
        return context


class DealDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Dealroom löschen
    """
    model = Deal
    template_name = 'deals/deal_confirm_delete.html'
    success_url = reverse_lazy('dealrooms:dealroom_list')
    
    def test_func(self):
        return self.request.user.can_edit_deals()
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Dealroom erfolgreich gelöscht.'))
        return super().delete(request, *args, **kwargs)


# DealFile Views
class DealFileListView(LoginRequiredMixin, ListView):
    """
    Liste aller Dateien eines Deals
    """
    model = DealFile
    template_name = 'deals/deal_file_list.html'
    context_object_name = 'files'
    paginate_by = 20
    
    def get_queryset(self):
        self.deal = get_object_or_404(Deal, pk=self.kwargs['deal_pk'])
        return self.deal.files.all().order_by('-uploaded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deal'] = self.deal
        return context


class DealFileUploadView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Datei für einen Deal hochladen
    """
    model = DealFile
    form_class = DealFileForm
    template_name = 'deals/deal_file_upload.html'
    
    def test_func(self):
        return self.request.user.can_edit_deals()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deal'] = get_object_or_404(Deal, pk=self.kwargs['deal_pk'])
        
        # Globale Dateien für die Sidebar hinzufügen
        from files.models import GlobalFile
        context['global_files'] = GlobalFile.objects.filter(is_public=True).order_by('-uploaded_at')[:10]
        
        return context
    
    def form_valid(self, form):
        form.instance.deal = get_object_or_404(Deal, pk=self.kwargs['deal_pk'])
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, _('Datei erfolgreich hochgeladen.'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('dealrooms:dealroom_files', kwargs={'deal_pk': self.kwargs['deal_pk']})


class DealFileDetailView(LoginRequiredMixin, DetailView):
    """
    Detailansicht einer Datei
    """
    model = DealFile
    template_name = 'deals/deal_file_detail.html'
    context_object_name = 'file'


class DealFileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Datei bearbeiten
    """
    model = DealFile
    form_class = DealFileForm
    template_name = 'deals/deal_file_form.html'
    
    def test_func(self):
        return self.request.user.can_edit_deals()
    
    def get_success_url(self):
        return reverse_lazy('dealrooms:dealroom_file_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _('Datei erfolgreich aktualisiert.'))
        return super().form_valid(form)


class DealFileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Datei löschen
    """
    model = DealFile
    template_name = 'deals/deal_file_confirm_delete.html'
    
    def test_func(self):
        return self.request.user.can_edit_deals()
    
    def get_success_url(self):
        return reverse_lazy('dealrooms:dealroom_files', kwargs={'deal_pk': self.object.deal.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Datei erfolgreich gelöscht.'))
        return super().delete(request, *args, **kwargs)


class DealFileDownloadView(LoginRequiredMixin, DetailView):
    """
    Datei herunterladen
    """
    model = DealFile
    
    def get(self, request, *args, **kwargs):
        file_obj = self.get_object()
        
        if not file_obj.file:
            raise Http404(_('Datei nicht gefunden.'))
        
        response = HttpResponse(file_obj.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_obj.file.name}"'
        return response


class WebsitePreviewView(LoginRequiredMixin, View):
    """
    View für die Vorschau der generierten Website
    
    Leitet zur generierten Website weiter oder zeigt eine Nachricht
    wenn die Website noch nicht generiert wurde.
    """
    
    def get(self, request, pk):
        """Zeigt Vorschau der generierten Website"""
        
        try:
            dealroom = Deal.objects.get(pk=pk)
            
            # Prüfen ob Website generiert ist
            if dealroom.website_status == 'generated' and dealroom.local_website_url:
                # Zur generierten Website weiterleiten
                return HttpResponseRedirect(dealroom.local_website_url)
            
            elif dealroom.website_status == 'generating':
                messages.warning(
                    request, 
                    f"Website für '{dealroom.title}' wird gerade generiert. "
                    "Bitte warten Sie einen Moment und versuchen Sie es erneut."
                )
            
            elif dealroom.website_status == 'failed':
                messages.error(
                    request,
                    f"Website-Generierung für '{dealroom.title}' fehlgeschlagen. "
                    f"Fehler: {dealroom.generation_error}"
                )
            
            else:
                messages.info(
                    request,
                    f"Website für '{dealroom.title}' wurde noch nicht generiert. "
                    "Die Website wird automatisch generiert wenn der Dealroom aktiviert wird."
                )
            
            # Zurück zur Dealroom-Detail-Seite
            return HttpResponseRedirect(reverse('dealrooms:dealroom_detail', kwargs={'pk': pk}))
            
        except Deal.DoesNotExist:
            messages.error(request, "Dealroom nicht gefunden.")
            return HttpResponseRedirect(reverse('dealrooms:dealroom_list'))


class RegenerateWebsiteView(LoginRequiredMixin, View):
    """
    View für manuelle Website-Regenerierung
    
    Regeneriert die Website für einen Dealroom manuell.
    """
    
    def post(self, request, pk):
        """Regeneriert Website für einen Dealroom"""
        
        try:
            dealroom = Deal.objects.get(pk=pk)
            
            # Generator initialisieren
            from generator.renderer import DealroomGenerator
            import os
            from django.conf import settings
            
            generator = DealroomGenerator(dealroom)
            
            # Website-Verzeichnis erstellen
            output_dir = os.path.join(settings.BASE_DIR, 'generated_pages', f'dealroom-{dealroom.id}')
            output_path = os.path.join(output_dir, 'index.html')
            
            # Website speichern
            success = generator.save_website(output_path)
            
            if success:
                # URL im Model speichern
                website_url = f"/generated_pages/dealroom-{dealroom.id}/"
                dealroom.local_website_url = website_url
                dealroom.website_status = 'generated'
                dealroom.last_generation = timezone.now()
                dealroom.generation_error = None
                dealroom.save(update_fields=['local_website_url', 'website_status', 'last_generation', 'generation_error'])
                
                # Änderung protokollieren
                log_website_generation(dealroom, request.user)
                
                messages.success(
                    request,
                    f"Website für '{dealroom.title}' erfolgreich regeneriert: {website_url}"
                )
            else:
                dealroom.website_status = 'failed'
                dealroom.generation_error = 'Fehler beim Speichern der Website'
                dealroom.save(update_fields=['website_status', 'generation_error'])
                
                messages.error(
                    request,
                    f"Fehler beim Speichern der Website für '{dealroom.title}'"
                )
            
        except Deal.DoesNotExist:
            messages.error(request, "Dealroom nicht gefunden.")
        except Exception as e:
            messages.error(
                request,
                f"Fehler bei Website-Regenerierung: {str(e)}"
            )
        
        # Zurück zur vorherigen Seite
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('dealrooms:dealroom_list')))


class DeleteWebsiteView(LoginRequiredMixin, View):
    """
    View für manuelle Website-Löschung
    
    Löscht die generierte Website für einen Dealroom.
    """
    
    def post(self, request, pk):
        """Löscht Website für einen Dealroom"""
        
        try:
            dealroom = Deal.objects.get(pk=pk)
            
            # Generator initialisieren
            from generator.renderer import DealroomGenerator
            generator = DealroomGenerator(dealroom)
            
            # Website löschen
            generator.delete_website()
            
            # Status zurücksetzen
            dealroom.website_status = 'not_generated'
            dealroom.local_website_url = None
            dealroom.generation_error = None
            dealroom.save(update_fields=['website_status', 'local_website_url', 'generation_error'])
            
            # Änderung protokollieren
            log_website_deletion(dealroom, request.user)
            
            messages.success(
                request,
                f"Website für '{dealroom.title}' erfolgreich gelöscht."
            )
            
        except Deal.DoesNotExist:
            messages.error(request, "Dealroom nicht gefunden.")
        except Exception as e:
            messages.error(
                request,
                f"Fehler bei Website-Löschung: {str(e)}"
            )
        
        # Zurück zur vorherigen Seite
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('dealrooms:dealroom_list')))


class DealFileAssignmentView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Datei zu Dealroom zuordnen
    """
    
    def test_func(self):
        deal = get_object_or_404(Deal, pk=self.kwargs['pk'])
        return self.request.user.can_edit_deals()
    
    def post(self, request, pk):
        deal = get_object_or_404(Deal, pk=pk)
        global_file_id = request.POST.get('global_file_id')
        role = request.POST.get('role', 'other')
        
        try:
            global_file = GlobalFile.objects.get(pk=global_file_id)
            
            # Prüfen ob Zuordnung bereits existiert
            assignment, created = DealFileAssignment.objects.get_or_create(
                deal=deal,
                global_file=global_file,
                defaults={
                    'assigned_by': request.user,
                    'role': role,
                    'order': deal.file_assignments.count()
                }
            )
            
            if created:
                messages.success(request, _('Datei erfolgreich zugeordnet.'))
                # Änderung protokollieren
                log_file_assignment(deal, request.user, global_file.title, role)
            else:
                # Rolle aktualisieren
                old_role = assignment.role
                assignment.role = role
                assignment.save()
                messages.success(request, _('Datei-Rolle aktualisiert.'))
                # Änderung protokollieren
                log_deal_update(deal, request.user, field_name='file_role', 
                              old_value=f"{global_file.title} ({old_role})", 
                              new_value=f"{global_file.title} ({role})")
            
        except GlobalFile.DoesNotExist:
            messages.error(request, _('Datei nicht gefunden.'))
        except Exception as e:
            messages.error(request, _('Fehler beim Zuordnen der Datei: {}').format(str(e)))
        
        return redirect('dealrooms:dealroom_detail', pk=pk)


class DealFileUnassignmentView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Datei von Dealroom entfernen
    """
    
    def test_func(self):
        deal = get_object_or_404(Deal, pk=self.kwargs['pk'])
        return self.request.user.can_edit_deals()
    
    def post(self, request, pk):
        deal = get_object_or_404(Deal, pk=pk)
        assignment_id = request.POST.get('assignment_id')
        
        try:
            assignment = get_object_or_404(DealFileAssignment, pk=assignment_id, deal=deal)
            
            # Änderung protokollieren
            log_file_unassignment(deal, request.user, assignment.global_file.title, assignment.role)
            
            assignment.delete()
            messages.success(request, _('Datei erfolgreich entfernt.'))
            
        except Exception as e:
            messages.error(request, _('Fehler beim Entfernen der Datei: {}').format(str(e)))
        
        return redirect('dealrooms:dealroom_detail', pk=pk)


class DealFileAssignmentListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Liste der zugeordneten Dateien für einen Dealroom
    """
    template_name = 'deals/deal_file_assignment_list.html'
    
    def test_func(self):
        deal = get_object_or_404(Deal, pk=self.kwargs['pk'])
        return self.request.user.can_edit_deals()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deal = get_object_or_404(Deal, pk=self.kwargs['pk'])
        
        context['deal'] = deal
        context['assignments'] = deal.file_assignments.select_related('global_file', 'assigned_by').order_by('order')
        context['available_files'] = GlobalFile.objects.filter(is_public=True).exclude(
            deal_assignments__deal=deal
        ).order_by('-uploaded_at')
        
        return context


class PasswordProtectionView(View):
    """Passwortschutz-View für Landingpages"""
    
    def get(self, request, deal_id):
        """Zeigt die Passwortabfrage"""
        deal = get_object_or_404(Deal, id=deal_id)
        
        # Prüfe ob Passwortschutz aktiviert ist
        if not deal.password_protection_enabled:
            return redirect('deals:landingpage', deal_id=deal.id)
        
        # Prüfe ob bereits authentifiziert
        if request.session.get(f'deal_{deal.id}_authenticated'):
            return redirect('deals:landingpage', deal_id=deal.id)
        
        # Prüfe ob gesperrt
        if deal.is_blocked():
            remaining_time = deal.get_block_remaining_time()
            return render(request, 'deals/password_protection_blocked.html', {
                'deal': deal,
                'remaining_time': remaining_time
            })
        
        return render(request, 'deals/password_protection.html', {
            'deal': deal,
            'remaining_attempts': deal.get_remaining_attempts()
        })
    
    def post(self, request, deal_id):
        """Verarbeitet die Passwortabfrage"""
        deal = get_object_or_404(Deal, id=deal_id)
        
        # Prüfe ob Passwortschutz aktiviert ist
        if not deal.password_protection_enabled:
            return redirect('deals:landingpage', deal_id=deal.id)
        
        password = request.POST.get('password', '')
        ip_address = self._get_client_ip(request)
        
        # Prüfe Passwort
        if deal.check_password(password):
            # Erfolgreich - Session setzen
            request.session[f'deal_{deal.id}_authenticated'] = True
            request.session[f'deal_{deal.id}_authenticated_at'] = timezone.now().isoformat()
            
            # Log erfolgreichen Versuch
            deal.log_password_attempt(True, ip_address)
            
            return redirect('deals:landingpage', deal_id=deal.id)
        else:
            # Fehlgeschlagen
            deal.log_password_attempt(False, ip_address)
            
            messages.error(request, 'Falsches Passwort. Bitte versuchen Sie es erneut.')
            return redirect('deals:password_protection', deal_id=deal.id)
    
    def _get_client_ip(self, request):
        """Ermittelt die IP-Adresse des Clients"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LandingpageView(View):
    """Landingpage-View mit Passwortschutz"""
    
    def get(self, request, deal_id):
        """Zeigt die Landingpage"""
        deal = get_object_or_404(Deal, id=deal_id)
        
        # Prüfe Passwortschutz
        if deal.password_protection_enabled:
            if not request.session.get(f'deal_{deal.id}_authenticated'):
                return redirect('deals:password_protection', deal_id=deal.id)
        
        # Generiere HTML
        try:
            from generator.renderer import DealroomGenerator
            generator = DealroomGenerator(deal)
            html_content = generator.generate_website()
            
            # Tracking
            deal.last_accessed = timezone.now()
            deal.access_count += 1
            deal.save()
            
            return HttpResponse(html_content, content_type='text/html')
            
        except Exception as e:
            return HttpResponse(f'<html><body><h1>Fehler</h1><p>{str(e)}</p></body></html>')


class PasswordProtectionAdminView(View):
    """Admin-View für Passwortschutz-Einstellungen"""
    def get(self, request, deal_id):
        deal = get_object_or_404(Deal, id=deal_id)
        return render(request, 'deals/password_protection_admin.html', {'deal': deal})
    
    def post(self, request, deal_id):
        deal = get_object_or_404(Deal, id=deal_id)
        action = request.POST.get('action')
        
        if action == 'enable':
            password = request.POST.get('password')
            message = request.POST.get('message', '')
            if password:
                deal.set_password_protection(password, message)
                messages.success(request, 'Passwortschutz wurde aktiviert!')
        
        elif action == 'disable':
            deal.disable_password_protection()
            messages.success(request, 'Passwortschutz wurde deaktiviert!')
        
        elif action == 'change_password':
            new_password = request.POST.get('new_password')
            if new_password:
                deal.set_password_protection(new_password, deal.password_protection_message)
                messages.success(request, 'Passwort wurde geändert!')
        
        return redirect('deals:password_protection_admin', deal_id=deal_id)


# Content-Management Views
class LandingpageBuilderView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Landingpage-Builder - Weiterleitung zum GrapesJS Editor"""
    
    def test_func(self):
        """Prüft ob User Zugriff auf den Dealroom hat"""
        deal = get_object_or_404(Deal, pk=self.kwargs['deal_id'])
        return self.request.user == deal.created_by or self.request.user.is_staff
    
    def get(self, request, deal_id):
        """Weiterleitung zum GrapesJS Editor"""
        return redirect('deals:grapesjs_editor', deal_id=deal_id)


class ContentLibraryView(View):
    """Content-Bibliothek Übersicht - nur für Designer verfügbar"""
    def get(self, request):
        from .models import ContentBlock, MediaLibrary
        
        content_blocks = ContentBlock.objects.all().order_by('category', 'title')
        media_library = MediaLibrary.objects.all().order_by('category', 'title')
        
        context = {
            'content_blocks': content_blocks,
            'media_library': media_library,
            'active_tab': request.GET.get('tab', 'content')
        }
        
        return render(request, 'deals/content_library.html', context)








class DuplicateDealView(View):
    """Dealroom duplizieren"""
    def get(self, request, deal_id):
        deal = get_object_or_404(Deal, id=deal_id)
        return render(request, 'deals/duplicate_deal.html', {'deal': deal})
    
    def post(self, request, deal_id):
        deal = get_object_or_404(Deal, id=deal_id)
        
        # Form-Daten verarbeiten
        new_title = request.POST.get('new_title')
        new_slug = request.POST.get('new_slug')
        include_files = request.POST.get('include_files') == 'on'
        include_content = request.POST.get('include_content') == 'on'
        reset_status = request.POST.get('reset_status') == 'on'
        reset_progress = request.POST.get('reset_progress') == 'on'
        reset_password_protection = request.POST.get('reset_password_protection') == 'on'
        
        try:
            # Deal duplizieren
            new_deal = deal.duplicate(
                new_title=new_title,
                new_slug=new_slug,
                include_files=include_files,
                include_content=include_content
            )
            
            # Zusätzliche Resets anwenden
            if reset_status:
                new_deal.status = 'draft'
            if reset_progress:
                new_deal.deal_progress = 0
            if reset_password_protection:
                new_deal.password_protection_enabled = False
                new_deal.password_protection_password = None
            
            new_deal.save()
            
            messages.success(request, f'Dealroom "{new_deal.title}" wurde erfolgreich dupliziert!')
            return redirect('admin:deals_deal_change', new_deal.id)
            
        except Exception as e:
            messages.error(request, f'Fehler beim Duplizieren: {str(e)}')
            return render(request, 'deals/duplicate_deal.html', {'deal': deal})


class HTMLEditorView(View):
    """HTML-Editor View für manuelle Bearbeitung der Landingpages"""
    
    def get(self, request, deal_id):
        """Zeigt den HTML-Editor"""
        deal = get_object_or_404(Deal, id=deal_id)
        
        # Aktuellen HTML-Code laden
        current_html = self._get_current_html(deal)
        
        return render(request, 'deals/html_editor.html', {
            'deal': deal,
            'current_html': current_html,
            'editor_modes': Deal.html_editor_mode.field.choices,
        })
    
    def post(self, request, deal_id):
        """Speichert die HTML-Änderungen"""
        deal = get_object_or_404(Deal, id=deal_id)
        
        try:
            # HTML-Editor-Modus
            deal.html_editor_mode = request.POST.get('html_editor_mode', 'auto')
            
            # Custom HTML-Felder
            deal.custom_html_header = request.POST.get('custom_html_header', '')
            deal.custom_html_body_start = request.POST.get('custom_html_body_start', '')
            deal.custom_html_content = request.POST.get('custom_html_content', '')
            deal.custom_html_body_end = request.POST.get('custom_html_body_end', '')
            deal.custom_css = request.POST.get('custom_css', '')
            deal.custom_javascript = request.POST.get('custom_javascript', '')
            
            # Tracking
            deal.last_html_edit = timezone.now()
            deal.html_edit_count += 1
            
            deal.save()
            
            # Website regenerieren
            self._regenerate_website(deal)
            
            messages.success(request, f'HTML-Code für "{deal.title}" wurde erfolgreich gespeichert und die Website wurde regeneriert!')
            return redirect('deals:html_editor', deal_id=deal.id)
            
        except Exception as e:
            messages.error(request, f'Fehler beim Speichern: {str(e)}')
            return redirect('deals:html_editor', deal_id=deal.id)
    
    def _get_current_html(self, deal):
        """Lädt den aktuellen HTML-Code der Website"""
        try:
            if deal.local_website_url:
                import os
                file_path = os.path.join('generated_pages', f'dealroom-{deal.id}', 'index.html')
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
        except Exception as e:
            print(f"Fehler beim Laden des HTML-Codes: {e}")
        
        return ""
    
    def _regenerate_website(self, deal):
        """Regeneriert die Website mit den neuen HTML-Einstellungen"""
        try:
            from .views import RegenerateWebsiteView
            view = RegenerateWebsiteView()
            view.regenerate_website(deal)
        except Exception as e:
            print(f"Fehler beim Regenerieren der Website: {e}")


class HTMLPreviewView(View):
    """HTML-Preview View für Live-Vorschau"""
    
    def get(self, request, deal_id):
        """Zeigt eine Live-Vorschau der Website"""
        deal = get_object_or_404(Deal, id=deal_id)
        
        # Generiere HTML für Vorschau
        preview_html = self._generate_preview_html(deal)
        
        return HttpResponse(preview_html, content_type='text/html')
    
    def _generate_preview_html(self, deal):
        """Generiert HTML für die Live-Vorschau"""
        try:
            from generator.renderer import DealroomGenerator
            generator = DealroomGenerator(deal)
            return generator.generate_website()
        except Exception as e:
            return f"<html><body><h1>Vorschau-Fehler</h1><p>{str(e)}</p></body></html>"


@method_decorator(csrf_exempt, name='dispatch')
class HTMLCodeView(View):
    """API-View für HTML-Code-Operationen"""
    
    def get(self, request, deal_id):
        """Gibt den aktuellen HTML-Code zurück"""
        deal = get_object_or_404(Deal, id=deal_id)
        
        html_data = {
            'custom_html_header': deal.custom_html_header or '',
            'custom_html_body_start': deal.custom_html_body_start or '',
            'custom_html_content': deal.custom_html_content or '',
            'custom_html_body_end': deal.custom_html_body_end or '',
            'custom_css': deal.custom_css or '',
            'custom_javascript': deal.custom_javascript or '',
            'html_editor_mode': deal.html_editor_mode,
            'current_html': self._get_current_html(deal),
        }
        
        return JsonResponse(html_data)
    
    def post(self, request, deal_id):
        """Speichert HTML-Code über API"""
        deal = get_object_or_404(Deal, id=deal_id)
        
        try:
            data = json.loads(request.body)
            
            # HTML-Felder aktualisieren
            deal.custom_html_header = data.get('custom_html_header', '')
            deal.custom_html_body_start = data.get('custom_html_body_start', '')
            deal.custom_html_content = data.get('custom_html_content', '')
            deal.custom_html_body_end = data.get('custom_html_body_end', '')
            deal.custom_css = data.get('custom_css', '')
            deal.custom_javascript = data.get('custom_javascript', '')
            deal.html_editor_mode = data.get('html_editor_mode', 'auto')
            
            # Tracking
            deal.last_html_edit = timezone.now()
            deal.html_edit_count += 1
            
            deal.save()
            
            # Website regenerieren
            self._regenerate_website(deal)
            
            return JsonResponse({'success': True, 'message': 'HTML-Code gespeichert'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    def _get_current_html(self, deal):
        """Lädt den aktuellen HTML-Code"""
        try:
            if deal.local_website_url:
                import os
                file_path = os.path.join('generated_pages', f'dealroom-{deal.id}', 'index.html')
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
        except Exception:
            pass
        return ""
    
    def _regenerate_website(self, deal):
        """Regeneriert die Website"""
        try:
            from .views import RegenerateWebsiteView
            view = RegenerateWebsiteView()
            view.regenerate_website(deal)
        except Exception as e:
            print(f"Fehler beim Regenerieren: {e}")


class ModernDealCreateView(LoginRequiredMixin, CreateView):
    """
    Moderne Dealroom-Erstellung mit Designer-Integration
    """
    model = Deal
    form_class = ModernDealForm
    template_name = 'deals/modern_deal_form.html'
    
    def get_success_url(self):
        return reverse('deals:landingpage_builder', args=[self.object.pk])
    
    @transaction.atomic
    def form_valid(self, form):
        """Dealroom erstellen und direkt zum Designer weiterleiten"""
        dealroom = form.save(commit=False)
        dealroom.created_by = self.request.user
        dealroom.status = 'draft'  # Start als Draft
        dealroom.save()
        
        # Log erstellen
        log_deal_creation(dealroom, self.request.user)
        
        messages.success(
            self.request, 
            f'Dealroom "{dealroom.title}" wurde erstellt! Sie werden jetzt zum Designer weitergeleitet.'
        )
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['templates'] = Deal.get_available_templates()
        return context


class GrapesJSView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    GrapesJS Editor für Dealroom-Design
    """
    
    def test_func(self):
        """Prüft ob User Zugriff auf den Dealroom hat"""
        deal = get_object_or_404(Deal, pk=self.kwargs['deal_id'])
        return self.request.user == deal.created_by or self.request.user.is_staff
    
    def get(self, request, deal_id):
        """Zeigt GrapesJS Editor"""
        deal = get_object_or_404(Deal, pk=deal_id)
        
        # Initial HTML für GrapesJS
        initial_html = self._get_initial_html(deal)
        
        return render(request, 'deals/grapesjs_editor.html', {
            'deal': deal,
            'initial_html': initial_html,
        })
    
    def post(self, request, deal_id):
        """Speichert HTML von GrapesJS"""
        deal = get_object_or_404(Deal, pk=deal_id)
        
        try:
            data = json.loads(request.body)
            html_content = data.get('html', '')
            css_content = data.get('css', '')
            
            # Speichere in Deal-Model
            deal.custom_html_content = html_content
            deal.custom_css = css_content
            deal.html_editor_mode = 'manual'
            deal.last_html_edit = timezone.now()
            deal.html_edit_count += 1
            deal.save()
            
            # Log erstellen
            log_deal_update(deal, request.user, 'HTML über GrapesJS bearbeitet')
            
            return JsonResponse({'success': True, 'message': 'HTML erfolgreich gespeichert'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    def _get_initial_html(self, deal):
        """Generiert initiales HTML für GrapesJS"""
        if deal.custom_html_content:
            return deal.custom_html_content
        
        # Fallback HTML basierend auf Template
        template_html = self._get_template_html(deal)
        return template_html
    
    def _get_template_html(self, deal):
        """Generiert HTML basierend auf Template-Typ"""
        base_html = f"""
        <div class="dealroom-container" style="font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px;">
            <header class="hero-section" style="background: linear-gradient(135deg, {deal.primary_color}, {deal.secondary_color}); color: white; padding: 60px 20px; text-align: center; border-radius: 10px; margin-bottom: 40px;">
                <h1 style="font-size: 2.5em; margin-bottom: 20px;">{deal.title}</h1>
                <p style="font-size: 1.2em; opacity: 0.9;">Willkommen zu Ihrem Dealroom</p>
            </header>
            
            <section class="deal-info" style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px;">
                <h2 style="color: {deal.primary_color}; margin-bottom: 20px;">Deal-Übersicht</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                    <div class="info-card" style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                        <h3 style="margin-bottom: 10px;">Empfänger</h3>
                        <p>{deal.recipient_name or 'Nicht angegeben'}</p>
                    </div>
                    <div class="info-card" style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                        <h3 style="margin-bottom: 10px;">Status</h3>
                        <p>{deal.get_status_display()}</p>
                    </div>
                    <div class="info-card" style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                        <h3 style="margin-bottom: 10px;">Firma</h3>
                        <p>{deal.company_name or 'Nicht angegeben'}</p>
                    </div>
                </div>
            </section>
            
            <section class="description" style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px;">
                <h2 style="color: {deal.primary_color}; margin-bottom: 20px;">Beschreibung</h2>
                <p style="line-height: 1.6;">{deal.description or 'Keine Beschreibung verfügbar'}</p>
            </section>
            
            <footer style="text-align: center; padding: 20px; color: #666; border-top: 1px solid #eee;">
                <p>Erstellt mit DealShare</p>
            </footer>
        </div>
        """
        
        return base_html


class GrapesJSAssetUploadView(LoginRequiredMixin, View):
    """
    API View für GrapesJS Asset-Upload
    """
    
    def post(self, request):
        """Handhabt Asset-Upload für GrapesJS"""
        try:
            uploaded_file = request.FILES.get('files')
            if not uploaded_file:
                return JsonResponse({'error': 'Keine Datei gefunden'}, status=400)
            
            # Erstelle MediaLibrary Eintrag
            media_item = MediaLibrary.objects.create(
                title=uploaded_file.name,
                media_type=self._get_media_type(uploaded_file.name),
                file=uploaded_file,
                created_by=request.user,
                description=f'Uploaded via GrapesJS: {uploaded_file.name}'
            )
            
            # URL für GrapesJS zurückgeben
            file_url = request.build_absolute_uri(media_item.file.url)
            
            return JsonResponse({
                'success': True,
                'data': [{
                    'src': file_url,
                    'name': uploaded_file.name,
                    'type': self._get_media_type(uploaded_file.name)
                }]
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def _get_media_type(self, filename):
        """Bestimmt Media-Type basierend auf Dateiendung"""
        ext = filename.lower().split('.')[-1]
        
        image_exts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']
        video_exts = ['mp4', 'webm', 'ogg', 'avi', 'mov']
        document_exts = ['pdf', 'doc', 'docx', 'txt', 'rtf']
        
        if ext in image_exts:
            return 'image'
        elif ext in video_exts:
            return 'video'
        elif ext in document_exts:
            return 'document'
        else:
            return 'other'
