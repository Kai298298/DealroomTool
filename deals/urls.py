"""
URL-Konfiguration für die Dealrooms-App
"""
from django.urls import path
from . import views
from .views import (
    DealListView, DealDetailView, DealCreateView, DealBatchCreateView,
    DealEditView, DealDeleteView, DealFileDownloadView,
    WebsitePreviewView, RegenerateWebsiteView, DeleteWebsiteView
)

app_name = 'dealrooms'

urlpatterns = [
    # Dealroom URLs
    path('', views.DealListView.as_view(), name='dealroom_list'),
    path('create/', views.DealCreateView.as_view(), name='dealroom_create'),
    path('batch-create/', views.DealBatchCreateView.as_view(), name='dealroom_batch_create'),
    path('<int:pk>/', views.DealDetailView.as_view(), name='dealroom_detail'),
    path('<int:pk>/edit/', views.DealEditView.as_view(), name='dealroom_edit'),
    path('<int:pk>/delete/', views.DealDeleteView.as_view(), name='dealroom_delete'),
    
    # Datei URLs
    path('files/<int:pk>/download/', views.DealFileDownloadView.as_view(), name='dealroom_file_download'),
    path('<int:deal_pk>/files/', views.DealFileListView.as_view(), name='dealroom_files'),
    path('<int:deal_pk>/files/upload/', views.DealFileUploadView.as_view(), name='dealroom_file_upload'),
    path('files/<int:pk>/', views.DealFileDetailView.as_view(), name='dealroom_file_detail'),
    path('files/<int:pk>/edit/', views.DealFileEditView.as_view(), name='dealroom_file_edit'),
    path('files/<int:pk>/delete/', views.DealFileDeleteView.as_view(), name='dealroom_file_delete'),
]

# Website-Management URLs
urlpatterns += [
    path('<int:pk>/preview/', WebsitePreviewView.as_view(), name='website_preview'),
    path('<int:pk>/regenerate/', RegenerateWebsiteView.as_view(), name='regenerate_website'),
    path('<int:pk>/delete-website/', DeleteWebsiteView.as_view(), name='delete_website'),
] 