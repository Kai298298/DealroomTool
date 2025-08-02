"""
Image-Processor für Dealroom-Bilder
==================================

Diese Datei verarbeitet Bilder für die generierten Webseiten.
Sie kümmert sich um Hero-Bilder, Logos, Galerie-Bilder und andere
Bild-Assets der Dealrooms.

Funktionsweise:
1. Sammelt alle Bilder eines Dealrooms
2. Kategorisiert sie nach Typ (Hero, Logo, Galerie)
3. Erstellt responsive Bild-Galerien
4. Optimiert Bild-Pfade für die Website
5. Generiert Thumbnail-Versionen

Unterstützte Bild-Typen:
- Hero-Bilder (Hauptbilder)
- Logos (Firmenlogos)
- Galerie-Bilder (Produktbilder, Screenshots)
- Dokumente (PDFs, Präsentationen)

Verwendung:
    image_processor = ImageProcessor()
    gallery_html = image_processor.process_images(dealroom)
"""
import os
from django.conf import settings


class ImageProcessor:
    """
    Verarbeitet Bilder für die Webseiten
    
    Diese Klasse kümmert sich um alle Bild-bezogenen Aufgaben:
    - Sammeln und Kategorisieren von Bildern
    - Erstellen von Bild-Galerien
    - Optimieren von Bild-Pfaden
    - Generieren von Thumbnails
    
    Features:
    - Automatische Bild-Kategorisierung
    - Responsive Bild-Galerien
    - Lightbox-Support für Galerien
    - Fallback für fehlende Bilder
    - Optimierte Bild-Pfade
    """
    
    def process_images(self, dealroom):
        """
        Verarbeitet alle Bilder eines Dealrooms
        
        Sammelt alle hochgeladenen Bilder und erstellt
        entsprechende HTML-Strukturen für die Website.
        
        Args:
            dealroom: Dealroom-Model-Objekt mit Bild-Daten
            
        Returns:
            dict: Verarbeitete Bilder nach Kategorien
        """
        
        # Bilder nach Typen sammeln
        hero_images = self.get_images_by_type(dealroom, 'hero_image')
        logos = self.get_images_by_type(dealroom, 'logo')
        gallery_images = self.get_images_by_type(dealroom, 'gallery')
        
        return {
            'hero': self.process_hero_images(hero_images),
            'logos': self.process_logos(logos),
            'gallery': self.process_gallery_images(gallery_images),
            'all_images': self.get_all_images(dealroom),
        }
    
    def get_images_by_type(self, dealroom, file_type):
        """
        Sammelt Bilder eines bestimmten Typs
        
        Filtert alle Dateien eines Dealrooms nach dem
        angegebenen Datei-Typ.
        
        Args:
            dealroom: Dealroom-Model-Objekt
            file_type: Typ der zu sammelnden Bilder
            
        Returns:
            list: Liste von Bild-Dateien
        """
        return dealroom.files.filter(file_type=file_type, is_public=True)
    
    def process_hero_images(self, hero_images):
        """
        Verarbeitet Hero-Bilder für prominente Anzeige
        
        Hero-Bilder werden groß und prominent auf der Website
        angezeigt, oft als Hintergrund oder Hauptbild.
        
        Args:
            hero_images: Liste von Hero-Bildern
            
        Returns:
            dict: Verarbeitete Hero-Bilder mit HTML
        """
        if not hero_images:
            return {
                'has_images': False,
                'html': '',
                'images': []
            }
        
        # Hero-Bilder verarbeiten
        processed_images = []
        for image in hero_images:
            if image.file:
                processed_images.append({
                    'title': image.title,
                    'description': image.description,
                    'url': self.get_image_url(image.file),
                    'filename': os.path.basename(image.file.name),
                    'is_primary': image.is_primary,
                })
        
        # HTML für Hero-Bereich generieren
        html = self.generate_hero_html(processed_images)
        
        return {
            'has_images': True,
            'html': html,
            'images': processed_images
        }
    
    def process_logos(self, logos):
        """
        Verarbeitet Logos für Header/Footer
        
        Logos werden typischerweise klein angezeigt, oft
        im Header oder Footer der Website.
        
        Args:
            logos: Liste von Logo-Dateien
            
        Returns:
            dict: Verarbeitete Logos mit HTML
        """
        if not logos:
            return {
                'has_logos': False,
                'html': '',
                'logos': []
            }
        
        # Logos verarbeiten
        processed_logos = []
        for logo in logos:
            if logo.file:
                processed_logos.append({
                    'title': logo.title,
                    'description': logo.description,
                    'url': self.get_image_url(logo.file),
                    'filename': os.path.basename(logo.file.name),
                })
        
        # HTML für Logo-Bereich generieren
        html = self.generate_logo_html(processed_logos)
        
        return {
            'has_logos': True,
            'html': html,
            'logos': processed_logos
        }
    
    def process_gallery_images(self, gallery_images):
        """
        Verarbeitet Galerie-Bilder für Bildergalerie
        
        Galerie-Bilder werden in einer responsiven Grid-Galerie
        angezeigt, oft mit Lightbox-Funktionalität.
        
        Args:
            gallery_images: Liste von Galerie-Bildern
            
        Returns:
            dict: Verarbeitete Galerie-Bilder mit HTML
        """
        if not gallery_images:
            return {
                'has_gallery': False,
                'html': '',
                'images': []
            }
        
        # Galerie-Bilder verarbeiten
        processed_images = []
        for image in gallery_images:
            if image.file:
                processed_images.append({
                    'title': image.title,
                    'description': image.description,
                    'url': self.get_image_url(image.file),
                    'filename': os.path.basename(image.file.name),
                    'thumbnail_url': self.get_thumbnail_url(image.file),
                })
        
        # HTML für Galerie generieren
        html = self.generate_gallery_html(processed_images)
        
        return {
            'has_gallery': True,
            'html': html,
            'images': processed_images
        }
    
    def get_all_images(self, dealroom):
        """
        Sammelt alle Bilder eines Dealrooms
        
        Erstellt eine vollständige Liste aller Bilder
        unabhängig vom Typ.
        
        Args:
            dealroom: Dealroom-Model-Objekt
            
        Returns:
            list: Alle Bilder mit Metadaten
        """
        all_images = []
        for file in dealroom.files.filter(is_public=True):
            if file.file:
                all_images.append({
                    'title': file.title,
                    'description': file.description,
                    'file_type': file.get_file_type_display(),
                    'url': self.get_image_url(file.file),
                    'filename': os.path.basename(file.file.name),
                    'is_primary': file.is_primary,
                })
        
        return all_images
    
    def get_image_url(self, image_file):
        """
        Generiert URL für ein Bild
        
        Erstellt die korrekte URL für ein Bild basierend
        auf dem Datei-Pfad.
        
        Args:
            image_file: Django FileField-Objekt
            
        Returns:
            str: Bild-URL
        """
        if hasattr(image_file, 'url'):
            return image_file.url
        return ''
    
    def get_thumbnail_url(self, image_file):
        """
        Generiert Thumbnail-URL für ein Bild
        
        Für Galerie-Bilder können Thumbnail-Versionen
        erstellt werden (hier vereinfacht).
        
        Args:
            image_file: Django FileField-Objekt
            
        Returns:
            str: Thumbnail-URL (hier gleich der Original-URL)
        """
        return self.get_image_url(image_file)
    
    def generate_hero_html(self, images):
        """
        Generiert HTML für Hero-Bilder
        
        Erstellt HTML-Code für die prominente Anzeige
        von Hero-Bildern.
        
        Args:
            images: Liste verarbeiteter Hero-Bilder
            
        Returns:
            str: HTML-Code für Hero-Bereich
        """
        if not images:
            return ''
        
        # Primäres Hero-Bild finden
        primary_image = next((img for img in images if img['is_primary']), images[0])
        
        html = f'''
        <div class="hero-image-container">
            <img src="{primary_image['url']}" 
                 alt="{primary_image['title']}" 
                 class="hero-image"
                 style="width: 100%; max-height: 400px; object-fit: cover;">
            <div class="hero-overlay">
                <h2>{primary_image['title']}</h2>
                <p>{primary_image['description']}</p>
            </div>
        </div>
        '''
        
        return html
    
    def generate_logo_html(self, logos):
        """
        Generiert HTML für Logos
        
        Erstellt HTML-Code für die Anzeige von Logos,
        typischerweise klein und in einer Reihe.
        
        Args:
            logos: Liste verarbeiteter Logos
            
        Returns:
            str: HTML-Code für Logo-Bereich
        """
        if not logos:
            return ''
        
        html = '<div class="logo-container">'
        for logo in logos:
            html += f'''
            <div class="logo-item">
                <img src="{logo['url']}" 
                     alt="{logo['title']}" 
                     class="logo-image"
                     style="max-height: 60px; max-width: 200px;">
                <p class="logo-title">{logo['title']}</p>
            </div>
            '''
        html += '</div>'
        
        return html
    
    def generate_gallery_html(self, images):
        """
        Generiert HTML für Bildergalerie
        
        Erstellt eine responsive Grid-Galerie mit
        Lightbox-Funktionalität.
        
        Args:
            images: Liste verarbeiteter Galerie-Bilder
            
        Returns:
            str: HTML-Code für Galerie
        """
        if not images:
            return ''
        
        html = '''
        <div class="image-gallery">
            <div class="gallery-grid">
        '''
        
        for i, image in enumerate(images):
            html += f'''
            <div class="gallery-item" data-index="{i}">
                <img src="{image['url']}" 
                     alt="{image['title']}" 
                     class="gallery-image"
                     onclick="openLightbox({i})">
                <div class="gallery-overlay">
                    <h4>{image['title']}</h4>
                    <p>{image['description']}</p>
                </div>
            </div>
            '''
        
        html += '''
            </div>
        </div>
        
        <!-- Lightbox Modal -->
        <div id="lightbox" class="lightbox-modal" onclick="closeLightbox()">
            <span class="close-lightbox">&times;</span>
            <img id="lightbox-image" class="lightbox-content">
            <div class="lightbox-caption" id="lightbox-caption"></div>
        </div>
        '''
        
        return html
    
    def validate_image_file(self, image_file):
        """
        Validiert Bild-Datei
        
        Prüft ob eine Datei ein unterstütztes Bild-Format ist.
        
        Args:
            image_file: Zu validierende Datei
            
        Returns:
            tuple: (is_valid, message)
        """
        if not image_file:
            return False, "Keine Datei angegeben"
        
        # Unterstützte Bild-Formate
        supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        file_extension = os.path.splitext(image_file.name)[1].lower()
        
        if file_extension not in supported_formats:
            return False, f"Nicht unterstütztes Bild-Format: {file_extension}"
        
        return True, f"Bild-Format unterstützt: {file_extension}"
    
    def get_image_dimensions(self, image_file):
        """
        Ermittelt Bild-Dimensionen
        
        Versucht die Abmessungen eines Bildes zu ermitteln.
        (Hier vereinfacht - in der Praxis würde man PIL/Pillow verwenden)
        
        Args:
            image_file: Bild-Datei
            
        Returns:
            tuple: (width, height) oder (None, None)
        """
        # In der Praxis würde man hier PIL/Pillow verwenden
        # um die tatsächlichen Dimensionen zu ermitteln
        return None, None 