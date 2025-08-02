"""
URL-Konfiguration für die Dealrooms-App
"""
from django.urls import path
from . import views

app_name = 'dealrooms'

urlpatterns = [
    # Dealroom-Listen
    path('', views.DealListView.as_view(), name='dealroom_list'),
    
    # Dealroom-Details
    path('<int:pk>/', views.DealDetailView.as_view(), name='dealroom_detail'),
    
    # Dealroom erstellen/bearbeiten
    path('create/', views.DealCreateView.as_view(), name='dealroom_create'),
    path('<int:pk>/edit/', views.DealUpdateView.as_view(), name='dealroom_edit'),
    path('<int:pk>/delete/', views.DealDeleteView.as_view(), name='dealroom_delete'),
    
    # Datei-Management
    path('<int:pk>/files/upload/', views.DealFileUploadView.as_view(), name='dealroom_file_upload'),
    path('<int:pk>/files/assign/', views.DealFileAssignmentView.as_view(), name='dealroom_file_assign'),
    path('<int:pk>/files/unassign/', views.DealFileUnassignmentView.as_view(), name='dealroom_file_unassign'),
    
    # Website-Management
    path('<int:pk>/regenerate/', views.RegenerateWebsiteView.as_view(), name='dealroom_regenerate'),
    path('<int:pk>/delete-website/', views.DeleteWebsiteView.as_view(), name='dealroom_delete_website'),
] 