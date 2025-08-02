"""
Image-Processor für Bild-Galerien und -Verarbeitung
==================================================

Verarbeitet Bilder und erstellt Galerien für die generierten Websites.
"""

import os
from typing import List, Optional


class ImageProcessor:
    """
    Verarbeitet Bilder und erstellt Galerien
    """
    
    def __init__(self):
        """Initialisiert den Image-Processor"""
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
    
    def is_image_file(self, file_path: str) -> bool:
        """
        Prüft ob es sich um eine Bilddatei handelt
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            bool: True wenn Bilddatei
        """
        if not file_path:
            return False
            
        extension = os.path.splitext(file_path)[1].lower()
        return extension in self.supported_formats
    
    def create_image_gallery(self, images: List[str], title: str = "Galerie") -> str:
        """
        Erstellt HTML-Code für eine Bild-Galerie
        
        Args:
            images: Liste von Bild-URLs
            title: Titel der Galerie
            
        Returns:
            str: HTML-Code für die Galerie
        """
        if not images:
            return f'<p>Keine Bilder in der Galerie "{title}" verfügbar.</p>'
        
        gallery_html = f'''
        <div class="image-gallery">
            <h3>{title}</h3>
            <div class="gallery-grid">
        '''
        
        for image_url in images:
            if self.is_image_file(image_url):
                gallery_html += f'''
                <div class="gallery-item">
                    <img src="{image_url}" alt="Galerie-Bild" loading="lazy">
                </div>
                '''
        
        gallery_html += '''
            </div>
        </div>
        '''
        
        return gallery_html
    
    def create_hero_image(self, image_url: str, title: str = "", subtitle: str = "") -> str:
        """
        Erstellt HTML-Code für ein Hero-Bild
        
        Args:
            image_url: URL des Bildes
            title: Titel über dem Bild
            subtitle: Untertitel über dem Bild
            
        Returns:
            str: HTML-Code für das Hero-Bild
        """
        if not image_url or not self.is_image_file(image_url):
            return f'<p>Kein gültiges Hero-Bild verfügbar.</p>'
        
        hero_html = f'''
        <div class="hero-image">
            <img src="{image_url}" alt="Hero-Bild" class="hero-img">
        '''
        
        if title or subtitle:
            hero_html += f'''
            <div class="hero-overlay">
                {f'<h1>{title}</h1>' if title else ''}
                {f'<p>{subtitle}</p>' if subtitle else ''}
            </div>
            '''
        
        hero_html += '</div>'
        
        return hero_html
    
    def create_logo_display(self, logo_url: str, alt_text: str = "Logo") -> str:
        """
        Erstellt HTML-Code für ein Logo
        
        Args:
            logo_url: URL des Logos
            alt_text: Alt-Text für das Logo
            
        Returns:
            str: HTML-Code für das Logo
        """
        if not logo_url or not self.is_image_file(logo_url):
            return f'<p>Kein Logo verfügbar.</p>'
        
        return f'''
        <div class="logo-container">
            <img src="{logo_url}" alt="{alt_text}" class="logo-img">
        </div>
        '''
    
    def create_image_slider(self, images: List[str], title: str = "Bilder") -> str:
        """
        Erstellt HTML-Code für einen Bild-Slider
        
        Args:
            images: Liste von Bild-URLs
            title: Titel des Sliders
            
        Returns:
            str: HTML-Code für den Slider
        """
        if not images:
            return f'<p>Keine Bilder für den Slider "{title}" verfügbar.</p>'
        
        slider_html = f'''
        <div class="image-slider">
            <h3>{title}</h3>
            <div class="slider-container">
        '''
        
        for i, image_url in enumerate(images):
            if self.is_image_file(image_url):
                active_class = "active" if i == 0 else ""
                slider_html += f'''
                <div class="slide {active_class}">
                    <img src="{image_url}" alt="Slider-Bild {i+1}">
                </div>
                '''
        
        slider_html += '''
            </div>
            <div class="slider-controls">
                <button class="prev-btn">‹</button>
                <button class="next-btn">›</button>
            </div>
        </div>
        '''
        
        return slider_html
    
    def get_image_info(self, image_url: str) -> dict:
        """
        Gibt Informationen zu einem Bild zurück
        
        Args:
            image_url: URL des Bildes
            
        Returns:
            dict: Bild-Informationen
        """
        if not image_url:
            return {}
        
        filename = os.path.basename(image_url)
        extension = os.path.splitext(filename)[1].lower()
        
        return {
            'url': image_url,
            'filename': filename,
            'extension': extension,
            'is_image': self.is_image_file(image_url),
            'supported': extension in self.supported_formats
        } 