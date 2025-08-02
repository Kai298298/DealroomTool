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
        """
        Generiert eine komplette Website
        
        Returns:
            str: HTML-Code der Website
        """
        html_parts = [
            self._generate_html_header(),
            self._generate_css(),
            self._generate_body_start(),
            self._generate_header(),
            self._generate_hero_section(),
            self._generate_content_sections(),
            self._generate_footer(),
            self._generate_body_end()
        ]
        
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
        """Generiert Content-Bereiche"""
        content_html = '''
        <main class="content">
            <div class="container">'''
        
        # Beschreibung
        if self.dealroom.description:
            content_html += f'''
            <section class="section">
                <h2>Über uns</h2>
                <p>{self.dealroom.description}</p>
            </section>'''
        
        # Kontakt-Informationen
        if self.dealroom.recipient_name or self.dealroom.recipient_email:
            content_html += '''
            <section class="section">
                <h2>Kontakt</h2>
                <div class="contact-info">'''
            
            if self.dealroom.recipient_name:
                content_html += f'<p><strong>Name:</strong> {self.dealroom.recipient_name}</p>'
            
            if self.dealroom.recipient_email:
                content_html += f'<p><strong>E-Mail:</strong> <a href="mailto:{self.dealroom.recipient_email}">{self.dealroom.recipient_email}</a></p>'
            
            if self.dealroom.recipient_company:
                content_html += f'<p><strong>Firma:</strong> {self.dealroom.recipient_company}</p>'
            
            content_html += '''
                </div>
            </section>'''
        
        # Bild-Galerie-Sektion
        gallery_section = self._generate_gallery_section()
        if gallery_section:
            content_html += gallery_section
        
        # Dateien-Download-Sektion
        files_section = self._generate_files_download_section()
        if files_section:
            content_html += files_section
        
        content_html += '''
            </div>
        </main>'''
        
        return content_html
    
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