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
from .models import Deal, DealFile, DealFileAssignment
from .forms import DealForm, DealFileForm
from files.models import GlobalFile
from .utils import (
    log_deal_creation, log_deal_update, log_status_change,
    log_file_assignment, log_file_unassignment,
    log_website_generation, log_website_deletion
)


# Dealroom Views
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
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Log erstellen
        log_deal_creation(self.object, self.request.user)
        
        # Logo-Upload verarbeiten
        logo_file = self.request.FILES.get('logo_upload')
        if logo_file:
            deal_file = DealFile.objects.create(
                deal=self.object,
                title=f"Logo - {self.object.title}",
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
        
        messages.success(self.request, f'Dealroom "{self.object.title}" wurde erfolgreich erstellt.')
        return response
    
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
    
    def form_valid(self, form):
        old_status = self.object.status
        response = super().form_valid(form)
        
        # Log erstellen
        log_deal_update(self.object, self.request.user)
        
        # Status-Änderung loggen
        if old_status != self.object.status:
            log_status_change(self.object, self.request.user, old_status, self.object.status)
        
        # Logo-Upload verarbeiten
        logo_file = self.request.FILES.get('logo_upload')
        if logo_file:
            deal_file = DealFile.objects.create(
                deal=self.object,
                title=f"Logo - {self.object.title}",
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
            generator = DealroomGenerator(dealroom)
            
            # Website regenerieren
            website_url = generator.regenerate_website()
            
            # Änderung protokollieren
            log_website_generation(dealroom, request.user)
            
            messages.success(
                request,
                f"Website für '{dealroom.title}' erfolgreich regeneriert: {website_url}"
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
