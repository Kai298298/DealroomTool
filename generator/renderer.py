"""
Website-Renderer für Dealroom-Generierung
========================================

Hauptkomponente für die Generierung von Websites aus Dealroom-Daten.
"""

import os
from typing import Optional
from .css_generator import CSSGenerator
from .video_processor import VideoProcessor
from .image_processor import ImageProcessor
from .utils import create_directory, sanitize_filename
from django.conf import settings


class DealroomGenerator:
    """
    Generiert Websites aus Dealroom-Daten
    """
    
    def __init__(self, dealroom):
        """
        Initialisiert den Generator
        
        Args:
            dealroom: Dealroom-Objekt
        """
        self.dealroom = dealroom
        self.css_generator = CSSGenerator(dealroom)
        self.video_processor = VideoProcessor()
        self.image_processor = ImageProcessor()
        
    def generate_website(self) -> str:
        """Generiert die komplette Website"""
        try:
            # HTML-Editor-Modus prüfen
            if self.dealroom.html_editor_mode == 'manual':
                return self._generate_manual_html()
            elif self.dealroom.html_editor_mode == 'hybrid':
                return self._generate_hybrid_html()
            else:
                return self._generate_auto_html()
        except Exception as e:
            error_msg = f"Fehler bei der Website-Generierung: {str(e)}"
            print(f"❌ {error_msg}")
            return f"<html><body><h1>Generierungsfehler</h1><p>{error_msg}</p></body></html>"
    
    def _generate_manual_html(self) -> str:
        """Generiert HTML nur aus manuellen Eingaben"""
        html_parts = []
        
        # HTML-Header
        html_parts.append('<!DOCTYPE html>')
        html_parts.append('<html lang="de">')
        html_parts.append('<head>')
        html_parts.append('<meta charset="UTF-8">')
        html_parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html_parts.append(f'<title>{self.dealroom.title}</title>')
        
        # Benutzerdefinierter HTML-Header
        if self.dealroom.custom_html_header:
            html_parts.append(self.dealroom.custom_html_header)
        
        # Standard-CSS einbinden
        html_parts.append('<link rel="stylesheet" href="style.css">')
        
        # Benutzerdefiniertes CSS
        if self.dealroom.custom_css:
            html_parts.append(f'<style>{self.dealroom.custom_css}</style>')
        
        html_parts.append('</head>')
        html_parts.append('<body>')
        
        # Benutzerdefinierter Body-Start
        if self.dealroom.custom_html_body_start:
            html_parts.append(self.dealroom.custom_html_body_start)
        
        # Benutzerdefinierter Content
        if self.dealroom.custom_html_content:
            html_parts.append(self.dealroom.custom_html_content)
        else:
            html_parts.append('<div class="container"><h1>Kein Content definiert</h1></div>')
        
        # Benutzerdefinierter Body-End
        if self.dealroom.custom_html_body_end:
            html_parts.append(self.dealroom.custom_html_body_end)
        
        # Benutzerdefiniertes JavaScript
        if self.dealroom.custom_javascript:
            html_parts.append(f'<script>{self.dealroom.custom_javascript}</script>')
        
        html_parts.append('</body>')
        html_parts.append('</html>')
        
        return '\n'.join(html_parts)
    
    def _generate_hybrid_html(self) -> str:
        """Generiert HTML aus automatisch generiertem + manuellen Anpassungen"""
        # Automatisch generiertes HTML
        auto_html = self._generate_auto_html()
        
        # Manuelle Anpassungen einfügen
        if self.dealroom.custom_html_header:
            # Header-Anpassungen
            auto_html = auto_html.replace('</head>', f'{self.dealroom.custom_html_header}\n</head>')
        
        if self.dealroom.custom_css:
            # CSS-Anpassungen
            auto_html = auto_html.replace('</head>', f'<style>{self.dealroom.custom_css}</style>\n</head>')
        
        if self.dealroom.custom_html_body_start:
            # Body-Start Anpassungen
            auto_html = auto_html.replace('<body>', f'<body>\n{self.dealroom.custom_html_body_start}')
        
        if self.dealroom.custom_html_content:
            # Content-Anpassungen (ersetze automatischen Content)
            # Hier müsste eine intelligentere Logik implementiert werden
            pass
        
        if self.dealroom.custom_html_body_end:
            # Body-End Anpassungen
            auto_html = auto_html.replace('</body>', f'{self.dealroom.custom_html_body_end}\n</body>')
        
        if self.dealroom.custom_javascript:
            # JavaScript-Anpassungen
            auto_html = auto_html.replace('</body>', f'<script>{self.dealroom.custom_javascript}</script>\n</body>')
        
        return auto_html
    
    def _generate_auto_html(self) -> str:
        """Generiert HTML automatisch (bestehende Logik)"""
        html_parts = []
        
        # HTML-Header
        html_parts.append(self._generate_html_header())
        
        # Body-Start
        html_parts.append(self._generate_body_start())
        
        # Content-Sections
        html_parts.append(self._generate_content_sections())
        
        # Files Download Section
        html_parts.append(self._generate_files_download_section())
        
        # Body-End
        html_parts.append(self._generate_body_end())
        
        return '\n'.join(html_parts)
    
    def _generate_html_header(self) -> str:
        """Generiert HTML-Header"""
        meta_title = self.dealroom.meta_title or self.dealroom.title
        meta_description = self.dealroom.meta_description or self.dealroom.description or ''
        
        return f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta_title}</title>
    <meta name="description" content="{meta_description}">
    <meta name="keywords" content="Dealroom, {self.dealroom.title}, Business">
    <meta name="author" content="{self.dealroom.created_by.get_full_name() or self.dealroom.created_by.username}">
    <meta property="og:title" content="{meta_title}">
    <meta property="og:description" content="{meta_description}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{self.get_website_url()}">
    <link rel="canonical" href="{self.get_website_url()}">
