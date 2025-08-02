"""
Tests für die Deals-App
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Deal, DealFile, DealFileAssignment
from .forms import DealForm, DealFileForm
from files.models import GlobalFile

User = get_user_model()


class DealModelTest(TestCase):
    """
    Tests für das Deal-Modell
    """
    
    def setUp(self):
        """Test-Daten erstellen"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role=User.UserRole.EDITOR
        )
        
        self.deal = Deal.objects.create(
            title='Test Dealroom',
            slug='test-dealroom',
            description='Ein Test Dealroom',
            status=Deal.DealStatus.DRAFT,
            template_type=Deal.TemplateType.MODERN,
            created_by=self.user,
            recipient_name='Max Mustermann',
            recipient_email='max@example.com',
            hero_title='Willkommen',
            hero_subtitle='Ein toller Dealroom',
            call_to_action='Jetzt kontaktieren',
            primary_color='#0d6efd',
            secondary_color='#6c757d'
        )
    
    def test_deal_creation(self):
        """Test: Dealroom kann erstellt werden"""
        self.assertEqual(self.deal.title, 'Test Dealroom')
        self.assertEqual(self.deal.slug, 'test-dealroom')
        self.assertEqual(self.deal.created_by, self.user)
        self.assertEqual(self.deal.status, Deal.DealStatus.DRAFT)
    
    def test_deal_str_method(self):
        """Test: __str__ Methode funktioniert"""
        self.assertEqual(str(self.deal), 'Test Dealroom')
    
    def test_deal_get_absolute_url(self):
        """Test: get_absolute_url funktioniert"""
        url = self.deal.get_absolute_url()
        self.assertIn('/dealrooms/', url)
    
    def test_deal_is_published(self):
        """Test: is_published Methode funktioniert"""
        # Draft sollte nicht published sein
        self.assertFalse(self.deal.is_published())
        
        # Active sollte published sein
        self.deal.status = Deal.DealStatus.ACTIVE
        self.deal.save()
        self.assertTrue(self.deal.is_published())


