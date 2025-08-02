from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import CustomUser
from deals.models import Deal


class Command(BaseCommand):
    help = 'Erstellt Willkommens-Dealrooms für alle User, die noch keinen haben'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Erstellt Willkommens-Dealrooms auch für User, die bereits einen haben',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Erstellt Willkommens-Dealroom nur für einen spezifischen User',
        )

    def handle(self, *args, **options):
        force = options['force']
        specific_user = options['user']
        
        self.stdout.write("🚀 Starte Erstellung von Willkommens-Dealrooms...")
        
        if specific_user:
            try:
                user = CustomUser.objects.get(username=specific_user)
                users_to_process = [user]
                self.stdout.write(f"📝 Verarbeite nur User: {user.username}")
            except CustomUser.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ User '{specific_user}' nicht gefunden"))
                return
        else:
            # Alle User ohne Superuser
            users_to_process = CustomUser.objects.filter(is_superuser=False)
            self.stdout.write(f"📝 Gefunden: {users_to_process.count()} User")
        
        created_count = 0
        skipped_count = 0
        
        for user in users_to_process:
            try:
                with transaction.atomic():
                    # Prüfen ob User bereits einen Willkommens-Dealroom hat
                    existing_welcome = Deal.objects.filter(
                        created_by=user,
                        title='Willkommen bei DealShare'
                    ).first()
                    
                    if existing_welcome and not force:
                        self.stdout.write(f"⏭️ Überspringe {user.username} (hat bereits Willkommens-Dealroom)")
                        skipped_count += 1
                        continue
                    
                    # Willkommens-Dealroom erstellen
                    welcome_deal = Deal.objects.create(
                        title='Willkommen bei DealShare',
                        slug=f'welcome-dealshare-{user.username}',
                        company_name='DealShare',
                        description='Entdecken Sie die Möglichkeiten von DealShare - der modernsten Plattform für professionelle Dealrooms und Landingpages.',
                        hero_title='Die Zukunft der Dealroom-Erstellung',
                        hero_subtitle='Erstellen Sie beeindruckende Landingpages in Minuten, nicht in Stunden',
                        deal_progress=100,
                        status='active',
                        template_type='modern',
                        theme_type='light',
                        created_by=user,
                        # Marketing-spezifische Felder
                        welcome_message='Willkommen bei DealShare! Entdecken Sie, wie einfach es ist, professionelle Dealrooms zu erstellen.',
                        call_to_action='Jetzt Dealroom erstellen',
                        # SEO-Felder
                        meta_title='DealShare - Professionelle Dealroom-Erstellung',
                        meta_description='Erstellen Sie beeindruckende Landingpages für Ihre Deals mit DealShare. Modern, schnell und professionell.',
                        # Custom HTML für Marketing
                        custom_html_content='''
                        <div class="welcome-section">
                            <div class="container">
                                <div class="row">
                                    <div class="col-lg-8 mx-auto text-center">
                                        <h2 class="display-4 mb-4">🚀 Willkommen bei DealShare</h2>
                                        <p class="lead mb-4">
                                            Erstellen Sie professionelle Dealrooms und Landingpages in wenigen Minuten. 
                                            Keine Programmierkenntnisse erforderlich!
                                        </p>
                                        
                                        <div class="features-grid mt-5">
                                            <div class="row">
                                                <div class="col-md-4">
                                                    <div class="feature-card">
                                                        <i class="bi bi-lightning-charge text-primary fs-1"></i>
                                                        <h4>Schnell & Einfach</h4>
                                                        <p>Erstellen Sie Landingpages in Minuten</p>
                                                    </div>
                                                </div>
                                                <div class="col-md-4">
                                                    <div class="feature-card">
                                                        <i class="bi bi-palette text-success fs-1"></i>
                                                        <h4>Professionelle Templates</h4>
                                                        <p>Moderne Designs für jeden Anlass</p>
                                                    </div>
                                                </div>
                                                <div class="col-md-4">
                                                    <div class="feature-card">
                                                        <i class="bi bi-shield-check text-warning fs-1"></i>
                                                        <h4>Sicher & DSGVO-konform</h4>
                                                        <p>Ihre Daten sind bei uns sicher</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="cta-section mt-5">
                                            <a href="/deals/create/" class="btn btn-primary btn-lg me-3">
                                                <i class="bi bi-plus-circle me-2"></i>Ersten Dealroom erstellen
                                            </a>
                                            <a href="/users/pricing/" class="btn btn-outline-primary btn-lg">
                                                <i class="bi bi-credit-card me-2"></i>Pläne ansehen
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        ''',
                        custom_css='''
                        .welcome-section {
                            padding: 4rem 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                        }
                        .feature-card {
                            text-align: center;
                            padding: 2rem 1rem;
                            background: rgba(255,255,255,0.1);
                            border-radius: 10px;
                            margin-bottom: 1rem;
                        }
                        .feature-card h4 {
                            margin: 1rem 0;
                            color: white;
                        }
                        .feature-card p {
                            color: rgba(255,255,255,0.8);
                        }
                        .cta-section {
                            margin-top: 3rem;
                        }
                        '''
                    )
                    
                    self.stdout.write(f"✅ Willkommens-Dealroom für {user.username} erstellt: {welcome_deal.title}")
                    created_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Fehler beim Erstellen für {user.username}: {e}")
                )
        
        # Zusammenfassung
        self.stdout.write("\n" + "="*50)
        self.stdout.write("📊 Zusammenfassung:")
        self.stdout.write(f"✅ Erstellt: {created_count} Willkommens-Dealrooms")
        self.stdout.write(f"⏭️ Übersprungen: {skipped_count} User")
        self.stdout.write(f"📝 Gesamt verarbeitet: {created_count + skipped_count} User")
        self.stdout.write("="*50)
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"\n🎉 Erfolgreich {created_count} Willkommens-Dealrooms erstellt!")
            )
        else:
            self.stdout.write("\nℹ️ Keine neuen Willkommens-Dealrooms erstellt.") 