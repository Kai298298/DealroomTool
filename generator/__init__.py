"""
Website-Generator für Dealroom Dashboard
======================================

Dieses Paket enthält alle Komponenten für die automatische
Generierung von Webseiten aus Dealroom-Daten.

Struktur:
├── __init__.py          # Paket-Initialisierung
├── renderer.py          # Haupt-Generator (DealroomGenerator)
├── css_generator.py     # CSS-Generator für dynamische Styles
├── video_processor.py   # Video-Verarbeitung (YouTube/Vimeo)
├── image_processor.py   # Bild-Verarbeitung und Galerien
├── utils.py            # Hilfsfunktionen
└── templates/          # HTML-Templates
    ├── modern/         # Modernes Template
    ├── classic/        # Klassisches Template
    ├── minimal/        # Minimalistisches Template
    └── corporate/      # Corporate Template

Hauptkomponenten:
- DealroomGenerator: Zentrale Generierungsklasse
- CSSGenerator: Dynamische CSS-Generierung
- VideoProcessor: YouTube/Vimeo Integration
- ImageProcessor: Bild-Galerien und -Verarbeitung

Verwendung:
    from generator.renderer import DealroomGenerator
    
    generator = DealroomGenerator(dealroom)
    website_url = generator.generate_website()
"""

# Version des Generator-Systems
__version__ = "1.0.0"

# Autor und Beschreibung
__author__ = "Dealroom Dashboard Team"
__description__ = "Automatischer Website-Generator für Dealrooms"

# Verfügbare Komponenten exportieren
from .renderer import DealroomGenerator
from .css_generator import CSSGenerator
from .video_processor import VideoProcessor
from .image_processor import ImageProcessor

# Utility-Funktionen exportieren
from .utils import (
    create_directory,
    copy_media_files,
    validate_file_path,
    get_file_size_mb,
    sanitize_filename,
    get_file_extension,
    is_image_file,
    is_video_file,
    is_document_file,
    format_file_size,
    ensure_unique_filename
)

# Alle wichtigen Klassen und Funktionen für einfachen Import
__all__ = [
    # Hauptkomponenten
    'DealroomGenerator',
    'CSSGenerator', 
    'VideoProcessor',
    'ImageProcessor',
    
    # Utility-Funktionen
    'create_directory',
    'copy_media_files',
    'validate_file_path',
    'get_file_size_mb',
    'sanitize_filename',
    'get_file_extension',
    'is_image_file',
    'is_video_file',
    'is_document_file',
    'format_file_size',
    'ensure_unique_filename',
]

# Konfiguration für das Generator-System
GENERATOR_CONFIG = {
    'supported_templates': ['modern', 'classic', 'minimal', 'corporate', 'creative', 'elegant', 'bold', 'tech', 'luxury', 'clean', 'professional', 'startup', 'premium'],
    'max_file_size_mb': 50,  # Maximale Dateigröße
    'supported_image_formats': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
    'supported_video_formats': ['.mp4', '.webm', '.ogg'],
    'supported_document_formats': ['.pdf', '.doc', '.docx', '.ppt', '.pptx'],
    'output_directory': 'generated_pages',  # Ausgabeverzeichnis
    'assets_directory': 'assets',  # Assets-Unterverzeichnis
}

# Template-Konfiguration
TEMPLATE_CONFIG = {
    'modern': {
        'name': 'Modern',
        'description': 'Responsive Design mit Hero-Section',
        'features': ['Hero-Bereich', 'Responsive Grid', 'Moderne Animationen'],
    },
    'classic': {
        'name': 'Classic', 
        'description': 'Traditionelles Layout mit Sidebar',
        'features': ['Sidebar-Navigation', 'Kompaktes Layout', 'Klassische Typografie'],
    },
    'minimal': {
        'name': 'Minimal',
        'description': 'Schlichtes, minimalistisches Design',
        'features': ['Viel Weißraum', 'Schlichte Typografie', 'Fokus auf Inhalt'],
    },
    'corporate': {
        'name': 'Corporate',
        'description': 'Professionelles Business-Design',
        'features': ['Business-Layout', 'Professionelle Farben', 'Strukturierte Inhalte'],
    },
    'creative': {
        'name': 'Creative',
        'description': 'Kreatives Design mit Animationen',
        'features': ['Kreative Animationen', 'Farbenfrohe Gestaltung', 'Interaktive Elemente'],
    },
    'elegant': {
        'name': 'Elegant',
        'description': 'Elegantes, hochwertiges Design',
        'features': ['Elegante Typografie', 'Hochwertige Farben', 'Sofistizierte Layouts'],
    },
    'bold': {
        'name': 'Bold',
        'description': 'Mutiges, auffälliges Design',
        'features': ['Starke Kontraste', 'Auffällige Farben', 'Bold Typografie'],
    },
    'tech': {
        'name': 'Tech',
        'description': 'Technologie-fokussiertes Design',
        'features': ['Tech-Ästhetik', 'Futuristische Elemente', 'Code-Inspiration'],
    },
    'luxury': {
        'name': 'Luxury',
        'description': 'Luxuriöses, exklusives Design',
        'features': ['Premium Materialien', 'Exklusive Farben', 'Luxuriöse Details'],
    },
    'clean': {
        'name': 'Clean',
        'description': 'Sauberes, minimalistisches Design',
        'features': ['Klare Linien', 'Viel Weißraum', 'Fokus auf Inhalt'],
    },
    'professional': {
        'name': 'Professional',
        'description': 'Professionelles Business-Design',
        'features': ['Business-Fokus', 'Vertrauensvolle Farben', 'Strukturierte Inhalte'],
    },
    'startup': {
        'name': 'Startup',
        'description': 'Modernes Startup-Design',
        'features': ['Innovative Elemente', 'Moderne Farben', 'Startup-Ästhetik'],
    },
    'premium': {
        'name': 'Premium',
        'description': 'Hochwertiges Premium-Design',
        'features': ['Premium Qualität', 'Exklusive Gestaltung', 'Hochwertige Details'],
    },
}

def get_supported_templates():
    """
    Gibt alle unterstützten Templates zurück
    
    Returns:
        dict: Template-Konfiguration
    """
    return TEMPLATE_CONFIG

def get_generator_config():
    """
    Gibt die Generator-Konfiguration zurück
    
    Returns:
        dict: Generator-Konfiguration
    """
    return GENERATOR_CONFIG

def validate_template_type(template_type):
    """
    Validiert einen Template-Typ
    
    Args:
        template_type: Zu validierender Template-Typ
        
    Returns:
        bool: True wenn Template unterstützt wird
    """
    return template_type in GENERATOR_CONFIG['supported_templates']

def get_template_info(template_type):
    """
    Gibt Informationen zu einem Template zurück
    
    Args:
        template_type: Template-Typ
        
    Returns:
        dict: Template-Informationen oder None
    """
    return TEMPLATE_CONFIG.get(template_type) 