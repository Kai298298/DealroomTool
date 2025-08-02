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
    path('<int:pk>/edit/', views.DealUpdateView.as_view(), name='dealroom_edit'),
    path('<int:pk>/delete/', views.DealDeleteView.as_view(), name='dealroom_delete'),
    
    # Datei-Management
    path('<int:pk>/files/upload/', views.DealFileUploadView.as_view(), name='dealroom_file_upload'),
    path('<int:pk>/files/assign/', views.DealFileAssignmentView.as_view(), name='dealroom_file_assign'),
    path('<int:pk>/files/unassign/', views.DealFileUnassignmentView.as_view(), name='dealroom_file_unassign'),
    
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
    path('content-library/', views.ContentLibraryView.as_view(), name='content_library'),


    
    # Duplizierung
    path('<int:deal_id>/duplicate/', views.DuplicateDealView.as_view(), name='duplicate_deal'),
    
    # GrapesJS Editor
    path('<int:deal_id>/grapesjs/', views.GrapesJSView.as_view(), name='grapesjs_editor'),
    path('api/grapesjs/upload-asset/', views.GrapesJSAssetUploadView.as_view(), name='grapesjs_upload'),
] 