"""
URL-Konfiguration für die Dealrooms-App
"""
from django.urls import path
from . import views

app_name = 'deals'

urlpatterns = [
    # Quick Setup
    path('quick-setup/', views.QuickSetupView.as_view(), name='quick_setup'),
    
    # Dealroom-Listen
    path('', views.DealListView.as_view(), name='dealroom_list'),
    
    # Dealroom-Details
    path('<int:pk>/', views.DealDetailView.as_view(), name='dealroom_detail'),
    
    # Dealroom erstellen/bearbeiten
    path('create/', views.ModernDealCreateView.as_view(), name='dealroom_create'),
    path('batch-create/', views.DealBatchCreateView.as_view(), name='dealroom_batch_create'),
    path('<int:pk>/edit/', views.DealUpdateView.as_view(), name='dealroom_edit'),
    path('<int:pk>/delete/', views.DealDeleteView.as_view(), name='dealroom_delete'),
    
    # Datei-Management
    path('<int:pk>/files/', views.DealFileListView.as_view(), name='dealroom_file_list'),
    path('<int:pk>/files/upload/', views.DealFileUploadView.as_view(), name='dealroom_file_upload'),
    path('<int:pk>/files/assign/', views.DealFileAssignmentView.as_view(), name='dealroom_file_assign'),
    path('<int:pk>/files/unassign/', views.DealFileUnassignmentView.as_view(), name='dealroom_file_unassign'),
    
    # Deal-Datei Details und Aktionen
    path('files/<int:pk>/', views.DealFileDetailView.as_view(), name='dealroom_file_detail'),
    path('files/<int:pk>/edit/', views.DealFileEditView.as_view(), name='dealroom_file_edit'),
    path('files/<int:pk>/delete/', views.DealFileDeleteView.as_view(), name='dealroom_file_delete'),
    path('files/<int:pk>/download/', views.DealFileDownloadView.as_view(), name='dealroom_file_download'),
    
    # Website-Management
    path('<int:pk>/regenerate/', views.RegenerateWebsiteView.as_view(), name='dealroom_regenerate'),
    path('<int:pk>/delete-website/', views.DeleteWebsiteView.as_view(), name='dealroom_delete_website'),
    
    # HTML-Editor
    path('<int:deal_id>/html-editor/', views.HTMLEditorView.as_view(), name='html_editor'),
    path('<int:deal_id>/html-preview/', views.HTMLPreviewView.as_view(), name='html_preview'),
    path('<int:deal_id>/html-code/', views.HTMLCodeView.as_view(), name='html_code'),
    
    # Password Protection URLs
    path('<int:deal_id>/landingpage/', views.LandingpageView.as_view(), name='landingpage'),
    path('<int:deal_id>/password-protection/', views.PasswordProtectionView.as_view(), name='password_protection'),
    path('<int:deal_id>/password-protection-admin/', views.PasswordProtectionAdminView.as_view(), name='password_protection_admin'),
    
    # Content-Management URLs
    path('<int:deal_id>/builder/', views.LandingpageBuilderView.as_view(), name='landingpage_builder'),
    
    # Content-Block URLs
    path('content-blocks/', views.ContentBlockListView.as_view(), name='content_block_list'),
    path('content-blocks/create/', views.ContentBlockCreateView.as_view(), name='content_block_create'),
    path('content-blocks/<int:pk>/', views.ContentBlockDetailView.as_view(), name='content_block_detail'),
    path('content-blocks/<int:pk>/edit/', views.ContentBlockUpdateView.as_view(), name='content_block_edit'),
    path('content-blocks/<int:pk>/delete/', views.ContentBlockDeleteView.as_view(), name='content_block_delete'),
    
    # Media-Library URLs
    path('media/', views.MediaLibraryListView.as_view(), name='media_library_list'),
    path('media/upload/', views.MediaUploadView.as_view(), name='media_upload'),
    path('media/<int:pk>/', views.MediaLibraryDetailView.as_view(), name='media_library_detail'),
    path('media/<int:pk>/edit/', views.MediaLibraryUpdateView.as_view(), name='media_library_edit'),
    path('media/<int:pk>/delete/', views.MediaLibraryDeleteView.as_view(), name='media_library_delete'),


    
    # Duplizierung
    path('<int:deal_id>/duplicate/', views.DuplicateDealView.as_view(), name='duplicate_deal'),
    
    # GrapesJS Editor
    path('<int:deal_id>/grapesjs/', views.GrapesJSView.as_view(), name='grapesjs_editor'),
    path('api/grapesjs/upload-asset/', views.GrapesJSAssetUploadView.as_view(), name='grapesjs_upload'),
    
    # CMS-Element API
    path('api/cms-element/<int:element_id>/', views.CMSElementAPIView.as_view(), name='cms_element_api'),
] 