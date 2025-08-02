from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import GlobalFile
from .forms import GlobalFileForm


class GlobalFileListView(LoginRequiredMixin, ListView):
    """
    Liste aller globalen Dateien
    """
    model = GlobalFile
    template_name = 'files/global_file_list.html'
    context_object_name = 'files'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = GlobalFile.objects.select_related('uploaded_by').order_by('-uploaded_at')
        
        # Suchfunktion
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )
        
        # Filter nach Dateityp
        file_type = self.request.GET.get('file_type')
        if file_type:
            queryset = queryset.filter(file_type=file_type)
        
        # Filter nach Uploader
        uploaded_by = self.request.GET.get('uploaded_by')
        if uploaded_by:
            queryset = queryset.filter(uploaded_by__username__icontains=uploaded_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['file_type_filter'] = self.request.GET.get('file_type', '')
        context['uploaded_by_filter'] = self.request.GET.get('uploaded_by', '')
        context['file_type_choices'] = GlobalFile.FileType.choices
        return context


class GlobalFileDetailView(LoginRequiredMixin, DetailView):
    """
    Detailansicht einer globalen Datei
    """
    model = GlobalFile
    template_name = 'files/global_file_detail.html'
    context_object_name = 'file'


class GlobalFileUploadView(LoginRequiredMixin, CreateView):
    """
    Globale Datei hochladen
    """
    model = GlobalFile
    form_class = GlobalFileForm
    template_name = 'files/global_file_upload.html'
    success_url = reverse_lazy('files:global_file_list')
    
    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        form.instance.is_public = True  # Standardmäßig öffentlich
        form.instance.is_primary = False  # Standardmäßig nicht primär
        messages.success(self.request, _('Datei erfolgreich hochgeladen.'))
        return super().form_valid(form)


class GlobalFileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Globale Datei bearbeiten
    """
    model = GlobalFile
    form_class = GlobalFileForm
    template_name = 'files/global_file_form.html'
    
    def test_func(self):
        file = self.get_object()
        return self.request.user == file.uploaded_by or self.request.user.is_staff
    
    def get_success_url(self):
        return reverse('files:global_file_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _('Datei erfolgreich aktualisiert.'))
        return super().form_valid(form)


class GlobalFileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Globale Datei löschen
    """
    model = GlobalFile
    template_name = 'files/global_file_confirm_delete.html'
    success_url = reverse_lazy('files:global_file_list')
    
    def test_func(self):
        file = self.get_object()
        return self.request.user == file.uploaded_by or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Datei erfolgreich gelöscht.'))
        return super().delete(request, *args, **kwargs)


class GlobalFileDownloadView(LoginRequiredMixin, DetailView):
    """
    Globale Datei herunterladen
    """
    model = GlobalFile
    
    def get(self, request, *args, **kwargs):
        file_obj = self.get_object()
        
        if not file_obj.file:
            raise Http404(_('Datei nicht gefunden.'))
        
        # Prüfen ob Benutzer Zugriff hat
        if not file_obj.is_public and request.user != file_obj.uploaded_by:
            raise Http404(_('Keine Berechtigung für diese Datei.'))
        
        response = HttpResponse(file_obj.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_obj.file.name.split("/")[-1]}"'
        return response
