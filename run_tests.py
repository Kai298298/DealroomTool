#!/usr/bin/env python3
"""
DealShare Test Runner - Automatisierte Test-Suite
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import execute_from_command_line

def setup_django():
    """Django Setup für Tests"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dealroom_dashboard.settings')
    django.setup()

def run_tests():
    """Führe alle Tests aus"""
    setup_django()
    
    # Test Runner konfigurieren
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    print("🧪 DealShare Test Suite wird gestartet...")
    print("=" * 60)
    
    # Test-Verzeichnisse definieren
    test_dirs = [
        'deals.tests',
        'users.tests',
        'files.tests',
        'core.tests',
    ]
    
    total_failures = 0
    total_errors = 0
    total_tests = 0
    
    for test_dir in test_dirs:
        print(f"\n📋 Teste {test_dir}...")
        print("-" * 40)
        
        try:
            failures, errors, tests_run = test_runner.run_tests([test_dir])
            total_failures += failures
            total_errors += errors
            total_tests += tests_run
            
            if failures == 0 and errors == 0:
                print(f"✅ {test_dir}: {tests_run} Tests erfolgreich")
            else:
                print(f"❌ {test_dir}: {failures} Fehler, {errors} Errors")
                
        except Exception as e:
            print(f"💥 Fehler beim Testen von {test_dir}: {e}")
            total_errors += 1
    
    # Zusammenfassung
    print("\n" + "=" * 60)
    print("📊 TEST-ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"Gesamt Tests: {total_tests}")
    print(f"Fehler: {total_failures}")
    print(f"Errors: {total_errors}")
    
    if total_failures == 0 and total_errors == 0:
        print("🎉 ALLE TESTS ERFOLGREICH!")
        return True
    else:
        print("❌ TESTS FEHLGESCHLAGEN!")
        return False

def run_specific_tests():
    """Führe spezifische Tests aus"""
    setup_django()
    
    print("🎯 Spezifische Tests...")
    
    # GrapesJS Tests
    print("\n🔧 GrapesJS Integration Tests...")
    os.system("python3 manage.py test deals.tests.GrapesJSIntegrationTests -v 2")
    
    # Dealroom Creation Tests
    print("\n🏗️ Dealroom Creation Tests...")
    os.system("python3 manage.py test deals.tests.DealroomCreationTests -v 2")
    
    # Integration Tests
    print("\n🔗 Integration Tests...")
    os.system("python3 manage.py test deals.tests.IntegrationTests -v 2")

def run_performance_tests():
    """Führe Performance Tests aus"""
    setup_django()
    
    print("⚡ Performance Tests...")
    os.system("python3 manage.py test deals.tests.PerformanceTests -v 2")

def run_security_tests():
    """Führe Security Tests aus"""
    setup_django()
    
    print("🔒 Security Tests...")
    os.system("python3 manage.py test deals.tests.SecurityTests -v 2")

def run_coverage_tests():
    """Führe Tests mit Coverage aus"""
    try:
        import coverage
        print("📊 Coverage Tests...")
        os.system("coverage run --source='.' manage.py test")
        os.system("coverage report")
        os.system("coverage html")
        print("📁 Coverage Report erstellt in htmlcov/")
    except ImportError:
        print("❌ Coverage nicht installiert. Installiere mit: pip install coverage")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'all':
            success = run_tests()
            sys.exit(0 if success else 1)
        elif command == 'specific':
            run_specific_tests()
        elif command == 'performance':
            run_performance_tests()
        elif command == 'security':
            run_security_tests()
        elif command == 'coverage':
            run_coverage_tests()
        else:
            print("Verwendung: python3 run_tests.py [all|specific|performance|security|coverage]")
    else:
        # Standard: Alle Tests
        success = run_tests()
        sys.exit(0 if success else 1) 