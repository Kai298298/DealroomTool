#!/usr/bin/env python3
"""
DealShare GrapesJS & Core Features Test Runner
"""
import os
import sys
import django
from django.test import TestCase
from django.test.utils import get_runner
from django.conf import settings

def setup_django():
    """Django Setup für Tests"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dealroom_dashboard.settings')
    django.setup()

def run_grapesjs_tests():
    """Führe GrapesJS und Core Tests aus"""
    setup_django()
    
    print("🎨 DealShare GrapesJS & Core Features Test Suite")
    print("=" * 60)
    
    # Test Runner konfigurieren
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Spezifische Test-Klassen
    test_classes = [
        'deals.tests.GrapesJSIntegrationTests',
        'deals.tests.DealModelTests', 
        'deals.tests.DealroomCreationTests',
        'deals.tests.IntegrationTests',
        'deals.tests.PerformanceTests',
        'deals.tests.SecurityTests'
    ]
    
    total_failures = 0
    total_errors = 0
    total_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 Teste {test_class}...")
        print("-" * 40)
        
        try:
            failures, errors, tests_run = test_runner.run_tests([test_class])
            total_failures += failures
            total_errors += errors
            total_tests += tests_run
            
            if failures == 0 and errors == 0:
                print(f"✅ {test_class}: {tests_run} Tests erfolgreich")
            else:
                print(f"❌ {test_class}: {failures} Fehler, {errors} Errors")
                
        except Exception as e:
            print(f"💥 Fehler beim Testen von {test_class}: {e}")
            total_errors += 1
    
    # Zusammenfassung
    print("\n" + "=" * 60)
    print("📊 TEST-ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"Gesamt Tests: {total_tests}")
    print(f"Fehler: {total_failures}")
    print(f"Errors: {total_errors}")
    
    if total_failures == 0 and total_errors == 0:
        print("🎉 ALLE GRAPESJS & CORE TESTS ERFOLGREICH!")
        return True
    else:
        print("❌ TESTS FEHLGESCHLAGEN!")
        return False

def run_specific_test(test_name):
    """Führe einen spezifischen Test aus"""
    setup_django()
    
    print(f"🎯 Teste {test_name}...")
    os.system(f"python3 manage.py test {test_name} -v 2")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'grapesjs':
            success = run_grapesjs_tests()
            sys.exit(0 if success else 1)
        elif command == 'specific':
            if len(sys.argv) > 2:
                test_name = sys.argv[2]
                run_specific_test(test_name)
            else:
                print("Verwendung: python3 test_grapesjs.py specific <test_name>")
        else:
            print("Verwendung: python3 test_grapesjs.py [grapesjs|specific <test_name>]")
    else:
        # Standard: GrapesJS Tests
        success = run_grapesjs_tests()
        sys.exit(0 if success else 1) 