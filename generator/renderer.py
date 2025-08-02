"""
Haupt-Generator für Dealroom-Webseiten
=====================================

Diese Datei enthält die zentrale Logik für die automatische Generierung
von Webseiten aus Dealroom-Daten. Der DealroomGenerator ist das Herzstück
des Systems und koordiniert alle anderen Komponenten.

Funktionsweise:
1. Nimmt einen Dealroom (Django-Model) als Input
2. Bereitet alle Daten für das Template vor
3. Wählt das passende HTML-Template aus
4. Generiert dynamisches CSS basierend auf Dealroom-Farben
5. Verarbeitet alle Assets (Bilder, Videos, Dokumente)
6. Speichert die generierte Website als statische Dateien
7. Erstellt SEO-Dateien (Sitemap, robots.txt)
8. Aktualisiert den Website-Status im Dealroom-Model

Verwendung:
    generator = DealroomGenerator(dealroom)
    website_url = generator.generate_website()
"""
import os
import shutil
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from .css_generator import CSSGenerator
from .video_processor import VideoProcessor
from .image_processor import ImageProcessor
from .utils import create_directory, copy_media_files


class DealroomGenerator:
    """
    Generiert automatisch Webseiten aus Dealroom-Daten
    
    Diese Klasse ist der zentrale Koordinator für die Website-Generierung.
    Sie orchestriert alle anderen Komponenten und stellt sicher, dass
    eine vollständige, funktionsfähige Website erstellt wird.
    
    Attributes:
        dealroom: Das Dealroom-Model-Objekt mit allen Daten
        base_dir: Basis-Verzeichnis für alle generierten Websites
        dealroom_dir: Spezifisches Verzeichnis für diesen Dealroom
        assets_dir: Verzeichnis für CSS, JS und andere Assets
        css_generator: Instanz für dynamische CSS-Generierung
        video_processor: Instanz für Video-Verarbeitung
        image_processor: Instanz für Bild-Verarbeitung
    """
    
    def __init__(self, dealroom):
        """
        Initialisiert den Generator mit einem Dealroom
        
        Args:
            dealroom: Dealroom-Model-Objekt mit allen Daten
        """
        self.dealroom = dealroom
        
        # Verzeichnis-Pfade definieren
        # Alle generierten Websites werden unter 'generated_pages' gespeichert
        self.base_dir = os.path.join(settings.BASE_DIR, 'generated_pages')
        
        # Jeder Dealroom bekommt sein eigenes Verzeichnis
        # Format: generated_pages/dealroom-{id}/
        self.dealroom_dir = os.path.join(self.base_dir, f'dealroom-{dealroom.id}')
        
        # Assets-Verzeichnis für CSS, JS, Bilder etc.
        self.assets_dir = os.path.join(self.dealroom_dir, 'assets')
        
        # Komponenten initialisieren
        self.css_generator = CSSGenerator()  # Für dynamische Styles
        self.video_processor = VideoProcessor()  # Für YouTube/Vimeo Videos
        self.image_processor = ImageProcessor()  # Für Bildverarbeitung
    
    def generate_website(self):
        """
        Hauptmethode für die komplette Webseiten-Generierung
        
        Diese Methode führt alle Schritte der Website-Generierung aus:
        1. Status auf "generating" setzen
        2. Verzeichnisse erstellen
        3. Template auswählen
        4. Kontext vorbereiten
        5. HTML generieren
        6. CSS generieren
        7. Assets verarbeiten
        8. Dateien speichern
        9. SEO-Dateien erstellen
        10. Status aktualisieren
        
        Returns:
            str: URL der generierten Website
            
        Raises:
            Exception: Bei Fehlern während der Generierung
        """
        
        try:
            # Schritt 1: Status auf "generating" setzen
            # Das verhindert doppelte Generierung und zeigt Fortschritt an
            self.dealroom.website_status = 'generating'
            self.dealroom.save(update_fields=['website_status'])
            
            # Schritt 2: Verzeichnisse erstellen
            # Erstellt alle notwendigen Ordner für die Website
            self._create_directories()
            
            # Schritt 3: Template auswählen
            # Wählt basierend auf dealroom.template_type das passende HTML-Template
            template_name = self._select_template()
            
            # Schritt 4: Kontext vorbereiten
            # Sammelt alle Daten die das Template benötigt
            context = self._prepare_context()
            
            # Schritt 5: HTML generieren
            # Rendert das HTML-Template mit den vorbereiteten Daten
            html_content = self._generate_html(template_name, context)
            
            # Schritt 6: CSS generieren
            # Erstellt dynamisches CSS basierend auf Dealroom-Farben
            css_content = self.css_generator.generate(self.dealroom)
            
            # Schritt 7: Assets verarbeiten
            # Kopiert Bilder, Videos und Dokumente
            self._process_assets()
            
            # Schritt 8: Dateien speichern
            # Speichert HTML, CSS und JavaScript-Dateien
            self._save_files(html_content, css_content)
            
            # Schritt 9: SEO-Dateien erstellen
            # Erstellt sitemap.xml und robots.txt
            self._generate_seo_files()
            
            # Schritt 10: URL generieren
            # Erstellt die lokale URL für die Website
            website_url = self._get_website_url()
            
            # Schritt 11: Status aktualisieren
            # Markiert die Generierung als erfolgreich
            self.dealroom.website_status = 'generated'
            self.dealroom.last_generation = timezone.now()
            self.dealroom.local_website_url = website_url
            self.dealroom.generation_error = None
            self.dealroom.save(update_fields=[
                'website_status', 'last_generation', 
                'local_website_url', 'generation_error'
            ])
            
            print(f"✅ Website für '{self.dealroom.title}' erfolgreich generiert: {website_url}")
            return website_url
            
        except Exception as e:
            # Fehlerbehandlung: Status auf "failed" setzen
            self.dealroom.website_status = 'failed'
            self.dealroom.generation_error = str(e)
            self.dealroom.save(update_fields=['website_status', 'generation_error'])
            
            print(f"❌ Fehler bei Website-Generierung für '{self.dealroom.title}': {e}")
            raise
    
    def _create_directories(self):
        """
        Erstellt alle notwendigen Verzeichnisse für die Website
        
        Erstellt folgende Struktur:
        generated_pages/
        └── dealroom-{id}/
            ├── index.html
            ├── sitemap.xml
            ├── robots.txt
            └── assets/
                ├── style.css
                ├── script.js
                ├── images/
                ├── videos/
                └── documents/
        """
        create_directory(self.dealroom_dir)  # Hauptverzeichnis
        create_directory(self.assets_dir)    # Assets-Verzeichnis
        create_directory(os.path.join(self.assets_dir, 'images'))     # Bilder
        create_directory(os.path.join(self.assets_dir, 'videos'))     # Videos
        create_directory(os.path.join(self.assets_dir, 'documents'))  # Dokumente
    
    def _select_template(self):
        """
        Wählt das passende HTML-Template basierend auf template_type
        
        Jeder Dealroom hat ein template_type (modern, classic, minimal, corporate)
        und bekommt das entsprechende HTML-Template zugewiesen.
        
        Returns:
            str: Pfad zum HTML-Template
        """
        # Mapping von template_type zu Template-Datei
        template_map = {
            'modern': 'modern/base.html',      # Responsive, Hero-Section
            'classic': 'classic/base.html',    # Sidebar-Layout
            'minimal': 'minimal/base.html',    # Schlicht
            'corporate': 'corporate/base.html', # Professionell
        }
        
        # Fallback auf modern wenn template_type nicht gefunden
        return template_map.get(self.dealroom.template_type, 'modern/base.html')
    
    def _prepare_context(self):
        """
        Bereitet alle Daten für das HTML-Template vor
        
        Sammelt alle relevanten Daten aus dem Dealroom-Model und
        bereitet sie in einer strukturierten Form für das Template vor.
        
        Returns:
            dict: Kontext-Daten für das Template
        """
        return {
            # Dealroom-Hauptdaten
            'dealroom': self.dealroom,
            
            # Empfänger-Informationen (strukturiert)
            'recipient': {
                'name': self.dealroom.recipient_name,
                'email': self.dealroom.recipient_email,
                'company': self.dealroom.recipient_company,
            },
            
            # Kunden-Informationen (strukturiert)
            'customer': {
                'name': self.dealroom.customer_name,
                'email': self.dealroom.customer_email,
                'info': self.dealroom.customer_info,
            },
            
            # Verarbeitete Medien
            'video': self.video_processor.process_video(self.dealroom),  # YouTube/Vimeo Embed
            'images': self.image_processor.process_images(self.dealroom), # Galerie-Bilder
            
            # Dateien (Dokumente, Präsentationen etc.)
            'files': self._process_files(),
            
            # Design-Farben (für CSS)
            'colors': {
                'primary': self.dealroom.primary_color,
                'secondary': self.dealroom.secondary_color,
            },
            
            # Zeitstempel für Footer
            'generated_at': timezone.now(),
        }
    
    def _generate_html(self, template_name, context):
        """
        Generiert HTML-Inhalt aus Template und Kontext
        
        Verwendet Django's Template-System um das HTML zu rendern.
        
        Args:
            template_name: Pfad zum HTML-Template
            context: Daten für das Template
            
        Returns:
            str: Gerenderter HTML-Inhalt
        """
        return render_to_string(template_name, context)
    
    def _process_assets(self):
        """
        Verarbeitet alle Assets (Bilder, Videos, Dokumente)
        
        Kopiert alle hochgeladenen Dateien in das Assets-Verzeichnis
        der generierten Website, damit sie verfügbar sind.
        """
        # Bilder kopieren (Hero-Bilder, Logos, Galerie)
        for file in self.dealroom.files.filter(file_type__in=['hero_image', 'logo', 'gallery']):
            if file.file:
                copy_media_files(file.file, self.assets_dir)
        
        # Videos kopieren (falls hochgeladen)
        if self.dealroom.central_video_file:
            copy_media_files(self.dealroom.central_video_file, self.assets_dir)
        
        # Dokumente kopieren (PDFs, Präsentationen etc.)
        for file in self.dealroom.files.filter(file_type='document'):
            if file.file:
                copy_media_files(file.file, self.assets_dir)
    
    def _process_files(self):
        """
        Verarbeitet alle Dateien des Dealrooms für das Template
        
        Erstellt eine strukturierte Liste aller Dateien mit Metadaten
        für die Anzeige in der Website.
        
        Returns:
            list: Liste von Datei-Dictionaries mit Metadaten
        """
        files = []
        for file in self.dealroom.files.all():
            files.append({
                'title': file.title,
                'description': file.description,
                'file_type': file.get_file_type_display(),  # Menschlich lesbar
                'url': f'assets/{file.file.name.split("/")[-1]}' if file.file else None,
                'is_primary': file.is_primary,  # Für Hero-Bilder
            })
        return files
    
    def _save_files(self, html_content, css_content):
        """
        Speichert HTML und CSS Dateien
        
        Speichert die generierten Dateien in die entsprechenden Verzeichnisse
        und kopiert JavaScript-Dateien falls vorhanden.
        
        Args:
            html_content: Gerenderter HTML-Inhalt
            css_content: Generiertes CSS
        """
        
        # HTML-Datei speichern (index.html)
        html_path = os.path.join(self.dealroom_dir, 'index.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # CSS-Datei speichern (style.css)
        css_path = os.path.join(self.assets_dir, 'style.css')
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        # JavaScript-Datei kopieren (falls vorhanden)
        # Jedes Template kann eine eigene script.js haben
        js_template = os.path.join(settings.BASE_DIR, 'generator/templates', 
                                  self.dealroom.template_type, 'script.js')
        if os.path.exists(js_template):
            js_dest = os.path.join(self.assets_dir, 'script.js')
            shutil.copy2(js_template, js_dest)
    
    def _generate_seo_files(self):
        """
        Generiert SEO-Dateien (sitemap.xml, robots.txt)
        
        Erstellt Suchmaschinen-optimierte Dateien für bessere
        Indexierung der generierten Websites.
        """
        
        # Sitemap generieren (XML-Format für Suchmaschinen)
        sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{self._get_website_url()}</loc>
        <lastmod>{self.dealroom.updated_at.strftime('%Y-%m-%d')}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>"""
        
        sitemap_path = os.path.join(self.dealroom_dir, 'sitemap.xml')
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        
        # robots.txt generieren (Anweisungen für Suchmaschinen-Crawler)
        robots_content = f"""User-agent: *
Allow: /

Sitemap: {self._get_website_url()}sitemap.xml"""
        
        robots_path = os.path.join(self.dealroom_dir, 'robots.txt')
        with open(robots_path, 'w', encoding='utf-8') as f:
            f.write(robots_content)
    
    def _get_website_url(self):
        """
        Generiert die lokale Website-URL
        
        Erstellt die URL unter der die Website erreichbar ist.
        Format: /generated_pages/dealroom-{id}/
        
        Returns:
            str: Lokale URL der Website
        """
        return f"/generated_pages/dealroom-{self.dealroom.id}/"
    
    def delete_website(self):
        """
        Löscht die generierte Website
        
        Entfernt das komplette Verzeichnis der Website
        und alle zugehörigen Dateien.
        """
        try:
            if os.path.exists(self.dealroom_dir):
                shutil.rmtree(self.dealroom_dir)
                print(f"🗑️ Website für '{self.dealroom.title}' gelöscht")
        except Exception as e:
            print(f"❌ Fehler beim Löschen der Website: {e}")
    
    def regenerate_website(self):
        """
        Generiert die Website neu
        
        Löscht die alte Website und erstellt sie komplett neu.
        Nützlich wenn sich Daten geändert haben.
        
        Returns:
            str: URL der neu generierten Website
        """
        self.delete_website()
        return self.generate_website() 