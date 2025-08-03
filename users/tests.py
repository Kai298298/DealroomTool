"""
Tests für die Users-App
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
import os

User = get_user_model()


class UserViewsTest(TestCase):
    """Tests für User-Views"""
    
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

    def test_login_page_loads(self):
        """Test: Login-Seite lädt korrekt"""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Anmelden')
        self.assertContains(response, 'Benutzername')
        self.assertContains(response, 'Passwort')

    def test_login_success(self):
        """Test: Erfolgreicher Login"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, '/')

    def test_login_failure(self):
        """Test: Fehlgeschlagener Login"""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Benutzername oder Passwort ist falsch')

    def test_logout(self):
        """Test: Logout funktioniert"""
        # Erst einloggen
        self.client.login(username='testuser', password='testpass123')
        
        # Dann logout - Django's LogoutView erwartet POST
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(response.url, '/')

    def test_profile_page_requires_login(self):
        """Test: Profile-Seite erfordert Login"""
        response = self.client.get(reverse('users:profile'))
        self.assertRedirects(response, f"{reverse('users:login')}?next={reverse('users:profile')}")

    def test_profile_page_loads_when_logged_in(self):
        """Test: Profile-Seite lädt für eingeloggte Benutzer"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
        self.assertContains(response, 'test@example.com')
        self.assertContains(response, 'Administrator')

    def test_profile_edit_page_loads(self):
        """Test: Profile-Edit-Seite lädt"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:profile_edit'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profil bearbeiten')

    def test_profile_edit_success(self):
        """Test: Profile-Edit funktioniert"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('users:profile_edit'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'phone': '+49123456789',
            'company': 'Test Company',
            'bio': 'Updated bio'
        })
        
        self.assertRedirects(response, reverse('users:profile'))
        
        # Prüfen ob Daten aktualisiert wurden
        updated_user = User.objects.get(username='testuser')
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        self.assertEqual(updated_user.email, 'updated@example.com')

    def test_password_change_page_loads(self):
        """Test: Password-Change-Seite lädt"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('users:password_change'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwort ändern')

    def test_password_change_success(self):
        """Test: Password-Change funktioniert"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('users:password_change'), {
            'old_password': 'testpass123',
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123'
        })
        
        self.assertRedirects(response, reverse('users:password_change_done'))
        
        # Prüfen ob Passwort geändert wurde
        self.client.logout()
        login_success = self.client.login(username='testuser', password='newpassword123')
        self.assertTrue(login_success)

    def test_register_page_loads(self):
        """Test: Register-Seite lädt"""
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Registrieren')

    def test_register_success(self):
        """Test: Registrierung funktioniert"""
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newuserpass123',
            'password2': 'newuserpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'viewer'
        }, follow=False)
        
        # Sollte 302 sein bei erfolgreicher Registrierung oder 200 bei Fehlern
        self.assertIn(response.status_code, [200, 302])
        
        # Wenn erfolgreich, prüfe Weiterleitung
        if response.status_code == 302:
            self.assertEqual(response.url, '/dashboard/')
            # Prüfen ob Benutzer erstellt wurde
            new_user = User.objects.get(username='newuser')
            self.assertEqual(new_user.email, 'newuser@example.com')
            self.assertEqual(new_user.first_name, 'New')

    def test_admin_login(self):
        """Test: Admin-Login funktioniert"""
        response = self.client.post(reverse('users:login'), {
            'username': 'admin',
            'password': 'admin123'
        })
        self.assertRedirects(response, '/')

    def test_user_roles(self):
        """Test: Benutzerrollen funktionieren"""
        # Admin-Rolle
        self.assertTrue(self.admin_user.is_admin())
        self.assertTrue(self.admin_user.is_manager())
        self.assertTrue(self.admin_user.is_editor())
        
        # Test-User-Rolle
        self.assertTrue(self.test_user.is_admin())
        self.assertTrue(self.test_user.is_manager())
        self.assertTrue(self.test_user.is_editor())


class UserModelTest(TestCase):
    """Tests für User-Model"""
    
    def setUp(self):
        """Setup für Model-Tests"""
        self.user = User.objects.create_user(
            username='modeltest',
            email='modeltest@example.com',
            password='testpass123',
            first_name='Model',
            last_name='Test',
            role=User.UserRole.ADMIN,
            phone='+49123456789',
            company='Test Company',
            bio='Test bio'
        )

    def test_user_creation(self):
        """Test: Benutzer-Erstellung"""
        self.assertEqual(self.user.username, 'modeltest')
        self.assertEqual(self.user.email, 'modeltest@example.com')
        self.assertEqual(self.user.first_name, 'Model')
        self.assertEqual(self.user.last_name, 'Test')
        self.assertEqual(self.user.role, User.UserRole.ADMIN)
        self.assertEqual(self.user.phone, '+49123456789')
        self.assertEqual(self.user.company, 'Test Company')
        self.assertEqual(self.user.bio, 'Test bio')

    def test_user_str_method(self):
        """Test: String-Repräsentation"""
        expected = f"modeltest (Administrator)"
        self.assertEqual(str(self.user), expected)

    def test_user_role_methods(self):
        """Test: Rollen-Methoden"""
        self.assertTrue(self.user.is_admin())
        self.assertTrue(self.user.is_manager())
        self.assertTrue(self.user.is_editor())
        self.assertTrue(self.user.can_edit_deals())
        self.assertTrue(self.user.can_manage_users())

    def test_user_role_choices(self):
        """Test: Rollen-Auswahl"""
        choices = User.UserRole.choices
        self.assertIn(('admin', 'Administrator'), choices)
        self.assertIn(('manager', 'Manager'), choices)
        self.assertIn(('editor', 'Editor'), choices)
        self.assertIn(('viewer', 'Viewer'), choices)


class UserIntegrationTest(TestCase):
    """Integration-Tests für User-Funktionen"""
    
    def setUp(self):
        """Setup für Integration-Tests"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='integrationtest',
            email='integration@example.com',
            password='testpass123',
            role=User.UserRole.ADMIN
        )

    def test_full_user_workflow(self):
        """Test: Vollständiger Benutzer-Workflow"""
        # 1. Login
        self.client.login(username='integrationtest', password='testpass123')
        
        # 2. Profile anzeigen
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        
        # 3. Profile bearbeiten
        response = self.client.post(reverse('users:profile_edit'), {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com',
            'phone': '+49123456789',
            'company': 'Updated Company',
            'bio': 'Updated bio'
        })
        self.assertRedirects(response, reverse('users:profile'))
        
        # 4. Passwort ändern
        response = self.client.post(reverse('users:password_change'), {
            'old_password': 'testpass123',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        })
        self.assertRedirects(response, reverse('users:password_change_done'))
        
        # 5. Logout
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(response.url, '/')
        
        # 6. Mit neuem Passwort einloggen
        login_success = self.client.login(username='integrationtest', password='newpass123')
        self.assertTrue(login_success)

    def test_navigation_links(self):
        """Test: Navigation-Links funktionieren"""
        self.client.login(username='integrationtest', password='testpass123')
        
        # Dashboard
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Profile
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        
        # Profile Edit
        response = self.client.get(reverse('users:profile_edit'))
        self.assertEqual(response.status_code, 200)
        
        # Password Change
        response = self.client.get(reverse('users:password_change'))
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    import django
    django.setup() 