"""
Tests für DealShare - Umfassende Test-Suite
"""
import json
import tempfile
import os
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import Deal, DealFile, DealFileAssignment, DealChangeLog, ContentBlock, MediaLibrary, LayoutTemplate
from files.models import GlobalFile

User = get_user_model()


class DealShareBaseTestCase(TestCase):
    """Basis-Test-Klasse mit Setup"""
    
    def setUp(self):
        """Test-Daten erstellen"""
        # Test-User erstellen
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            plan='free'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True,
            plan='enterprise'
        )
        
        # Test-Dealroom erstellen
        self.deal = Deal.objects.create(
            title='Test Dealroom',
            slug='test-dealroom',
            recipient_name='Test Empfänger',
            recipient_email='empfaenger@test.com',
            company_name='Test GmbH',
            description='Ein Test Dealroom',
            template_type='modern',
            theme_type='light',
            primary_color='#667eea',
            secondary_color='#764ba2',
            status='active',
            created_by=self.user
        )
        
        # Test-Content-Block erstellen
        self.content_block = ContentBlock.objects.create(
            title='Test Content Block',
            content='Dies ist ein Test-Content-Block',
            content_type='custom',
            created_by=self.user
        )
        
        # Test-Media-Item erstellen
        self.media_item = MediaLibrary.objects.create(
            title='Test Media',
            media_type='image',
            description='Ein Test-Medien-Item',
            created_by=self.user
        )
        
        # Client für Tests
        self.client = Client()
    
    def login_user(self, user=None):
        """User einloggen"""
        if user is None:
            user = self.user
        self.client.force_login(user)


class DealModelTests(DealShareBaseTestCase):
    """Tests für das Deal-Model"""
    
    def test_deal_creation(self):
        """Test: Dealroom erstellen"""
        self.assertEqual(self.deal.title, 'Test Dealroom')
        self.assertEqual(self.deal.status, 'active')
        self.assertEqual(self.deal.created_by, self.user)
    
    def test_deal_url_generation(self):
        """Test: URL-Generierung"""
        self.assertEqual(self.deal.slug, 'test-dealroom')
        public_url = self.deal.get_public_url()
        self.assertIn('test-dealroom', public_url)
    
    def test_deal_template_methods(self):
        """Test: Template-Methoden"""
        templates = Deal.get_available_templates()
        self.assertIsInstance(templates, list)
        self.assertTrue(len(templates) > 0)
        self.assertIn('name', templates[0])
        self.assertIn('display_name', templates[0])
    
    def test_deal_duplication(self):
        """Test: Dealroom duplizieren"""
        original_count = Deal.objects.count()
        duplicated_deal = self.deal.duplicate()
        
        self.assertEqual(Deal.objects.count(), original_count + 1)
        self.assertEqual(duplicated_deal.title, f"{self.deal.title} (Kopie)")
        self.assertEqual(duplicated_deal.created_by, self.user)
        self.assertEqual(duplicated_deal.status, 'draft')


