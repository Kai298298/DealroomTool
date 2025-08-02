"""
Tests für die Core-App
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import CustomUser

User = get_user_model()


class CoreViewsTest(TestCase):
    """Tests für Core-Views"""
    
    def setUp(self):
        """Setup für Tests"""
        self.client = Client()
        
        # Test-Benutzer erstellen
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role=User.UserRole.ADMIN
        )
        
        # Admin-Benutzer erstellen
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.admin_user.role = User.UserRole.ADMIN
        self.admin_user.save()

    def test_home_page_loads(self):
        """Test: Home-Seite lädt"""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dealroom Dashboard')

    def test_dashboard_requires_login(self):
        """Test: Dashboard erfordert Login"""
        response = self.client.get(reverse('core:dashboard'))
        self.assertRedirects(response, f"{reverse('users:login')}?next={reverse('core:dashboard')}")

    def test_dashboard_loads_when_logged_in(self):
        """Test: Dashboard lädt für eingeloggte Benutzer"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

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

    def test_login_success_redirects_to_dashboard(self):
        """Test: Login leitet zum Dashboard weiter"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('core:dashboard'))

    def test_admin_login_redirects_to_dashboard(self):
        """Test: Admin-Login leitet zum Dashboard weiter"""
        response = self.client.post(reverse('users:login'), {
            'username': 'admin',
            'password': 'admin123'
        })
        self.assertRedirects(response, reverse('core:dashboard'))

    def test_navigation_links_for_authenticated_user(self):
        """Test: Navigation-Links für eingeloggte Benutzer"""
        self.client.login(username='testuser', password='testpass123')
        
        # Dashboard
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # About
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        
        # Help
        response = self.client.get(reverse('core:help'))
        self.assertEqual(response.status_code, 200)
        
        # Impressum
        response = self.client.get(reverse('core:impressum'))
        self.assertEqual(response.status_code, 200)

    def test_navigation_links_for_anonymous_user(self):
        """Test: Navigation-Links für anonyme Benutzer"""
        # Home
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        
        # About
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        
        # Help
        response = self.client.get(reverse('core:help'))
        self.assertEqual(response.status_code, 200)
        
        # Impressum
        response = self.client.get(reverse('core:impressum'))
        self.assertEqual(response.status_code, 200)

    def test_user_context_in_dashboard(self):
        """Test: Benutzer-Kontext im Dashboard"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'Test User')

    def test_admin_context_in_dashboard(self):
        """Test: Admin-Kontext im Dashboard"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'admin')
        self.assertContains(response, 'Administrator')


class CoreIntegrationTest(TestCase):
    """Integration-Tests für Core-Funktionen"""
    
    def setUp(self):
        """Setup für Integration-Tests"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='integrationtest',
            email='integration@example.com',
            password='testpass123',
            role=User.UserRole.ADMIN
        )

    def test_full_user_journey(self):
        """Test: Vollständiger Benutzer-Journey"""
        # 1. Anonyme Benutzer sehen Home-Seite
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Dashboard erfordert Login
        response = self.client.get(reverse('core:dashboard'))
        self.assertRedirects(response, f"{reverse('users:login')}?next={reverse('core:dashboard')}")
        
        # 3. Login
        response = self.client.post(reverse('users:login'), {
            'username': 'integrationtest',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('core:dashboard'))
        
        # 4. Dashboard ist jetzt zugänglich
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # 5. Navigation funktioniert
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('core:help'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('core:impressum'))
        self.assertEqual(response.status_code, 200)
        
        # 6. Logout
        response = self.client.get(reverse('users:logout'))
        self.assertRedirects(response, '/')
        
        # 7. Dashboard wieder nicht zugänglich
        response = self.client.get(reverse('core:dashboard'))
        self.assertRedirects(response, f"{reverse('users:login')}?next={reverse('core:dashboard')}")

    def test_static_pages_content(self):
        """Test: Statische Seiten haben korrekten Inhalt"""
        # About-Seite
        response = self.client.get(reverse('core:about'))
        self.assertContains(response, 'Über')
        
        # Help-Seite
        response = self.client.get(reverse('core:help'))
        self.assertContains(response, 'Hilfe')
        
        # Impressum-Seite
        response = self.client.get(reverse('core:impressum'))
        self.assertContains(response, 'Impressum')

    def test_template_inheritance(self):
        """Test: Template-Vererbung funktioniert"""
        self.client.login(username='integrationtest', password='testpass123')
        
        # Alle Seiten sollten das Base-Template verwenden
        pages = [
            reverse('core:dashboard'),
            reverse('core:about'),
            reverse('core:help'),
            reverse('core:impressum'),
        ]
        
        for page in pages:
            response = self.client.get(page)
            self.assertEqual(response.status_code, 200)
            # Prüfen ob Bootstrap und andere Base-Template-Elemente vorhanden sind
            self.assertContains(response, 'bootstrap')
            self.assertContains(response, 'container')


if __name__ == '__main__':
    import django
    django.setup() 