class DealFormTest(TestCase):
    """
    Tests für das DealForm
    """
    
    def setUp(self):
        """Test-Daten erstellen"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=User.UserRole.EDITOR
        )
    
    def test_deal_form_valid(self):
        """Test: DealForm mit gültigen Daten"""
        form_data = {
            'title': 'Neuer Dealroom',
            'slug': 'neuer-dealroom',
            'description': 'Ein neuer Dealroom',
            'status': Deal.DealStatus.DRAFT,
            'template_type': Deal.TemplateType.MODERN,
            'recipient_name': 'Max Mustermann',
            'recipient_email': 'max@example.com',
            'hero_title': 'Willkommen',
            'hero_subtitle': 'Ein toller Dealroom',
            'call_to_action': 'Jetzt kontaktieren',
            'primary_color': '#0d6efd',
            'secondary_color': '#6c757d'
        }
        
        form = DealForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_deal_form_invalid(self):
        """Test: DealForm mit ungültigen Daten"""
        # Ohne Pflichtfelder
        form_data = {
            'title': '',  # Leer - sollte ungültig sein
            'slug': 'test-slug',
            'recipient_email': 'invalid-email'  # Ungültige E-Mail
        }
        
        form = DealForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('recipient_email', form.errors)


class DealViewsTest(TestCase):
    """
    Tests für die Deal-Views
    """
    
    def setUp(self):
        """Test-Daten erstellen"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role=User.UserRole.EDITOR
        )
        
        self.deal = Deal.objects.create(
            title='Test Dealroom',
            slug='test-dealroom',
            description='Ein Test Dealroom',
            status=Deal.DealStatus.DRAFT,
            template_type=Deal.TemplateType.MODERN,
            created_by=self.user,
            recipient_name='Max Mustermann',
            recipient_email='max@example.com',
            hero_title='Willkommen',
            hero_subtitle='Ein toller Dealroom',
            call_to_action='Jetzt kontaktieren'
        )
    
    def test_deal_list_view_requires_login(self):
        """Test: Deal-Liste erfordert Login"""
        response = self.client.get(reverse('dealrooms:dealroom_list'))
        self.assertEqual(response.status_code, 302)  # Redirect zu Login
        self.assertIn('login', response.url)
    
    def test_deal_list_view_with_login(self):
        """Test: Deal-Liste funktioniert mit Login"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dealroom')
    
    def test_deal_detail_view_requires_login(self):
        """Test: Deal-Detail erfordert Login"""
        response = self.client.get(reverse('dealrooms:dealroom_detail', args=[self.deal.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect zu Login
    
    def test_deal_detail_view_with_login(self):
        """Test: Deal-Detail funktioniert mit Login"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dealrooms:dealroom_detail', args=[self.deal.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dealroom')
    
    def test_deal_create_view_requires_login(self):
        """Test: Deal-Erstellung erfordert Login"""
        response = self.client.get(reverse('dealrooms:dealroom_create'))
        self.assertEqual(response.status_code, 302)  # Redirect zu Login
    
    def test_deal_create_view_with_login(self):
        """Test: Deal-Erstellung funktioniert mit Login"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dealrooms:dealroom_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Titel')
    
    def test_deal_create_success(self):
        """Test: Dealroom erfolgreich erstellen"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('dealrooms:dealroom_create'),
            {
                'title': 'Neuer Dealroom',
                'slug': 'neuer-dealroom',
                'description': 'Ein neuer Dealroom',
                'status': 'draft',
                'template_type': 'modern',
                'recipient_name': 'Max Mustermann',
                'recipient_email': 'max@example.com',
                'hero_title': 'Willkommen',
                'hero_subtitle': 'Ein toller Dealroom',
                'call_to_action': 'Jetzt kontaktieren',
                'primary_color': '#0d6efd',
                'secondary_color': '#6c757d'
            }
        )
        
        self.assertRedirects(response, reverse('core:dashboard'))
        
        # Prüfen ob Dealroom erstellt wurde
        deal = Deal.objects.filter(title='Neuer Dealroom').first()
        self.assertIsNotNone(deal)
        self.assertEqual(deal.created_by, self.user)
    
    def test_deal_edit_view_requires_login(self):
        """Test: Deal-Bearbeitung erfordert Login"""
        response = self.client.get(reverse('dealrooms:dealroom_edit', args=[self.deal.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect zu Login
    
    def test_deal_edit_view_with_login(self):
        """Test: Deal-Bearbeitung funktioniert mit Login"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dealrooms:dealroom_edit', args=[self.deal.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dealroom')
    
    def test_deal_edit_success(self):
        """Test: Dealroom erfolgreich bearbeiten"""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'title': 'Bearbeiteter Dealroom',
            'slug': 'bearbeiteter-dealroom',
            'description': 'Ein bearbeiteter Dealroom',
            'status': Deal.DealStatus.ACTIVE,
            'template_type': Deal.TemplateType.CLASSIC,
            'recipient_name': 'Max Mustermann',
            'recipient_email': 'max@example.com',
            'hero_title': 'Willkommen',
            'hero_subtitle': 'Ein bearbeiteter Dealroom',
            'call_to_action': 'Jetzt kontaktieren',
            'primary_color': '#0d6efd',
            'secondary_color': '#6c757d'
        }
        
        response = self.client.post(reverse('dealrooms:dealroom_edit', args=[self.deal.pk]), form_data)
        
        # Sollte zur Deal-Liste weiterleiten
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dealrooms/', response.url)
        
        # Deal sollte aktualisiert sein
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.title, 'Bearbeiteter Dealroom')
        self.assertEqual(self.deal.status, Deal.DealStatus.ACTIVE)
    
    def test_deal_delete_view_requires_login(self):
        """Test: Deal-Löschung erfordert Login"""
        response = self.client.get(reverse('dealrooms:dealroom_delete', args=[self.deal.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect zu Login
    
    def test_deal_delete_view_with_login(self):
        """Test: Deal-Löschung funktioniert mit Login"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dealrooms:dealroom_delete', args=[self.deal.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dealroom')
    
    def test_deal_delete_success(self):
        """Test: Dealroom erfolgreich löschen"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('dealrooms:dealroom_delete', args=[self.deal.pk]))
        
        # Sollte zur Deal-Liste weiterleiten
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dealrooms/', response.url)
        
        # Deal sollte gelöscht sein
        self.assertFalse(Deal.objects.filter(pk=self.deal.pk).exists())


class DealIntegrationTest(TestCase):
    """
    Integrationstests für das komplette Dealroom-Workflow
    """
    
    def setUp(self):
        """Test-Daten erstellen"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role=User.UserRole.EDITOR
        )
    
    def test_full_dealroom_workflow(self):
        """Test: Kompletter Dealroom-Workflow (Erstellen -> Bearbeiten -> Löschen)"""
        self.client.login(username='testuser', password='testpass123')
        
        # 1. Dealroom erstellen
        form_data = {
            'title': 'Workflow Test Dealroom',
            'slug': 'workflow-test-dealroom',
            'description': 'Ein Dealroom für Workflow-Tests',
            'status': Deal.DealStatus.DRAFT,
            'template_type': Deal.TemplateType.MODERN,
            'recipient_name': 'Max Mustermann',
            'recipient_email': 'max@example.com',
            'hero_title': 'Workflow Test',
            'hero_subtitle': 'Ein Test für den Workflow',
            'call_to_action': 'Test Button',
            'primary_color': '#0d6efd',
            'secondary_color': '#6c757d'
        }
        
        response = self.client.post(reverse('dealrooms:dealroom_create'), form_data)
        self.assertEqual(response.status_code, 302)
        
        # Deal sollte existieren
        deal = Deal.objects.get(slug='workflow-test-dealroom')
        self.assertEqual(deal.title, 'Workflow Test Dealroom')
        self.assertEqual(deal.created_by, self.user)
        
        # 2. Dealroom bearbeiten
        edit_data = form_data.copy()
        edit_data['title'] = 'Bearbeiteter Workflow Test'
        edit_data['status'] = Deal.DealStatus.ACTIVE
        
        response = self.client.post(reverse('dealrooms:dealroom_edit', args=[deal.pk]), edit_data)
        self.assertEqual(response.status_code, 302)
        
        # Deal sollte aktualisiert sein
        deal.refresh_from_db()
        self.assertEqual(deal.title, 'Bearbeiteter Workflow Test')
        self.assertEqual(deal.status, Deal.DealStatus.ACTIVE)
        
        # 3. Dealroom löschen
        response = self.client.post(reverse('dealrooms:dealroom_delete', args=[deal.pk]))
        self.assertEqual(response.status_code, 302)
        
        # Deal sollte gelöscht sein
        self.assertFalse(Deal.objects.filter(pk=deal.pk).exists())
    
    def test_dealroom_search_functionality(self):
        """Test: Suchfunktionalität für Dealrooms"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('core:dashboard'), {'search': 'Python'})
        self.assertEqual(response.status_code, 200)
        
        # Prüfen ob Suchfunktionalität im Template vorhanden ist
        self.assertContains(response, 'search')
    
    def test_dealroom_status_filter(self):
        """Test: Status-Filter für Dealrooms"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('core:dashboard'), {'status': 'draft'})
        self.assertEqual(response.status_code, 200)
        
        # Prüfen ob Filter-Funktionalität im Template vorhanden ist
        self.assertContains(response, 'status')


class DealFileTest(TestCase):
    """
    Tests für Deal-Dateien
    """
    
    def setUp(self):
        """Test-Daten erstellen"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=User.UserRole.EDITOR
        )
        
        self.deal = Deal.objects.create(
            title='Test Dealroom',
            slug='test-dealroom',
            created_by=self.user,
            recipient_email='test@example.com'
        )
    
    def test_deal_file_creation(self):
        """Test: Deal-Datei kann erstellt werden"""
        # Simuliere eine Datei
        file_content = b'Test file content'
        uploaded_file = SimpleUploadedFile(
            'test.txt',
            file_content,
            content_type='text/plain'
        )
        
        deal_file = DealFile.objects.create(
            deal=self.deal,
            title='Test Datei',
            description='Eine Test-Datei',
            file=uploaded_file,
            file_type=DealFile.FileType.DOCUMENT,
            uploaded_by=self.user
        )
        
        self.assertEqual(deal_file.title, 'Test Datei')
        self.assertEqual(deal_file.deal, self.deal)
        self.assertEqual(deal_file.uploaded_by, self.user)
    
    def test_deal_file_form_valid(self):
        """Test: DealFileForm mit gültigen Daten"""
        file_content = b'Test file content'
        uploaded_file = SimpleUploadedFile(
            'test.pdf',
            file_content,
            content_type='application/pdf'
        )
        
        form_data = {
            'title': 'Test Datei',
            'description': 'Eine Test-Datei',
            'file_type': DealFile.FileType.DOCUMENT,
            'is_public': True,
            'is_primary': False
        }
        
        files = {
            'file': uploaded_file
        }
        
        form = DealFileForm(data=form_data, files=files)
        self.assertTrue(form.is_valid())
    
    def test_deal_file_str_method(self):
        """Test: __str__ Methode für DealFile"""
        file_content = b'Test file content'
        uploaded_file = SimpleUploadedFile(
            'test.txt',
            file_content,
            content_type='text/plain'
        )
        
        deal_file = DealFile.objects.create(
            deal=self.deal,
            title='Test Datei',
            file=uploaded_file,
            file_type=DealFile.FileType.DOCUMENT,
            uploaded_by=self.user
        )
        
        self.assertEqual(str(deal_file), 'Test Datei - Test Dealroom')


class DealFileAssignmentTest(TestCase):
    """
    Tests für die Datei-Zuordnung-Funktionalität
    """
    
    def setUp(self):
        """Test-Daten erstellen"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role=User.UserRole.EDITOR
        )
        
        self.deal = Deal.objects.create(
            title='Test Dealroom',
            slug='test-dealroom',
            description='Ein Test Dealroom',
            status=Deal.DealStatus.DRAFT,
            template_type=Deal.TemplateType.MODERN,
            created_by=self.user,
            recipient_name='Max Mustermann',
            recipient_email='max@example.com',
            hero_title='Willkommen',
            hero_subtitle='Ein toller Dealroom',
            call_to_action='Jetzt kontaktieren',
            primary_color='#0d6efd',
            secondary_color='#6c757d'
        )
        
        # Globale Datei erstellen
        self.global_file = GlobalFile.objects.create(
            title='Test Globale Datei',
            description='Eine Test-Datei',
            file=SimpleUploadedFile(
                'test.pdf',
                b'Test PDF content',
                content_type='application/pdf'
            ),
            file_type=GlobalFile.FileType.DOCUMENT,
            uploaded_by=self.user,
            is_public=True
        )
    
    def test_deal_file_assignment_creation(self):
        """Test: Datei-Zuordnung kann erstellt werden"""
        assignment = DealFileAssignment.objects.create(
            deal=self.deal,
            global_file=self.global_file,
            assigned_by=self.user,
            role='hero_image',
            order=0
        )
        
        self.assertEqual(assignment.deal, self.deal)
        self.assertEqual(assignment.global_file, self.global_file)
        self.assertEqual(assignment.assigned_by, self.user)
        self.assertEqual(assignment.role, 'hero_image')
        self.assertEqual(assignment.order, 0)
    
    def test_deal_file_assignment_str_method(self):
        """Test: __str__ Methode für DealFileAssignment"""
        assignment = DealFileAssignment.objects.create(
            deal=self.deal,
            global_file=self.global_file,
            assigned_by=self.user,
            role='hero_image'
        )
        
        expected = f"{self.deal.title} - {self.global_file.title} (Hero-Bild)"
        self.assertEqual(str(assignment), expected)
    
    def test_deal_get_assigned_files(self):
        """Test: get_assigned_files Methode"""
        assignment = DealFileAssignment.objects.create(
            deal=self.deal,
            global_file=self.global_file,
            assigned_by=self.user,
            role='hero_image'
        )
        
        # Alle zugeordneten Dateien
        assigned_files = self.deal.get_assigned_files()
        self.assertEqual(assigned_files.count(), 1)
        self.assertEqual(assigned_files.first(), assignment)
        
        # Gefiltert nach Rolle
        hero_files = self.deal.get_assigned_files(role='hero_image')
        self.assertEqual(hero_files.count(), 1)
        
        logo_files = self.deal.get_assigned_files(role='logo')
        self.assertEqual(logo_files.count(), 0)
    
    def test_deal_get_hero_images(self):
        """Test: get_hero_images Methode"""
        DealFileAssignment.objects.create(
            deal=self.deal,
            global_file=self.global_file,
            assigned_by=self.user,
            role='hero_image'
        )
        
        hero_images = self.deal.get_hero_images()
        self.assertEqual(hero_images.count(), 1)
    
    def test_deal_get_logos(self):
        """Test: get_logos Methode"""
        DealFileAssignment.objects.create(
            deal=self.deal,
            global_file=self.global_file,
            assigned_by=self.user,
            role='logo'
        )
        
        logos = self.deal.get_logos()
        self.assertEqual(logos.count(), 1)
    
    def test_unique_together_constraint(self):
        """Test: Unique Together Constraint"""
        # Erste Zuordnung
        assignment1 = DealFileAssignment.objects.create(
            deal=self.deal,
            global_file=self.global_file,
            assigned_by=self.user,
            role='hero_image'
        )
        
        # Zweite Zuordnung der gleichen Datei sollte fehlschlagen
        with self.assertRaises(Exception):
            DealFileAssignment.objects.create(
                deal=self.deal,
                global_file=self.global_file,
                assigned_by=self.user,
                role='logo'
            )


class DealFileAssignmentViewsTest(TestCase):
    """
    Tests für die Datei-Zuordnung Views
    """
    
    def setUp(self):
        """Test-Daten erstellen"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role=User.UserRole.EDITOR
        )
        
        self.deal = Deal.objects.create(
            title='Test Dealroom',
            slug='test-dealroom',
            description='Ein Test Dealroom',
            status=Deal.DealStatus.DRAFT,
            template_type=Deal.TemplateType.MODERN,
            created_by=self.user,
            recipient_name='Max Mustermann',
            recipient_email='max@example.com',
            hero_title='Willkommen',
            hero_subtitle='Ein toller Dealroom',
            call_to_action='Jetzt kontaktieren',
            primary_color='#0d6efd',
            secondary_color='#6c757d'
        )
        
        # Globale Datei erstellen
        self.global_file = GlobalFile.objects.create(
            title='Test Globale Datei',
            description='Eine Test-Datei',
            file=SimpleUploadedFile(
                'test.pdf',
                b'Test PDF content',
                content_type='application/pdf'
            ),
            file_type=GlobalFile.FileType.DOCUMENT,
            uploaded_by=self.user,
            is_public=True
        )
    
    def test_file_assignment_list_view_requires_login(self):
        """Test: Datei-Zuordnung-Liste erfordert Login"""
        response = self.client.get(
            reverse('dealrooms:dealroom_file_assignments', kwargs={'deal_pk': self.deal.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_file_assignment_list_view_with_login(self):
        """Test: Datei-Zuordnung-Liste funktioniert mit Login"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('dealrooms:dealroom_file_assignments', kwargs={'deal_pk': self.deal.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dateien zuordnen')
        self.assertContains(response, 'Test Dealroom')
    
    def test_file_assignment_list_view_without_permission(self):
        """Test: Datei-Zuordnung-Liste erfordert Berechtigung"""
        # Benutzer ohne EDITOR-Rolle erstellen
        viewer_user = User.objects.create_user(
            username='viewer',
            email='viewer@example.com',
            password='testpass123',
            role=User.UserRole.VIEWER
        )
        
        self.client.login(username='viewer', password='testpass123')
        response = self.client.get(
            reverse('dealrooms:dealroom_file_assignments', kwargs={'deal_pk': self.deal.pk})
        )
        self.assertEqual(response.status_code, 403)
    
    def test_assign_file_view_requires_login(self):
        """Test: Datei zuordnen erfordert Login"""
        response = self.client.get(
            reverse('dealrooms:dealroom_file_assign', kwargs={'pk': self.deal.pk}),
        )
        self.assertEqual(response.status_code, 302)  # Weiterleitung zum Login
    
    def test_assign_file_view_success(self):
        """Test: Datei erfolgreich zuordnen"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('dealrooms:dealroom_file_assign', kwargs={'pk': self.deal.pk}),
            {
                'global_file_id': self.global_file.id,
                'role': 'hero_image'
            }
        )
        self.assertRedirects(response, reverse('dealrooms:dealroom_detail', kwargs={'pk': self.deal.pk}))
        
        # Prüfen ob Zuordnung erstellt wurde
        assignment = DealFileAssignment.objects.filter(
            deal=self.deal,
            global_file=self.global_file
        ).first()
        self.assertIsNotNone(assignment)
        self.assertEqual(assignment.role, 'hero_image')
    
    def test_assign_file_view_invalid_file(self):
        """Test: Zuordnung mit ungültiger Datei"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('dealrooms:dealroom_file_assign', kwargs={'pk': self.deal.pk}),
            {
                'global_file_id': 99999,  # Nicht existierende ID
                'role': 'hero_image'
            }
        )
        self.assertRedirects(response, reverse('dealrooms:dealroom_detail', kwargs={'pk': self.deal.pk}))
    
    def test_assign_file_view_duplicate_assignment(self):
        """Test: Doppelte Zuordnung wird aktualisiert"""
        self.client.login(username='testuser', password='testpass123')
        
        # Erste Zuordnung
        response = self.client.post(
            reverse('dealrooms:dealroom_file_assign', kwargs={'pk': self.deal.pk}),
            {
                'global_file_id': self.global_file.id,
                'role': 'hero_image'
            }
        )
        self.assertRedirects(response, reverse('dealrooms:dealroom_detail', kwargs={'pk': self.deal.pk}))
        
        # Zweite Zuordnung mit anderer Rolle
        response = self.client.post(
            reverse('dealrooms:dealroom_file_assign', kwargs={'pk': self.deal.pk}),
            {
                'global_file_id': self.global_file.id,
                'role': 'logo'
            }
        )
        self.assertRedirects(response, reverse('dealrooms:dealroom_detail', kwargs={'pk': self.deal.pk}))
        
        # Prüfen ob nur eine Zuordnung existiert (mit aktualisierter Rolle)
        assignments = DealFileAssignment.objects.filter(
            deal=self.deal,
            global_file=self.global_file
        )
        self.assertEqual(assignments.count(), 1)
        self.assertEqual(assignments.first().role, 'logo')
    
    def test_unassign_file_view_requires_login(self):
        """Test: Datei entfernen erfordert Login"""
        # Erstelle eine Zuordnung
        assignment = DealFileAssignment.objects.create(
            deal=self.deal,
            global_file=self.global_file,
            role='hero_image',
            assigned_by=self.user
        )
        
        response = self.client.post(
            reverse('dealrooms:dealroom_file_unassign', kwargs={'pk': self.deal.pk}),
            {'assignment_id': assignment.id}
        )
        self.assertEqual(response.status_code, 302)  # Weiterleitung zum Login
    
    def test_unassign_file_view_success(self):
        """Test: Datei erfolgreich entfernen"""
        self.client.login(username='testuser', password='testpass123')
        
        # Erstelle eine Zuordnung
        assignment = DealFileAssignment.objects.create(
            deal=self.deal,
            global_file=self.global_file,
            role='hero_image',
            assigned_by=self.user
        )
        
        response = self.client.post(
            reverse('dealrooms:dealroom_file_unassign', kwargs={'pk': self.deal.pk}),
            {'assignment_id': assignment.id}
        )
        self.assertRedirects(response, reverse('dealrooms:dealroom_detail', kwargs={'pk': self.deal.pk}))
        
        # Prüfen ob Zuordnung gelöscht wurde
        self.assertFalse(DealFileAssignment.objects.filter(id=assignment.id).exists())
    
    def test_file_assignment_list_view_requires_login(self):
        """Test: Datei-Zuordnung-Liste erfordert Login"""
        response = self.client.get(
            reverse('dealrooms:dealroom_detail', kwargs={'pk': self.deal.pk})
        )
        self.assertEqual(response.status_code, 302)  # Weiterleitung zum Login
    
    def test_file_assignment_list_view_with_login(self):
        """Test: Datei-Zuordnung-Liste funktioniert mit Login"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(
            reverse('dealrooms:dealroom_detail', kwargs={'pk': self.deal.pk})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_file_assignment_list_view_without_permission(self):
        """Test: Datei-Zuordnung-Liste erfordert Berechtigung"""
        # Erstelle einen Benutzer ohne Bearbeitungsberechtigung
        restricted_user = User.objects.create_user(
            username='restricted',
            email='restricted@example.com',
            password='restricted123',
            role=User.UserRole.VIEWER
        )
        
        self.client.login(username='restricted', password='restricted123')
        
        response = self.client.get(
            reverse('dealrooms:dealroom_detail', kwargs={'pk': self.deal.pk})
        )
        self.assertEqual(response.status_code, 200)  # Sollte trotzdem zugänglich sein
    
    def test_file_assignment_list_context(self):
        """Test: Kontext der Datei-Zuordnung-Liste"""
        self.client.login(username='testuser', password='testpass123')
        
        # Erstelle eine Zuordnung
        assignment = DealFileAssignment.objects.create(
            deal=self.deal,
            global_file=self.global_file,
            role='hero_image',
            assigned_by=self.user
        )
        
        response = self.client.get(
            reverse('dealrooms:dealroom_detail', kwargs={'pk': self.deal.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # Prüfe Kontext-Daten
        context = response.context
        self.assertIn('deal', context)
        self.assertIn('change_logs', context)
    
    def test_website_generation_includes_download_section(self):
        """Test: Generierte Website enthält Download-Sektion für Dateien"""
        # Datei zuordnen
        assignment = DealFileAssignment.objects.create(
            deal=self.deal,
            global_file=self.global_file,
            assigned_by=self.user,
            role='document'
        )
        
        # Website generieren
        from generator.renderer import DealroomGenerator
        generator = DealroomGenerator(self.deal)
        html_content = generator.generate_website()
        
        # Prüfen ob Download-Sektion vorhanden ist
        self.assertIn('Downloads', html_content)
        self.assertIn('file-card', html_content)
        self.assertIn('btn-download', html_content)
        self.assertIn(self.global_file.title, html_content)
        self.assertIn('Herunterladen', html_content)


class DealFileAssignmentIntegrationTest(TestCase):
    """
    Integrationstests für die Datei-Zuordnung-Funktionalität
    """
    
    def setUp(self):
        """Test-Daten erstellen"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role=User.UserRole.EDITOR
        )
        
        self.deal = Deal.objects.create(
            title='Test Dealroom',
            slug='test-dealroom',
            description='Ein Test Dealroom',
            status=Deal.DealStatus.DRAFT,
            template_type=Deal.TemplateType.MODERN,
            created_by=self.user,
            recipient_name='Max Mustermann',
            recipient_email='max@example.com',
            hero_title='Willkommen',
            hero_subtitle='Ein toller Dealroom',
            call_to_action='Jetzt kontaktieren',
            primary_color='#0d6efd',
            secondary_color='#6c757d'
        )
        
        # Mehrere globale Dateien erstellen
        self.hero_file = GlobalFile.objects.create(
            title='Hero Bild',
            description='Ein Hero-Bild',
            file=SimpleUploadedFile(
                'hero.jpg',
                b'Hero image content',
                content_type='image/jpeg'
            ),
            file_type=GlobalFile.FileType.HERO_IMAGE,
            uploaded_by=self.user,
            is_public=True
        )
        
        self.logo_file = GlobalFile.objects.create(
            title='Logo',
            description='Ein Logo',
            file=SimpleUploadedFile(
                'logo.png',
                b'Logo content',
                content_type='image/png'
            ),
            file_type=GlobalFile.FileType.LOGO,
            uploaded_by=self.user,
            is_public=True
        )
        
        self.document_file = GlobalFile.objects.create(
            title='Dokument',
            description='Ein Dokument',
            file=SimpleUploadedFile(
                'document.pdf',
                b'Document content',
                content_type='application/pdf'
            ),
            file_type=GlobalFile.FileType.DOCUMENT,
            uploaded_by=self.user,
            is_public=True
        )
    
    def test_full_file_assignment_workflow(self):
        """Test: Vollständiger Workflow für Datei-Zuordnung"""
        self.client.login(username='testuser', password='testpass123')
        
        # 1. Deal-Detail-Seite aufrufen
        response = self.client.get(
            reverse('dealrooms:dealroom_detail', kwargs={'pk': self.deal.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # 2. Hero-Bild zuordnen
        response = self.client.post(
            reverse('dealrooms:dealroom_file_assign', kwargs={'pk': self.deal.pk}),
            {
                'global_file_id': self.hero_file.id,
                'role': 'hero_image'
            }
        )
        self.assertRedirects(response, reverse('dealrooms:dealroom_detail', kwargs={'pk': self.deal.pk}))
        
        # 3. Logo zuordnen
        response = self.client.post(
            reverse('dealrooms:dealroom_file_assign', kwargs={'pk': self.deal.pk}),
            {
                'global_file_id': self.logo_file.id,
                'role': 'logo'
            }
        )
        self.assertRedirects(response, reverse('dealrooms:dealroom_detail', kwargs={'pk': self.deal.pk}))
        
        # 4. Dokument zuordnen
        response = self.client.post(
            reverse('dealrooms:dealroom_file_assign', kwargs={'pk': self.deal.pk}),
            {
                'global_file_id': self.document_file.id,
                'role': 'document'
            }
        )
        self.assertRedirects(response, reverse('dealrooms:dealroom_detail', kwargs={'pk': self.deal.pk}))
        
        # 5. Prüfen ob alle Zuordnungen erstellt wurden
        assignments = DealFileAssignment.objects.filter(deal=self.deal)
        self.assertEqual(assignments.count(), 3)
        
        hero_assignment = assignments.filter(role='hero_image').first()
        logo_assignment = assignments.filter(role='logo').first()
        document_assignment = assignments.filter(role='document').first()
        
        self.assertIsNotNone(hero_assignment)
        self.assertIsNotNone(logo_assignment)
        self.assertIsNotNone(document_assignment)
        
        self.assertEqual(hero_assignment.global_file, self.hero_file)
        self.assertEqual(logo_assignment.global_file, self.logo_file)
        self.assertEqual(document_assignment.global_file, self.document_file)
        
        # 6. Prüfen ob Deal-Methoden korrekt funktionieren
        hero_images = self.deal.get_hero_images()
        logos = self.deal.get_logos()
        documents = self.deal.get_documents()
        
        self.assertEqual(hero_images.count(), 1)
        self.assertEqual(logos.count(), 1)
        self.assertEqual(documents.count(), 1)
        
        # 7. Datei entfernen
        response = self.client.post(
            reverse('dealrooms:dealroom_file_unassign', kwargs={'pk': self.deal.pk}),
            {'assignment_id': hero_assignment.id}
        )
        self.assertRedirects(response, reverse('dealrooms:dealroom_detail', kwargs={'pk': self.deal.pk}))
        
        # 8. Prüfen ob Datei entfernt wurde
        assignments_after = DealFileAssignment.objects.filter(deal=self.deal)
        self.assertEqual(assignments_after.count(), 2)
        
        hero_images_after = self.deal.get_hero_images()
        self.assertEqual(hero_images_after.count(), 0)
    
    def test_file_assignment_with_different_roles(self):
        """Test: Datei-Zuordnung mit verschiedenen Rollen"""
        self.client.login(username='testuser', password='testpass123')
        
        # Gleiche Datei mit verschiedenen Rollen zuordnen
        response1 = self.client.post(
            reverse('dealrooms:dealroom_file_assign', kwargs={'pk': self.deal.pk}),
            {
                'global_file_id': self.hero_file.id,
                'role': 'hero_image'
            }
        )
        
        response2 = self.client.post(
            reverse('dealrooms:dealroom_file_assign', kwargs={'pk': self.deal.pk}),
            {
                'global_file_id': self.hero_file.id,
                'role': 'logo'
            }
        )
        
        self.assertRedirects(response1, reverse('dealrooms:dealroom_detail', kwargs={'pk': self.deal.pk}))
        self.assertRedirects(response2, reverse('dealrooms:dealroom_detail', kwargs={'pk': self.deal.pk}))
        
        # Es sollte nur eine Zuordnung geben mit der letzten Rolle
        assignments = DealFileAssignment.objects.filter(
            deal=self.deal,
            global_file=self.hero_file
        )
        self.assertEqual(assignments.count(), 1)
        self.assertEqual(assignments.first().role, 'logo')
    
    def test_file_assignment_permissions(self):
        """Test: Berechtigungen für Datei-Zuordnung"""
        # Benutzer ohne EDITOR-Rolle erstellen
        viewer_user = User.objects.create_user(
            username='viewer',
            email='viewer@example.com',
            password='testpass123',
            role=User.UserRole.VIEWER
        )
        
        self.client.login(username='viewer', password='testpass123')
        
        # Versuch Datei zuzuordnen
        response = self.client.post(
            reverse('dealrooms:dealroom_file_assign', kwargs={'pk': self.deal.pk}),
            {
                'global_file_id': self.hero_file.id,
                'role': 'hero_image'
            }
        )
        
        # Sollte 403 Forbidden zurückgeben
        self.assertEqual(response.status_code, 403)
        
        # Prüfen ob keine Zuordnung erstellt wurde
        assignments = DealFileAssignment.objects.filter(deal=self.deal)
        self.assertEqual(assignments.count(), 0)
    
