"""
Tests für die Core-App
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from deals.models import Deal, DealChangeLog
from files.models import GlobalFile
from django.core.paginator import Paginator
from django.db.models import Q
import csv
from io import StringIO

User = get_user_model()


class CoreViewsTest(TestCase):
    """
    Tests für die Core-Views
    """
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role=User.UserRole.EDITOR
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            role=User.UserRole.ADMIN
        )
        
        # Test-Dealrooms erstellen
        self.deal1 = Deal.objects.create(
            title='Test Dealroom 1',
            slug='test-dealroom-1',
            description='Ein Test Dealroom',
            status='active',
            template_type='modern',
            recipient_name='Max Mustermann',
            recipient_email='max@example.com',
            created_by=self.user
        )
        
        self.deal2 = Deal.objects.create(
            title='Test Dealroom 2',
            slug='test-dealroom-2',
            description='Ein weiterer Test Dealroom',
            status='draft',
            template_type='classic',
            recipient_name='Anna Mustermann',
            recipient_email='anna@example.com',
            created_by=self.admin_user
        )
        
        # Test-Änderungen erstellen
        DealChangeLog.objects.create(
            deal=self.deal1,
            change_type=DealChangeLog.ChangeType.CREATED,
            changed_by=self.user,
            description='Dealroom erstellt'
        )
        
        # Test-Globale-Dateien erstellen
        self.global_file = GlobalFile.objects.create(
            title='Test Datei',
            description='Eine Test Datei',
            file_type='document',
            uploaded_by=self.user
        )
    
    def test_home_page_loads(self):
        """Test: Home-Seite lädt"""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)  # Zeigt Template für anonyme Benutzer
    
    def test_dashboard_requires_login(self):
        """Test: Dashboard erfordert Login"""
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)  # Weiterleitung zum Login
    
    def test_dashboard_loads_when_logged_in(self):
        """Test: Dashboard lädt für eingeloggte Benutzer"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'Test Dealroom 1')
        self.assertContains(response, 'Test Dealroom 2')
    
    def test_csv_export_requires_login(self):
        """Test: CSV-Export erfordert Login"""
        response = self.client.get(reverse('core:csv_export'))
        self.assertEqual(response.status_code, 302)  # Weiterleitung zum Login
    
    def test_csv_export_loads_when_logged_in(self):
        """Test: CSV-Export lädt für eingeloggte Benutzer"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:csv_export'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('dealrooms_export_', response['Content-Disposition'])
    
    def test_csv_export_contains_correct_data(self):
        """Test: CSV-Export enthält korrekte Daten"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:csv_export'))
        
        # CSV-Daten parsen
        csv_content = response.content.decode('utf-8')
        csv_reader = csv.reader(StringIO(csv_content), delimiter=';')
        rows = list(csv_reader)
        
        # Header prüfen
        self.assertEqual(len(rows), 3)  # Header + 2 Dealrooms
        header = rows[0]
        expected_headers = [
            'ID', 'Titel', 'Slug', 'Beschreibung', 'Status', 'Template-Typ',
            'Empfänger Name', 'Empfänger E-Mail', 'Empfänger Firma',
            'Hero Titel', 'Hero Untertitel', 'Call-to-Action',
            'Primärfarbe', 'Sekundärfarbe', 'Website Status',
            'Öffentliche URL', 'Lokale Website URL',
            'Erstellt von', 'Erstellt am', 'Aktualisiert von', 'Aktualisiert am',
            'Anzahl Dateien', 'Anzahl Änderungen'
        ]
        self.assertEqual(header, expected_headers)
        
        # Daten prüfen (Reihenfolge kann variieren, daher prüfen wir beide)
        dealroom1_data = rows[1]
        dealroom2_data = rows[2]
        
        # Prüfe, dass beide Dealrooms vorhanden sind
        titles = [dealroom1_data[1], dealroom2_data[1]]
        self.assertIn('Test Dealroom 1', titles)
        self.assertIn('Test Dealroom 2', titles)
        
        # Prüfe spezifische Werte für einen der Dealrooms
        if dealroom1_data[1] == 'Test Dealroom 1':
            self.assertEqual(dealroom1_data[2], 'test-dealroom-1')  # Slug
            self.assertEqual(dealroom1_data[4], 'Aktiv')  # Status
            self.assertEqual(dealroom1_data[5], 'Modern')  # Template-Typ
            self.assertEqual(dealroom1_data[6], 'Max Mustermann')  # Empfänger Name
            self.assertEqual(dealroom1_data[7], 'max@example.com')  # Empfänger E-Mail
        else:
            self.assertEqual(dealroom2_data[2], 'test-dealroom-1')  # Slug
            self.assertEqual(dealroom2_data[4], 'Aktiv')  # Status
            self.assertEqual(dealroom2_data[5], 'Modern')  # Template-Typ
            self.assertEqual(dealroom2_data[6], 'Max Mustermann')  # Empfänger Name
            self.assertEqual(dealroom2_data[7], 'max@example.com')  # Empfänger E-Mail
    
    def test_csv_export_filename_format(self):
        """Test: CSV-Export Dateiname hat korrektes Format"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:csv_export'))
        
        content_disposition = response['Content-Disposition']
        self.assertIn('attachment', content_disposition)
        self.assertIn('dealrooms_export_', content_disposition)
        self.assertIn('.csv', content_disposition)
    
    def test_dashboard_search_functionality(self):
        """Test: Suchfunktionalität im Dashboard"""
        self.client.login(username='testuser', password='testpass123')
        
        # Suche nach Dealroom 1
        response = self.client.get(reverse('core:dashboard'), {'search': 'Test Dealroom 1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dealroom 1')
        self.assertNotContains(response, 'Test Dealroom 2')
        
        # Suche nach Empfänger
        response = self.client.get(reverse('core:dashboard'), {'search': 'Max Mustermann'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Dealroom 1')
        
        # Suche nach nicht existierendem Dealroom
        response = self.client.get(reverse('core:dashboard'), {'search': 'Nicht existierend'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Keine Dealrooms gefunden')
    
    def test_dashboard_pagination(self):
        """Test: Pagination im Dashboard"""
        self.client.login(username='testuser', password='testpass123')
        
        # Erstelle mehr Dealrooms für Pagination
        for i in range(15):
            Deal.objects.create(
                title=f'Dealroom {i}',
                slug=f'dealroom-{i}',
                description=f'Dealroom {i} Beschreibung',
                status='active',
                template_type='modern',
                recipient_name=f'Empfänger {i}',
                recipient_email=f'empfaenger{i}@example.com',
                created_by=self.user
            )
        
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        # Prüfe, dass Pagination vorhanden ist
        self.assertContains(response, 'chevron-right')
    
    def test_dashboard_context_data(self):
        """Test: Dashboard-Kontext enthält alle benötigten Daten"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        
        # Prüfe Kontext-Daten
        context = response.context
        self.assertIn('deals', context)
        self.assertIn('active_deals', context)
        self.assertIn('draft_deals', context)
        self.assertIn('global_files', context)
        self.assertIn('recent_global_files', context)
        self.assertIn('recent_changes', context)
        self.assertIn('dealrooms', context)
        self.assertIn('paginator', context)
        self.assertIn('search_query', context)
        
        # Prüfe spezifische Werte
        self.assertEqual(context['deals'].count(), 2)
        self.assertEqual(context['active_deals'].count(), 1)
        self.assertEqual(context['draft_deals'].count(), 1)
        self.assertEqual(context['global_files'].count(), 1)
        self.assertEqual(context['recent_changes'].count(), 1)
    
    def test_admin_context_in_dashboard(self):
        """Test: Admin-Kontext im Dashboard"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin User')  # Zeigt den vollständigen Namen an
    
    def test_user_context_in_dashboard(self):
        """Test: Benutzer-Kontext im Dashboard"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
    
    def test_admin_login_redirects_to_dashboard(self):
        """Test: Admin-Login leitet zum Dashboard weiter"""
        response = self.client.post(reverse('users:login'), {
            'username': 'admin',
            'password': 'adminpass123'
        })
        self.assertRedirects(response, reverse('core:dashboard'))
    
    def test_login_success_redirects_to_dashboard(self):
        """Test: Login leitet zum Dashboard weiter"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('core:dashboard'))
    
    def test_navigation_links_for_anonymous_user(self):
        """Test: Navigation-Links für anonyme Benutzer"""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)  # Zeigt Template für anonyme Benutzer
    
    def test_navigation_links_for_authenticated_user(self):
        """Test: Navigation-Links für eingeloggte Benutzer"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'Dateien')
        # Dealrooms sollte nur im Dashboard-Inhalt sein, nicht in der Navigation
        self.assertContains(response, 'Dealrooms')  # Im Dashboard-Inhalt
    
    def test_about_page_loads(self):
        """Test: About-Seite lädt"""
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Über')
    
    def test_help_page_loads(self):
        """Test: Help-Seite lädt"""
        response = self.client.get(reverse('core:help'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hilfe')
    
    def test_impressum_page_loads(self):
        """Test: Impressum-Seite lädt"""
        response = self.client.get(reverse('core:impressum'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Impressum')


class CoreIntegrationTest(TestCase):
    """
    Integrationstests für die Core-App
    """
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='integrationtest',
            email='integration@example.com',
            password='integrationpass123',
            first_name='Integration',
            last_name='Test',
            role=User.UserRole.ADMIN
        )
    
    def test_full_user_journey(self):
        """Test: Vollständiger Benutzer-Journey"""
        # 1. Startseite (anonyme Benutzer sehen das Template)
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)  # Zeigt Template für anonyme Benutzer
        
        # 2. Login
        response = self.client.post(reverse('users:login'), {
            'username': 'integrationtest',
            'password': 'integrationpass123'
        })
        self.assertRedirects(response, reverse('core:dashboard'))
        
        # 3. Dashboard
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'Integration Test')
        
        # 4. Navigation funktioniert
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('core:help'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('core:impressum'))
        self.assertEqual(response.status_code, 200)
        
        # 5. Logout
        response = self.client.post(reverse('users:logout'))
        # Logout leitet zur Home-Seite weiter, die wiederum zum Dashboard weiterleitet
        self.assertEqual(response.status_code, 302)
        
        # 6. Nach Logout keine Dashboard-Zugriff
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)  # Weiterleitung zum Login
    
    def test_static_pages_content(self):
        """Test: Statische Seiten haben korrekten Inhalt"""
        self.client.login(username='integrationtest', password='integrationpass123')
        
        # About-Seite
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Über')
        
        # Help-Seite
        response = self.client.get(reverse('core:help'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hilfe')
        
        # Impressum-Seite
        response = self.client.get(reverse('core:impressum'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Impressum')
    
    def test_template_inheritance(self):
        """Test: Template-Vererbung funktioniert"""
        self.client.login(username='integrationtest', password='integrationpass123')
        
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Prüfe, dass base.html verwendet wird
        self.assertContains(response, 'Dealroom Dashboard')  # Aus base.html
        self.assertContains(response, 'Dashboard')  # Aus dashboard.html 