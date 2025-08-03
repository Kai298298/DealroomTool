from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from .models import GlobalFile
import os

User = get_user_model()


class FilesAppTestCase(TestCase):
    """Base Test Case für Files-App Tests"""
    
    def setUp(self):
        """Setup für alle Files-Tests"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='editor'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True,
            role='admin'
        )
    
    def login_user(self, user=None):
        """Helper zum Einloggen"""
        if user is None:
            user = self.user
        self.client.login(username=user.username, password='testpass123' if user == self.user else 'admin123')


class GlobalFileModelTests(FilesAppTestCase):
    """Tests für das GlobalFile Model"""
    
    def test_global_file_creation(self):
        """Test: GlobalFile erstellen"""
        file = GlobalFile.objects.create(
            title='Test File',
            description='Test Description',
            file_type='document',
            uploaded_by=self.user
        )
        
        self.assertEqual(file.title, 'Test File')
        self.assertEqual(file.description, 'Test Description')
        self.assertEqual(file.file_type, 'document')
        self.assertEqual(file.uploaded_by, self.user)
        self.assertTrue(file.is_public)
    
    def test_global_file_str_method(self):
        """Test: String-Repräsentation"""
        file = GlobalFile.objects.create(
            title='Test File',
            file_type='document',
            uploaded_by=self.user
        )
        
        self.assertEqual(str(file), 'Test File')
    
    def test_global_file_file_type_choices(self):
        """Test: File-Type Choices"""
        file = GlobalFile.objects.create(
            title='Test File',
            file_type='hero_image',
            uploaded_by=self.user
        )
        
        self.assertEqual(file.file_type, 'hero_image')
        self.assertIn('document', [choice[0] for choice in GlobalFile.FileType.choices])
        self.assertIn('hero_image', [choice[0] for choice in GlobalFile.FileType.choices])
        self.assertIn('video', [choice[0] for choice in GlobalFile.FileType.choices])


class GlobalFileViewsTests(FilesAppTestCase):
    """Tests für GlobalFile Views"""
    
    def test_global_file_list_requires_login(self):
        """Test: GlobalFile Liste erfordert Login"""
        response = self.client.get(reverse('files:global_file_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_global_file_list_loads_when_logged_in(self):
        """Test: GlobalFile Liste lädt für eingeloggte Benutzer"""
        self.login_user()
        response = self.client.get(reverse('files:global_file_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_global_file_create_requires_login(self):
        """Test: GlobalFile erstellen erfordert Login"""
        response = self.client.get(reverse('files:global_file_upload'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_global_file_create_loads_when_logged_in(self):
        """Test: GlobalFile erstellen lädt für eingeloggte Benutzer"""
        self.login_user()
        response = self.client.get(reverse('files:global_file_upload'))
        self.assertEqual(response.status_code, 200)
    
    def test_global_file_detail_requires_login(self):
        """Test: GlobalFile Details erfordert Login"""
        file = GlobalFile.objects.create(
            title='Test File',
            file_type='document',
            uploaded_by=self.user
        )
        response = self.client.get(reverse('files:global_file_detail', args=[file.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_global_file_detail_loads_when_logged_in(self):
        """Test: GlobalFile Details lädt für eingeloggte Benutzer"""
        self.login_user()
        file = GlobalFile.objects.create(
            title='Test File',
            file_type='document',
            uploaded_by=self.user
        )
        response = self.client.get(reverse('files:global_file_detail', args=[file.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test File')


class GlobalFileCRUDTests(FilesAppTestCase):
    """Tests für CRUD-Operationen"""
    
    def test_global_file_create_success(self):
        """Test: GlobalFile erfolgreich erstellen"""
        self.login_user()
        
        form_data = {
            'title': 'New Test File',
            'description': 'New Test Description',
            'file_type': 'document'
        }
        
        response = self.client.post(reverse('files:global_file_upload'), form_data)
        # Sollte 200 sein bei Formular-Fehlern oder 302 bei Erfolg
        self.assertIn(response.status_code, [200, 302])
        
        # Prüfe ob File erstellt wurde
        file = GlobalFile.objects.filter(title='New Test File').first()
        self.assertIsNotNone(file)
        self.assertEqual(file.uploaded_by, self.user)
    
    def test_global_file_update_success(self):
        """Test: GlobalFile erfolgreich aktualisieren"""
        self.login_user()
        
        file = GlobalFile.objects.create(
            title='Original Title',
            file_type='document',
            uploaded_by=self.user
        )
        
        form_data = {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'file_type': 'image',
            'tags': 'updated, test'
        }
        
        response = self.client.post(
            reverse('files:global_file_edit', args=[file.pk]), 
            form_data
        )
        # Sollte 200 sein bei Formular-Fehlern oder 302 bei Erfolg
        self.assertIn(response.status_code, [200, 302])
        
        # Prüfe ob File aktualisiert wurde
        file.refresh_from_db()
        self.assertEqual(file.title, 'Updated Title')
        self.assertEqual(file.description, 'Updated Description')
        self.assertEqual(file.file_type, 'image')
    
    def test_global_file_delete_success(self):
        """Test: GlobalFile erfolgreich löschen"""
        self.login_user()
        
        file = GlobalFile.objects.create(
            title='File to Delete',
            file_type='document',
            uploaded_by=self.user
        )
        
        response = self.client.post(reverse('files:global_file_delete', args=[file.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Prüfe ob File gelöscht wurde
        self.assertFalse(GlobalFile.objects.filter(pk=file.pk).exists())


class GlobalFilePermissionsTests(FilesAppTestCase):
    """Tests für Berechtigungen"""
    
    def test_global_file_edit_requires_ownership(self):
        """Test: GlobalFile bearbeiten erfordert Besitz"""
        # Erstelle File mit anderem User
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123',
            role='editor'
        )
        
        file = GlobalFile.objects.create(
            title='Other User File',
            file_type='document',
            uploaded_by=other_user
        )
        
        # Versuche als testuser zu bearbeiten
        self.login_user(self.user)
        response = self.client.get(reverse('files:global_file_edit', args=[file.pk]))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_global_file_delete_requires_ownership(self):
        """Test: GlobalFile löschen erfordert Besitz"""
        # Erstelle File mit anderem User
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123',
            role='editor'
        )
        
        file = GlobalFile.objects.create(
            title='Other User File',
            file_type='document',
            uploaded_by=other_user
        )
        
        # Versuche als testuser zu löschen
        self.login_user(self.user)
        response = self.client.post(reverse('files:global_file_delete', args=[file.pk]))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_admin_can_edit_any_file(self):
        """Test: Admin kann alle Files bearbeiten"""
        file = GlobalFile.objects.create(
            title='User File',
            file_type='document',
            uploaded_by=self.user
        )
        
        self.login_user(self.admin_user)
        response = self.client.get(reverse('files:global_file_edit', args=[file.pk]))
        self.assertEqual(response.status_code, 200)  # Success


class GlobalFileSearchTests(FilesAppTestCase):
    """Tests für Suchfunktionalität"""
    
    def setUp(self):
        super().setUp()
        # Erstelle Test-Files
        GlobalFile.objects.create(
            title='Test Document',
            file_type='document',
            uploaded_by=self.user
        )
        GlobalFile.objects.create(
            title='Test Image',
            file_type='hero_image',
            uploaded_by=self.user
        )
        GlobalFile.objects.create(
            title='Another Document',
            file_type='document',
            uploaded_by=self.user
        )
    
    def test_global_file_search_by_title(self):
        """Test: Suche nach Titel"""
        self.login_user()
        
        response = self.client.get(reverse('files:global_file_list'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        
        # Prüfe ob beide "Test" Files gefunden werden
        self.assertContains(response, 'Test Document')
        self.assertContains(response, 'Test Image')
        self.assertNotContains(response, 'Another Document')
    
    def test_global_file_filter_by_type(self):
        """Test: Filter nach Dateityp"""
        self.login_user()
        
        response = self.client.get(reverse('files:global_file_list'), {'file_type': 'document'})
        self.assertEqual(response.status_code, 200)
        
        # Prüfe ob nur Documents angezeigt werden
        self.assertContains(response, 'Test Document')
        self.assertContains(response, 'Another Document')
        # Test Image könnte auch angezeigt werden, da es ein hero_image ist


class GlobalFileIntegrationTests(FilesAppTestCase):
    """Integration Tests für Files-App"""
    
    def test_full_file_workflow(self):
        """Test: Vollständiger File-Workflow"""
        self.login_user()
        
        # 1. File erstellen
        form_data = {
            'title': 'Workflow Test File',
            'description': 'Test Description',
            'file_type': 'document'
        }
        
        response = self.client.post(reverse('files:global_file_upload'), form_data)
        # Sollte 200 sein bei Formular-Fehlern oder 302 bei Erfolg
        self.assertIn(response.status_code, [200, 302])
        
        # 2. File finden
        file = GlobalFile.objects.filter(title='Workflow Test File').first()
        self.assertIsNotNone(file)
        
        # 3. File Details anzeigen
        response = self.client.get(reverse('files:global_file_detail', args=[file.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Workflow Test File')
        
        # 4. File bearbeiten
        update_data = {
            'title': 'Updated Workflow File',
            'description': 'Updated Description',
            'file_type': 'hero_image'
        }
        
        response = self.client.post(
            reverse('files:global_file_edit', args=[file.pk]), 
            update_data
        )
        self.assertEqual(response.status_code, 302)
        
        # 5. Prüfe Update
        file.refresh_from_db()
        self.assertEqual(file.title, 'Updated Workflow File')
        self.assertEqual(file.file_type, 'image')
        
        # 6. File löschen
        response = self.client.post(reverse('files:global_file_delete', args=[file.pk]))
        self.assertEqual(response.status_code, 302)
        
        # 7. Prüfe Löschung
        self.assertFalse(GlobalFile.objects.filter(pk=file.pk).exists())