class GrapesJSIntegrationTests(DealShareBaseTestCase):
    """Tests für GrapesJS Integration"""
    
    def test_grapesjs_editor_access(self):
        """Test: GrapesJS Editor Zugriff"""
        self.login_user()
        response = self.client.get(reverse('deals:grapesjs_editor', args=[self.deal.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'grapesjs')
        self.assertContains(response, 'gjs')
        self.assertContains(response, 'GrapesJS Editor')
    
    def test_grapesjs_editor_unauthorized(self):
        """Test: Unauthorized Zugriff auf GrapesJS Editor"""
        # Nicht eingeloggt
        response = self.client.get(reverse('deals:grapesjs_editor', args=[self.deal.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Anderer User
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        self.client.force_login(other_user)
        response = self.client.get(reverse('deals:grapesjs_editor', args=[self.deal.pk]))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_grapesjs_asset_upload(self):
        """Test: Asset-Upload für GrapesJS"""
        self.login_user()
        
        # Test-Bild erstellen
        image_content = b'fake-image-content'
        image_file = SimpleUploadedFile(
            'test_image.jpg',
            image_content,
            content_type='image/jpeg'
        )
        
        response = self.client.post(
            reverse('deals:grapesjs_upload'),
            {'files': image_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('data', response_data)
        
        # Prüfe ob MediaLibrary Eintrag erstellt wurde
        media_items = MediaLibrary.objects.filter(title='test_image.jpg')
        self.assertTrue(media_items.exists())
    
    def test_grapesjs_html_save(self):
        """Test: HTML-Speicherung von GrapesJS"""
        self.login_user()
        
        test_html = '<div class="test">Test Content</div>'
        test_css = '.test { color: red; }'
        
        response = self.client.post(
            reverse('deals:grapesjs_editor', args=[self.deal.pk]),
            data=json.dumps({
                'html': test_html,
                'css': test_css
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Prüfe ob Deal aktualisiert wurde
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.custom_html_content, test_html)
        self.assertEqual(self.deal.custom_css, test_css)
        self.assertEqual(self.deal.html_editor_mode, 'manual')


class DealroomCreationTests(DealShareBaseTestCase):
    """Tests für Dealroom-Erstellung"""
    
    def test_modern_deal_creation_form(self):
        """Test: Moderne Dealroom-Erstellung"""
        self.login_user()
        response = self.client.get(reverse('deals:dealroom_create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Neuen Dealroom erstellen')
        self.assertContains(response, 'Template & Design')
    
    def test_modern_deal_creation_submission(self):
        """Test: Dealroom-Erstellung Submit"""
        self.login_user()
        
        form_data = {
            'title': 'Neuer Test Dealroom',
            'slug': 'neuer-test-dealroom',
            'recipient_name': 'Neuer Empfänger',
            'recipient_email': 'neuer@test.com',
            'company_name': 'Neue Test GmbH',
            'description': 'Ein neuer Test Dealroom',
            'template_type': 'corporate',
            'theme_type': 'dark',
            'primary_color': '#ff6b6b',
            'secondary_color': '#4ecdc4'
        }
        
        response = self.client.post(reverse('deals:dealroom_create'), form_data)
        
        # Sollte zu Landingpage Builder weiterleiten
        self.assertEqual(response.status_code, 302)
        
        # Prüfe ob Dealroom erstellt wurde
        new_deal = Deal.objects.filter(title='Neuer Test Dealroom').first()
        self.assertIsNotNone(new_deal)
        self.assertEqual(new_deal.template_type, 'corporate')
        self.assertEqual(new_deal.theme_type, 'dark')
    
    def test_deal_creation_validation(self):
        """Test: Validierung bei Dealroom-Erstellung"""
        self.login_user()
        
        # Test mit fehlenden Pflichtfeldern
        form_data = {
            'title': '',  # Leerer Titel
            'recipient_email': 'invalid-email'  # Ungültige E-Mail
        }
        
        response = self.client.post(reverse('deals:dealroom_create'), form_data)
        
        self.assertEqual(response.status_code, 200)  # Bleibt auf Formular
        self.assertContains(response, 'Dieses Feld ist erforderlich')


class ContentLibraryTests(DealShareBaseTestCase):
    """Tests für Content Library"""
    
    def test_content_library_access(self):
        """Test: Content Library Zugriff"""
        self.login_user()
        response = self.client.get(reverse('deals:content_library'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Content-Bibliothek')
    
    def test_content_block_creation(self):
        """Test: Content Block erstellen"""
        self.login_user()
        
        form_data = {
            'title': 'Neuer Content Block',
            'content': 'Dies ist ein neuer Content Block',
            'content_type': 'custom'
        }
        
        response = self.client.post(reverse('deals:content_block_create'), form_data)
        
        # Sollte weiterleiten
        self.assertEqual(response.status_code, 302)
        
        # Prüfe ob Content Block erstellt wurde
        new_block = ContentBlock.objects.filter(title='Neuer Content Block').first()
        self.assertIsNotNone(new_block)
        self.assertEqual(new_block.created_by, self.user)
    
    def test_media_upload(self):
        """Test: Media Upload"""
        self.login_user()
        
        # Test-Bild erstellen
        image_content = b'fake-image-content'
        image_file = SimpleUploadedFile(
            'test_media.jpg',
            image_content,
            content_type='image/jpeg'
        )
        
        form_data = {
            'title': 'Test Media Upload',
            'description': 'Ein Test Media Upload',
            'media_type': 'image'
        }
        
        response = self.client.post(
            reverse('deals:media_upload'),
            {**form_data, 'file': image_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Prüfe ob Media Item erstellt wurde
        media_items = MediaLibrary.objects.filter(title='Test Media Upload')
        self.assertTrue(media_items.exists())


class LandingpageBuilderTests(DealShareBaseTestCase):
    """Tests für Landingpage Builder"""
    
    def test_landingpage_builder_access(self):
        """Test: Landingpage Builder Zugriff"""
        self.login_user()
        response = self.client.get(reverse('deals:landingpage_builder', args=[self.deal.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Landingpage Builder')
    
    def test_landingpage_builder_content_integration(self):
        """Test: Content-Integration im Builder"""
        self.login_user()
        response = self.client.get(reverse('deals:landingpage_builder', args=[self.deal.pk]))
        
        # Prüfe ob Content Blocks angezeigt werden
        self.assertContains(response, 'Content-Blöcke')
        self.assertContains(response, 'Test Content Block')
    
    def test_landingpage_builder_media_integration(self):
        """Test: Media-Integration im Builder"""
        self.login_user()
        response = self.client.get(reverse('deals:landingpage_builder', args=[self.deal.pk]))
        
        # Prüfe ob Media Items angezeigt werden
        self.assertContains(response, 'Medien-Bibliothek')
        self.assertContains(response, 'Test Media')


class UserManagementTests(DealShareBaseTestCase):
    """Tests für User Management"""
    
    def test_user_registration(self):
        """Test: User Registrierung"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'plan': 'free'
        }
        
        response = self.client.post(reverse('users:register'), form_data)
        
        # Sollte weiterleiten nach erfolgreicher Registrierung
        self.assertEqual(response.status_code, 302)
        
        # Prüfe ob User erstellt wurde
        new_user = User.objects.filter(username='newuser').first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.plan, 'free')
    
    def test_user_login(self):
        """Test: User Login"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 302)  # Weiterleitung nach Login
        
        # Prüfe ob User eingeloggt ist
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_user_profile(self):
        """Test: User Profil"""
        self.login_user()
        response = self.client.get(reverse('users:profile'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
        self.assertContains(response, 'test@example.com')


class DealroomManagementTests(DealShareBaseTestCase):
    """Tests für Dealroom Management"""
    
    def test_dealroom_list(self):
        """Test: Dealroom Liste"""
        self.login_user()
        response = self.client.get(reverse('deals:dealroom_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dealroom')
    
    def test_dealroom_detail(self):
        """Test: Dealroom Details"""
        self.login_user()
        response = self.client.get(reverse('deals:dealroom_detail', args=[self.deal.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dealroom')
        self.assertContains(response, 'GrapesJS Editor')
    
    def test_dealroom_edit(self):
        """Test: Dealroom bearbeiten"""
        self.login_user()
        response = self.client.get(reverse('deals:dealroom_edit', args=[self.deal.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bearbeiten')
    
    def test_dealroom_delete(self):
        """Test: Dealroom löschen"""
        self.login_user()
        
        # Erstelle einen separaten Dealroom zum Löschen
        deal_to_delete = Deal.objects.create(
            title='Dealroom zum Löschen',
            slug='dealroom-zum-loeschen',
            created_by=self.user
        )
        
        response = self.client.post(reverse('deals:dealroom_delete', args=[deal_to_delete.pk]))
        
        self.assertEqual(response.status_code, 302)  # Weiterleitung nach Löschung
        
        # Prüfe ob Dealroom gelöscht wurde
        self.assertFalse(Deal.objects.filter(pk=deal_to_delete.pk).exists())


class FileManagementTests(DealShareBaseTestCase):
    """Tests für Datei-Management"""
    
    def test_file_upload(self):
        """Test: Datei-Upload"""
        self.login_user()
        
        # Test-Datei erstellen
        file_content = b'Test file content'
        test_file = SimpleUploadedFile(
            'test_document.pdf',
            file_content,
            content_type='application/pdf'
        )
        
        form_data = {
            'title': 'Test Dokument',
            'file_type': 'document',
            'description': 'Ein Test-Dokument'
        }
        
        response = self.client.post(
            reverse('deals:dealroom_file_upload', args=[self.deal.pk]),
            {**form_data, 'file': test_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Prüfe ob Datei erstellt wurde
        files = DealFile.objects.filter(deal=self.deal, title='Test Dokument')
        self.assertTrue(files.exists())
    
    def test_file_assignment(self):
        """Test: Datei-Zuweisung"""
        self.login_user()
        
        # Erstelle eine GlobalFile
        global_file = GlobalFile.objects.create(
            title='Global Test File',
            file_type='document',
            created_by=self.user
        )
        
        response = self.client.post(
            reverse('deals:dealroom_file_assign', args=[self.deal.pk]),
            {'global_file_id': global_file.pk}
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Prüfe ob Assignment erstellt wurde
        assignments = DealFileAssignment.objects.filter(
            deal=self.deal,
            global_file=global_file
        )
        self.assertTrue(assignments.exists())


class AnalyticsTests(DealShareBaseTestCase):
    """Tests für Analytics"""
    
    def test_analytics_opt_in(self):
        """Test: Analytics Opt-In"""
        self.login_user()
        
        # Prüfe initialen Status
        self.assertFalse(self.user.analytics_opt_in)
        
        # Opt-In setzen
        self.user.analytics_opt_in = True
        self.user.save()
        
        self.assertTrue(self.user.analytics_opt_in)
    
    def test_deal_analytics_event_creation(self):
        """Test: Analytics Event Erstellung"""
        # User mit Analytics Opt-In
        self.user.analytics_opt_in = True
        self.user.save()
        
        # Erstelle einen neuen Deal (sollte Event triggern)
        new_deal = Deal.objects.create(
            title='Analytics Test Deal',
            slug='analytics-test-deal',
            created_by=self.user
        )
        
        # Prüfe ob Analytics Event erstellt wurde
        from deals.models import DealAnalyticsEvent
        events = DealAnalyticsEvent.objects.filter(
            deal=new_deal,
            user=self.user,
            event_type='deal_created'
        )
        self.assertTrue(events.exists())


class PasswordProtectionTests(DealShareBaseTestCase):
    """Tests für Passwortschutz"""
    
    def test_password_protection_setup(self):
        """Test: Passwortschutz einrichten"""
        self.login_user()
        
        # Passwortschutz aktivieren
        self.deal.password_protection_enabled = True
        self.deal.set_password_protection('testpass123', 'Bitte Passwort eingeben')
        self.deal.save()
        
        self.assertTrue(self.deal.password_protection_enabled)
        self.assertTrue(self.deal.check_password('testpass123'))
    
    def test_password_protection_landingpage(self):
        """Test: Passwortschutz auf Landingpage"""
        # Passwortschutz aktivieren
        self.deal.password_protection_enabled = True
        self.deal.set_password_protection('testpass123', 'Bitte Passwort eingeben')
        self.deal.save()
        
        # Versuche Landingpage ohne Passwort zu öffnen
        response = self.client.get(reverse('deals:landingpage', args=[self.deal.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwortschutz')
        
        # Mit korrektem Passwort
        response = self.client.post(reverse('deals:landingpage', args=[self.deal.pk]), {
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dealroom')


class URLGenerationTests(DealShareBaseTestCase):
    """Tests für URL-Generierung"""
    
    def test_friendly_url_generation(self):
        """Test: Freundliche URL-Generierung"""
        self.deal.url_type = 'friendly'
        self.deal.save()
        
        url = self.deal.get_public_url()
        self.assertIn('test-dealroom', url)
    
    def test_random_url_generation(self):
        """Test: Random URL-Generierung"""
        self.deal.url_type = 'random'
        self.deal.generate_random_url_code()
        self.deal.save()
        
        url = self.deal.get_public_url()
        self.assertIn(self.deal.random_url_code, url)
        self.assertEqual(len(self.deal.random_url_code), 8)


class TemplateSystemTests(DealShareBaseTestCase):
    """Tests für Template-System"""
    
    def test_template_creation_from_template(self):
        """Test: Dealroom aus Template erstellen"""
        template_data = {
            'title': 'Template Dealroom',
            'template_type': 'corporate',
            'theme_type': 'dark',
            'primary_color': '#ff0000',
            'secondary_color': '#00ff00'
        }
        
        new_deal = Deal.create_from_template(
            template_data,
            created_by=self.user
        )
        
        self.assertEqual(new_deal.template_type, 'corporate')
        self.assertEqual(new_deal.theme_type, 'dark')
        self.assertEqual(new_deal.primary_color, '#ff0000')
    
    def test_available_templates(self):
        """Test: Verfügbare Templates"""
        templates = Deal.get_available_templates()
        
        template_names = [t['name'] for t in templates]
        expected_names = ['modern', 'classic', 'minimal', 'corporate', 'creative']
        
        for name in expected_names:
            self.assertIn(name, template_names)


class IntegrationTests(DealShareBaseTestCase):
    """Integration Tests für das gesamte System"""
    
    def test_complete_workflow(self):
        """Test: Kompletter Workflow von Dealroom-Erstellung bis GrapesJS"""
        self.login_user()
        
        # 1. Dealroom erstellen
        form_data = {
            'title': 'Workflow Test Dealroom',
            'slug': 'workflow-test',
            'recipient_name': 'Workflow Empfänger',
            'recipient_email': 'workflow@test.com',
            'template_type': 'modern',
            'theme_type': 'light',
            'primary_color': '#667eea',
            'secondary_color': '#764ba2'
        }
        
        response = self.client.post(reverse('deals:dealroom_create'), form_data)
        self.assertEqual(response.status_code, 302)
        
        # 2. Dealroom finden
        new_deal = Deal.objects.filter(title='Workflow Test Dealroom').first()
        self.assertIsNotNone(new_deal)
        
        # 3. GrapesJS Editor öffnen
        response = self.client.get(reverse('deals:grapesjs_editor', args=[new_deal.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'GrapesJS Editor')
        
        # 4. HTML speichern
        test_html = '<div class="workflow-test">Workflow Test Content</div>'
        test_css = '.workflow-test { background: red; }'
        
        response = self.client.post(
            reverse('deals:grapesjs_editor', args=[new_deal.pk]),
            data=json.dumps({'html': test_html, 'css': test_css}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # 5. Prüfe gespeicherte Daten
        new_deal.refresh_from_db()
        self.assertEqual(new_deal.custom_html_content, test_html)
        self.assertEqual(new_deal.custom_css, test_css)
    
    def test_error_handling(self):
        """Test: Fehlerbehandlung"""
        self.login_user()
        
        # Test mit ungültigen Daten
        response = self.client.post(
            reverse('deals:grapesjs_editor', args=[self.deal.pk]),
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        
        # Test mit nicht existierendem Dealroom
        response = self.client.get(reverse('deals:grapesjs_editor', args=[99999]))
        self.assertEqual(response.status_code, 404)


# Performance Tests
class PerformanceTests(DealShareBaseTestCase):
    """Performance Tests"""
    
    def test_multiple_dealroom_creation(self):
        """Test: Mehrere Dealrooms erstellen"""
        self.login_user()
        
        start_time = timezone.now()
        
        for i in range(10):
            Deal.objects.create(
                title=f'Performance Test Dealroom {i}',
                slug=f'performance-test-{i}',
                created_by=self.user
            )
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        # Sollte unter 1 Sekunde dauern
        self.assertLess(duration, 1.0)
    
    def test_large_html_handling(self):
        """Test: Große HTML-Dateien handhaben"""
        self.login_user()
        
        # Große HTML-Content erstellen
        large_html = '<div>' + '<p>Test Content</p>' * 1000 + '</div>'
        large_css = '.test { color: red; }' * 100
        
        response = self.client.post(
            reverse('deals:grapesjs_editor', args=[self.deal.pk]),
            data=json.dumps({'html': large_html, 'css': large_css}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Prüfe ob gespeichert wurde
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.custom_html_content, large_html)


# Security Tests
class SecurityTests(DealShareBaseTestCase):
    """Security Tests"""
    
    def test_csrf_protection(self):
        """Test: CSRF-Schutz"""
        self.login_user()
        
        # Test ohne CSRF-Token
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        
        response = client.post(
            reverse('deals:grapesjs_editor', args=[self.deal.pk]),
            data=json.dumps({'html': '<div>test</div>'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)  # CSRF Error
    
    def test_xss_protection(self):
        """Test: XSS-Schutz"""
        self.login_user()
        
        malicious_html = '<script>alert("xss")</script><div>content</div>'
        
        response = self.client.post(
            reverse('deals:grapesjs_editor', args=[self.deal.pk]),
            data=json.dumps({'html': malicious_html, 'css': ''}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # HTML sollte gespeichert werden (GrapesJS handhabt XSS)
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.custom_html_content, malicious_html)


print("✅ Alle Tests erfolgreich erstellt!")