</head>'''
    
    def _generate_css(self) -> str:
        """Generiert CSS"""
        return f'<style>\n{self.css_generator.generate_css()}\n</style>'
    
    def _generate_body_start(self) -> str:
        """Generiert Body-Start"""
        return '<body>'
    
    def _generate_header(self) -> str:
        """Generiert Header-Bereich"""
        return f'''
        <header class="header">
            <div class="container">
                <nav class="nav">
                    <div class="logo">{self.dealroom.title}</div>
                </nav>
            </div>
        </header>'''
    
    def _generate_hero_section(self) -> str:
        """Generiert Hero-Section"""
        hero_html = f'''
        <section class="hero">
            <div class="container">
                <h1>{self.dealroom.hero_title or self.dealroom.title}</h1>
                <p>{self.dealroom.hero_subtitle or ''}</p>'''
        
        # Hero-Bild hinzufügen falls vorhanden
        hero_images = self.dealroom.get_hero_images()
        if hero_images:
            hero_image = hero_images.first()
            if hero_image and hero_image.get_actual_file():
                hero_html += f'''
                <div class="hero-image">
                    <img src="{hero_image.get_file_url()}" alt="Hero-Bild" class="hero-img">
                </div>'''
        
        # Video hinzufügen falls vorhanden
        if self.dealroom.central_video_url:
            video_embed = self.video_processor.create_embed_code(self.dealroom.central_video_url)
            hero_html += f'''
            <div class="hero-video">
                {video_embed}
            </div>'''
        
        if self.dealroom.call_to_action:
            hero_html += f'<a href="#" class="btn">{self.dealroom.call_to_action}</a>'
        
        hero_html += '''
            </div>
        </section>'''
        
        return hero_html
    
    def _generate_content_sections(self) -> str:
        """Generiert erweiterte Content-Bereiche für Landingpage"""
        content_html = '''
        <main class="content">
            <div class="container">'''
        
        # 1. Begrüßungsbox / Header
        content_html += self._generate_welcome_section()

        # 2. Produktbeschreibung
        content_html += self._generate_product_section()

        # 3. Deal-Status & Fortschritt
        content_html += self._generate_deal_status_section()

        # 4. Wichtige Dokumente & Informationen
        content_html += self._generate_documents_section()
        
        # 5. Aufgaben & To-Dos für den Kunden
        content_html += self._generate_tasks_section()
        
        # 5. Kommunikation & Kontakt
        content_html += self._generate_communication_section()
        
        # 6. Team & Stakeholder-Übersicht
        content_html += self._generate_team_section()
        
        # 7. Zeitachse / Aktivitätenprotokoll
        content_html += self._generate_timeline_section()
        
        # 8. Hilfs- & Erklärungsbereich / FAQ
        content_html += self._generate_faq_section()
        
        # 9. Call-to-Action / Abschlussbutton
        content_html += self._generate_cta_section()
        
        content_html += '''
            </div>
        </main>'''
        
        return content_html
    
    def _generate_welcome_section(self) -> str:
        """Generiert Begrüßungsbox / Header"""
        welcome_html = '''
            <section class="section welcome-section">
                <div class="card">
                    <div class="welcome-header">
                        <div class="welcome-logo">
                            <img src="https://via.placeholder.com/100x50/007bff/ffffff?text=LOGO" alt="Logo" class="logo-img">
                        </div>
                        <div class="welcome-content">
                            <h1>Willkommen im Dealroom</h1>'''
        
        if hasattr(self.dealroom, 'welcome_message') and self.dealroom.welcome_message:
            welcome_html += f'<p class="welcome-message">{self.dealroom.welcome_message}</p>'
        else:
            welcome_html += f'<p class="welcome-message">Willkommen bei {self.dealroom.title}!</p>'
        
        if self.dealroom.recipient_name:
            welcome_html += f'<p class="customer-name">Hallo {self.dealroom.recipient_name}!</p>'
        
        welcome_html += '''
                        </div>
                    </div>
                </div>
            </section>'''
        
        return welcome_html
    
    def _generate_product_section(self) -> str:
        """Generiert Produktbeschreibung & Details"""
        product_name = getattr(self.dealroom, 'product_name', '')
        product_description = getattr(self.dealroom, 'product_description', '')
        product_features = getattr(self.dealroom, 'product_features', [])
        product_price = getattr(self.dealroom, 'product_price', None)
        product_currency = getattr(self.dealroom, 'product_currency', 'EUR')
        
        if not product_name and not product_description:
            return ''
        
        product_html = '''
            <section class="section">
                <div class="card">
                    <h2>Produktbeschreibung</h2>
                    <div class="product-details">'''
        
        if product_name:
            product_html += f'''
                        <div class="product-header">
                            <h3>{product_name}</h3>'''
            
            if product_price:
                currency_symbol = {'EUR': '€', 'USD': '$', 'CHF': 'CHF'}.get(product_currency, product_currency)
                product_html += f'<div class="product-price">{currency_symbol} {product_price:,.2f}</div>'
            
            product_html += '''
                        </div>'''
        
        if product_description:
            product_html += f'''
                        <div class="product-description">
                            <p>{product_description}</p>
                        </div>'''
        
        if product_features:
            product_html += '''
                        <div class="product-features">
                            <h4>Produktfeatures</h4>
                            <ul class="features-list">'''
            
            for feature in product_features:
                if isinstance(feature, dict):
                    feature_text = feature.get('text', '')
                    feature_icon = feature.get('icon', '✓')
                else:
                    feature_text = str(feature)
                    feature_icon = '✓'
                
                if feature_text:
                    product_html += f'''
                                <li class="feature-item">
                                    <span class="feature-icon">{feature_icon}</span>
                                    <span class="feature-text">{feature_text}</span>
                                </li>'''
            
            product_html += '''
                            </ul>
                        </div>'''
        
        product_html += '''
                    </div>
                </div>
            </section>'''
        
        return product_html
    
    def _generate_deal_status_section(self) -> str:
        """Generiert Deal-Status & Fortschritt"""
        status_html = '''
            <section class="section">
                <div class="card">
                    <h2>Deal-Status</h2>
                    <div class="deal-status">'''
        
        # Status-Anzeige
        status_text = getattr(self.dealroom, 'deal_status', 'initial')
        status_display = {
            'initial': 'Initial',
            'offer_review': 'Angebot in Prüfung',
            'contract_prepared': 'Vertragsdaten bereitgestellt',
            'pending_signature': 'Unterschrift ausstehend',
            'completed': 'Abgeschlossen'
        }.get(status_text, 'Initial')
        
        progress = getattr(self.dealroom, 'deal_progress', 0)
        
        status_html += f'''
                        <div class="status-info">
                            <h3>{status_display}</h3>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {progress}%"></div>
                            </div>
                            <p class="progress-text">{progress}% abgeschlossen</p>
                        </div>'''
        
        status_html += '''
                    </div>
                </div>
            </section>'''
        
        return status_html
    
    def _generate_documents_section(self) -> str:
        """Generiert Wichtige Dokumente & Informationen"""
        # Erweiterte Dokumentenverwaltung mit Kategorien
        documents_html = '''
            <section class="section">
                <div class="card">
                    <h2>Wichtige Dokumente</h2>
                    <div class="documents-grid">'''
        
        # Dokumente nach Kategorien gruppieren
        documents_by_category = {}
        
        # Direkt hochgeladene Dateien
        for file in self.dealroom.files.all():
            if file.file_type in ['document', 'contract', 'offer', 'invoice', 'presentation', 'specification']:
                category = getattr(file, 'document_category', 'Allgemein')
                if category not in documents_by_category:
                    documents_by_category[category] = []
                documents_by_category[category].append(file)
        
        # Globale zugeordnete Dateien
        for assignment in self.dealroom.file_assignments.all():
            if assignment.role in ['document', 'contract', 'offer', 'invoice', 'presentation', 'specification']:
                category = getattr(assignment.global_file, 'document_category', 'Allgemein')
                if category not in documents_by_category:
                    documents_by_category[category] = []
                documents_by_category[category].append(assignment.global_file)
        
        if not documents_by_category:
            return ''
        
        # Kategorien anzeigen
        for category, files in documents_by_category.items():
            documents_html += f'''
                        <div class="document-category">
                            <h3>{category}</h3>
                            <div class="document-list">'''
            
            for file in files:
                file_url = file.get_file_url() if hasattr(file, 'get_file_url') else file.file.url
                file_name = file.title if hasattr(file, 'title') else file.name
                file_size = file.get_file_size_display() if hasattr(file, 'get_file_size_display') else ''
                
                # Zugriffsebene anzeigen
                access_level = getattr(file, 'document_access_level', 'public')
                access_badge = {
                    'public': '<span class="badge public">Öffentlich</span>',
                    'customer': '<span class="badge customer">Nur Kunde</span>',
                    'internal': '<span class="badge internal">Intern</span>',
                    'confidential': '<span class="badge confidential">Vertraulich</span>'
                }.get(access_level, '')
                
                # Unterschrift erforderlich
                requires_signature = getattr(file, 'document_requires_signature', False)
                signature_badge = '<span class="badge signature">Unterschrift erforderlich</span>' if requires_signature else ''
                
                documents_html += f'''
                                <div class="document-item">
                                    <div class="document-info">
                                        <h4>{file_name}</h4>
                                        <p class="document-meta">
                                            {file_size} {access_badge} {signature_badge}
                                        </p>
                                    </div>
                                    <a href="{file_url}" class="btn btn-primary" download>
                                        <i class="icon-download"></i> Download
                                    </a>
                                </div>'''
            
            documents_html += '''
                            </div>
                        </div>'''
        
        documents_html += '''
                    </div>
                </div>
            </section>'''
        
        return documents_html
    
    def _generate_tasks_section(self) -> str:
        """Generiert Aufgaben & To-Dos für den Kunden"""
        tasks = getattr(self.dealroom, 'customer_tasks', [])
        if not tasks:
            return ''
        
        tasks_html = '''
            <section class="section">
                <div class="card">
                    <h2>Ihre Aufgaben</h2>
                    <div class="tasks-list">'''
        
        for task in tasks:
            if isinstance(task, dict):
                title = task.get('title', 'Aufgabe')
                description = task.get('description', '')
                completed = task.get('completed', False)
                due_date = task.get('due_date', '')
                
                tasks_html += f'''
                        <div class="task-item {'completed' if completed else ''}">
                            <div class="task-checkbox">
                                <input type="checkbox" {'checked' if completed else ''} disabled>
                            </div>
                            <div class="task-content">
                                <h4>{title}</h4>
                                <p>{description}</p>'''
                
                if due_date:
                    tasks_html += f'<span class="task-due">Fällig: {due_date}</span>'
                
                tasks_html += '''
                            </div>
                        </div>'''
        
        tasks_html += '''
                    </div>
                </div>
            </section>'''
        
        return tasks_html
    
    def _generate_communication_section(self) -> str:
        """Generiert Kommunikation & Kontakt"""
        contact_html = '''
            <section class="section">
                <div class="card">
                    <h2>Kontakt & Kommunikation</h2>
                    <div class="contact-grid">'''
        
        # Ansprechpartner
        if hasattr(self.dealroom, 'contact_person_name') and self.dealroom.contact_person_name:
            contact_html += f'''
                        <div class="contact-person">
                            <h3>Ihr Ansprechpartner</h3>
                            <p><strong>{self.dealroom.contact_person_name}</strong></p>'''
            
            if hasattr(self.dealroom, 'contact_person_email') and self.dealroom.contact_person_email:
                contact_html += f'<p><a href="mailto:{self.dealroom.contact_person_email}">{self.dealroom.contact_person_email}</a></p>'
            
            if hasattr(self.dealroom, 'contact_person_phone') and self.dealroom.contact_person_phone:
                contact_html += f'<p><a href="tel:{self.dealroom.contact_person_phone}">{self.dealroom.contact_person_phone}</a></p>'
            
            contact_html += '''
                        </div>'''
        
        # Chat-Bereich
        contact_html += '''
                        <div class="chat-section">
                            <h3>Direkte Nachricht</h3>
                            <div class="chat-box">
                                <textarea placeholder="Ihre Nachricht..." class="chat-input"></textarea>
                                <button class="btn">Nachricht senden</button>
                            </div>
                        </div>'''
        
        contact_html += '''
                    </div>
                </div>
            </section>'''
        
        return contact_html
    
    def _generate_team_section(self) -> str:
        """Generiert Team & Stakeholder-Übersicht"""
        team_html = '''
            <section class="section">
                <div class="card">
                    <h2>Team & Stakeholder</h2>
                    <div class="team-grid">
                        <div class="team-column">
                            <h3>Ihr Team</h3>
                            <div class="team-member">
                                <div class="member-avatar">👤</div>
                                <div class="member-info">
                                    <h4>Ihr Name</h4>
                                    <p>Kunde</p>
                                </div>
                            </div>
                        </div>
                        <div class="team-column">
                            <h3>Unser Team</h3>
                            <div class="team-member">
                                <div class="member-avatar">👨‍💼</div>
                                <div class="member-info">
                                    <h4>Berater</h4>
                                    <p>Ansprechpartner</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>'''
        
        return team_html
    
    def _generate_timeline_section(self) -> str:
        """Generiert Zeitachse / Aktivitätenprotokoll"""
        timeline_events = getattr(self.dealroom, 'timeline_events', [])
        if not timeline_events:
            timeline_events = [
                {'date': '2024-01-15', 'title': 'Dealroom erstellt', 'description': 'Ihr persönlicher Dealroom wurde angelegt'},
                {'date': '2024-01-16', 'title': 'Dokumente hochgeladen', 'description': 'Alle relevanten Unterlagen wurden bereitgestellt'},
                {'date': '2024-01-17', 'title': 'Angebot erstellt', 'description': 'Ihr individuelles Angebot wurde erstellt'}
            ]
        
        timeline_html = '''
            <section class="section">
                <div class="card">
                    <h2>Aktivitäten & Timeline</h2>
                    <div class="timeline">'''
        
        for event in timeline_events:
            if isinstance(event, dict):
                date = event.get('date', '')
                title = event.get('title', 'Aktivität')
                description = event.get('description', '')
                
                timeline_html += f'''
                        <div class="timeline-item">
                            <div class="timeline-date">{date}</div>
                            <div class="timeline-content">
                                <h4>{title}</h4>
                                <p>{description}</p>
                            </div>
                        </div>'''
        
        timeline_html += '''
                    </div>
                </div>
            </section>'''
        
        return timeline_html
    
    def _generate_faq_section(self) -> str:
        """Generiert Hilfs- & Erklärungsbereich / FAQ"""
        faq_items = getattr(self.dealroom, 'faq_items', [])
        if not faq_items:
            faq_items = [
                {'question': 'Wie funktioniert der Dealroom?', 'answer': 'Der Dealroom ist Ihr persönlicher Bereich für alle Deal-relevanten Informationen und Dokumente.'},
                {'question': 'Wo finde ich die Dokumente?', 'answer': 'Alle wichtigen Dokumente finden Sie im Bereich "Wichtige Dokumente" weiter oben.'},
                {'question': 'Wie kann ich Kontakt aufnehmen?', 'answer': 'Nutzen Sie den Chat-Bereich oder die Kontaktdaten Ihres Ansprechpartners.'}
            ]
        
        faq_html = '''
            <section class="section">
                <div class="card">
                    <h2>Häufige Fragen</h2>
                    <div class="faq-list">'''
        
        for faq in faq_items:
            if isinstance(faq, dict):
                question = faq.get('question', 'Frage')
                answer = faq.get('answer', 'Antwort')
                
                faq_html += f'''
                        <div class="faq-item">
                            <h4 class="faq-question">{question}</h4>
                            <p class="faq-answer">{answer}</p>
                        </div>'''
        
        faq_html += '''
                    </div>
                </div>
            </section>'''
        
        return faq_html
    
    def _generate_cta_section(self) -> str:
        """Generiert Call-to-Action / Abschlussbutton"""
        cta_html = '''
            <section class="section">
                <div class="card cta-card">
                    <h2>Nächster Schritt</h2>
                    <p>Bereit für den nächsten Schritt? Klicken Sie auf den Button unten.</p>
                    <div class="cta-buttons">'''
        
        if hasattr(self.dealroom, 'call_to_action') and self.dealroom.call_to_action:
            cta_html += f'<button class="btn btn-primary">{self.dealroom.call_to_action}</button>'
        else:
            cta_html += '<button class="btn btn-primary">Angebot annehmen</button>'
        
        cta_html += '''
                    </div>
                </div>
            </section>'''
        
        return cta_html
    
    def _generate_files_download_section(self) -> str:
        """Generiert Download-Sektion für Dateien"""
        # Alle zugeordneten Dateien abrufen
        assigned_files = self.dealroom.get_assigned_files()
        uploaded_files = self.dealroom.files.all()
        
        # Wenn keine Dateien vorhanden, nichts anzeigen
        if not assigned_files and not uploaded_files:
            return ''
        
        files_html = '''
            <section class="section">
                <h2>Downloads</h2>
                <div class="files-grid">'''
        
        # Zugeordnete globale Dateien
        for assignment in assigned_files:
            global_file = assignment.global_file
            if global_file and global_file.file:
                files_html += f'''
                    <div class="file-card">
                        <div class="file-icon">
                            <i class="file-icon-{global_file.get_file_extension().replace('.', '')}"></i>
                        </div>
                        <div class="file-info">
                            <h3>{global_file.title}</h3>
                            <p>{global_file.description or ''}</p>
                            <span class="file-size">{global_file.get_file_size_display()}</span>
                        </div>
                        <div class="file-actions">
                            <a href="{global_file.file.url}" class="btn btn-download" download>
                                <i class="download-icon"></i> Herunterladen
                            </a>
                        </div>
                    </div>'''
        
        # Direkt hochgeladene Dateien
        for file in uploaded_files:
            actual_file = file.get_actual_file()
            if actual_file:
                files_html += f'''
                    <div class="file-card">
                        <div class="file-icon">
                            <i class="file-icon-{file.get_file_extension().replace('.', '')}"></i>
                        </div>
                        <div class="file-info">
                            <h3>{file.title}</h3>
                            <p>{file.description or ''}</p>
                            <span class="file-size">{file.get_file_size()}</span>
                        </div>
                        <div class="file-actions">
                            <a href="{file.get_file_url()}" class="btn btn-download" download>
                                <i class="download-icon"></i> Herunterladen
                            </a>
                        </div>
                    </div>'''
        
        files_html += '''
                </div>
            </section>'''
        
        return files_html
    
    def _generate_gallery_section(self) -> str:
        """Generiert Galerie-Sektion für Bilder"""
        # Alle Galerie-Bilder abrufen
        gallery_assignments = self.dealroom.get_gallery_files()
        
        if not gallery_assignments:
            return ''
        
        # Bild-URLs sammeln
        image_urls = []
        for assignment in gallery_assignments:
            global_file = assignment.global_file
            if global_file and global_file.file_type == 'image' and global_file.file:
                image_urls.append(global_file.file.url)
        
        if not image_urls:
            return ''
        
        # Galerie-HTML generieren
        gallery_html = '''
            <section class="section">
                <h2>Galerie</h2>
                <div class="image-gallery">
                    <div class="gallery-grid">
        '''
        
        for image_url in image_urls:
            gallery_html += f'''
                        <div class="gallery-item">
                            <img src="{image_url}" alt="Galerie-Bild" loading="lazy">
                        </div>
            '''
        
        gallery_html += '''
                    </div>
                </div>
            </section>'''
        
        return gallery_html
    
    def _generate_footer(self) -> str:
        """Generiert Footer"""
        return f'''
        <footer class="footer">
            <div class="container">
                <p>&copy; 2024 {self.dealroom.title}. Alle Rechte vorbehalten.</p>
            </div>
        </footer>'''
    
    def _generate_body_end(self) -> str:
        """Generiert Body-Ende"""
        return f'''
        <script>
        // Interaktive Funktionen
        document.addEventListener('DOMContentLoaded', function() {{
            // Smooth Scrolling für Anker-Links
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
                anchor.addEventListener('click', function (e) {{
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {{
                        target.scrollIntoView({{
                            behavior: 'smooth',
                            block: 'start'
                        }});
                    }}
                }});
            }});
            
            // Lazy Loading für Bilder
            const images = document.querySelectorAll('img[loading="lazy"]');
            if ('IntersectionObserver' in window) {{
                const imageObserver = new IntersectionObserver((entries, observer) => {{
                    entries.forEach(entry => {{
                        if (entry.isIntersecting) {{
                            const img = entry.target;
                            img.src = img.dataset.src || img.src;
                            img.classList.remove('lazy');
                            imageObserver.unobserve(img);
                        }}
                    }});
                }});
                
                images.forEach(img => imageObserver.observe(img));
            }}
            
            // Download-Tracking
            document.querySelectorAll('.btn-download').forEach(btn => {{
                btn.addEventListener('click', function() {{
                    console.log('Download gestartet:', this.href);
                }});
            }});
        }});
        </script>
        </body>
        </html>'''
    
    def save_website(self, output_path: str) -> bool:
        """
        Speichert die generierte Website
        
        Args:
            output_path: Ausgabepfad
            
        Returns:
            bool: True wenn erfolgreich gespeichert
        """
        try:
            # Verzeichnis erstellen
            directory = os.path.dirname(output_path)
            create_directory(directory)
            
            # HTML generieren und speichern
            html_content = self.generate_website()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
        except Exception as e:
            print(f"Fehler beim Speichern der Website: {e}")
            return False
    
    def get_website_url(self) -> str:
        """
        Gibt die URL der generierten Website zurück
        
        Returns:
            str: Website-URL
        """
        if self.dealroom.local_website_url:
            return self.dealroom.local_website_url
        elif self.dealroom.public_url:
            return self.dealroom.public_url
        else:
            return f"/generated_pages/dealroom-{self.dealroom.id}/index.html"
    
    def delete_website(self) -> bool:
        """
        Löscht die generierte Website
        
        Returns:
            bool: True wenn erfolgreich gelöscht
        """
        try:
            # Website-Verzeichnis-Pfad erstellen
            website_dir = os.path.join(settings.BASE_DIR, 'generated_pages', f'dealroom-{self.dealroom.id}')
            
            # Prüfen ob Verzeichnis existiert
            if os.path.exists(website_dir):
                # Verzeichnis und alle Inhalte löschen
                import shutil
                shutil.rmtree(website_dir)
                print(f"🗑️ Website-Verzeichnis gelöscht: {website_dir}")
                return True
            else:
                print(f"ℹ️ Website-Verzeichnis existiert nicht: {website_dir}")
                return True  # Als erfolgreich betrachten wenn nichts zu löschen ist
                
        except Exception as e:
            print(f"❌ Fehler beim Löschen der Website: {e}")
            return False 