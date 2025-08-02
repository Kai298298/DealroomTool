"""
URL-Konfiguration für die Files-App
"""
from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    # Globale Datei URLs
    path('', views.GlobalFileListView.as_view(), name='global_file_list'),
    path('upload/', views.GlobalFileUploadView.as_view(), name='global_file_upload'),
    path('<int:pk>/', views.GlobalFileDetailView.as_view(), name='global_file_detail'),
    path('<int:pk>/edit/', views.GlobalFileEditView.as_view(), name='global_file_edit'),
    path('<int:pk>/delete/', views.GlobalFileDeleteView.as_view(), name='global_file_delete'),
    path('<int:pk>/download/', views.GlobalFileDownloadView.as_view(), name='global_file_download'),
] 