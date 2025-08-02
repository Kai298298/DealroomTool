# Dealroom Dashboard - Automatischer Website-Generator

Ein Django-basiertes Dashboard-System zur Verwaltung von Dealrooms mit automatischer Website-Generierung.

## 📋 Inhaltsverzeichnis

- [Übersicht](#-übersicht)
- [Features](#-features)
- [Installation](#-installation)
- [Systemarchitektur](#-systemarchitektur)
- [Website-Generator](#-website-generator)
- [Verwendung](#-verwendung)
- [API-Dokumentation](#-api-dokumentation)
- [Entwicklung](#-entwicklung)
- [Troubleshooting](#-troubleshooting)

## 🎯 Übersicht

Das Dealroom Dashboard ist ein vollständiges System zur Verwaltung von Dealrooms (Deals/Landing Pages) mit automatischer Website-Generierung. Jeder Dealroom kann individuell konfiguriert werden und generiert automatisch eine vollständige Website.

### Hauptfunktionen:
- **Benutzerverwaltung** mit Rollen (Admin, Manager, Editor, Viewer)
- **Dealroom-Verwaltung** mit umfangreichen Metadaten
- **Automatische Website-Generierung** basierend auf Dealroom-Daten
- **Responsive Templates** (Modern, Classic, Minimal, Corporate)
- **Dynamische CSS-Generierung** mit benutzerdefinierten Farben
- **Video-Integration** (YouTube, Vimeo, lokale Videos)
- **Bild-Galerien** und Dokumentenverwaltung
- **SEO-Optimierung** mit automatischen Sitemaps

## ✨ Features

### 🎨 Design & Templates
- **4 verschiedene Templates**: Modern, Classic, Minimal, Corporate
- **Dynamische Farben**: Jeder Dealroom kann eigene Primär- und Sekundärfarben definieren
- **Responsive Design**: Mobile-first Ansatz für alle Geräte
- **Moderne Animationen**: Hover-Effekte und Transitions

### 📹 Medien-Unterstützung
- **YouTube/Vimeo Integration**: Automatische Embed-Code-Generierung
- **Lokale Videos**: HTML5-Video-Unterstützung
- **Bild-Galerien**: Hero-Bilder, Logos, Galerie-Bilder
- **Dokumentenverwaltung**: PDFs, Präsentationen, etc.

### 🔧 Technische Features
- **Automatische Generierung**: Websites werden bei Dealroom-Änderungen neu generiert
- **SEO-Optimierung**: Automatische Sitemap- und robots.txt-Generierung
- **Lokales Hosting**: Entwicklungsumgebung für generierte Websites
- **Django-Signals**: Automatische Trigger bei Datenänderungen

## 🚀 Installation

### Voraussetzungen
- Python 3.8+
- Django 5.2.4
- Chrome/Chromium (für Selenium-Tests)

### Setup
```bash
# Repository klonen
git clone <repository-url>
cd Dealroom2

# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt

# Datenbank migrieren
python manage.py makemigrations
python manage.py migrate

# Superuser erstellen
python manage.py createsuperuser

# Server starten
python manage.py runserver
```

### Umgebung konfigurieren
```bash
# .env Datei erstellen
cp .env.example .env

# Einstellungen anpassen
# SECRET_KEY, DEBUG, DATABASE_URL, etc.
```

## 🏗️ Systemarchitektur

### Django-Apps
```
dealroom_dashboard/
├── core/                 # Haupt-App (Dashboard, Navigation)
├── users/               # Benutzerverwaltung und Authentifizierung
├── deals/               # Dealroom-Models und -Verwaltung
└── generator/           # Website-Generator-System
```

### Generator-System
```
generator/
├── __init__.py          # Paket-Initialisierung und Konfiguration
├── renderer.py          # Haupt-Generator (DealroomGenerator)
├── css_generator.py     # Dynamische CSS-Generierung
├── video_processor.py   # Video-Verarbeitung (YouTube/Vimeo)
├── image_processor.py   # Bild-Verarbeitung und Galerien
├── utils.py            # Hilfsfunktionen
└── templates/          # HTML-Templates
    ├── modern/         # Modernes Template
    ├── classic/        # Klassisches Template
    ├── minimal/        # Minimalistisches Template
    └── corporate/      # Corporate Template
```

## 🌐 Website-Generator

### Funktionsweise

Der Website-Generator ist das Herzstück des Systems und arbeitet in 11 Schritten:

1. **Status setzen**: `website_status = 'generating'`
2. **Verzeichnisse erstellen**: `generated_pages/dealroom-{id}/`
3. **Template auswählen**: Basierend auf `template_type`
4. **Kontext vorbereiten**: Alle Dealroom-Daten sammeln
5. **HTML generieren**: Template mit Daten rendern
6. **CSS generieren**: Dynamisches CSS mit Dealroom-Farben
7. **Assets verarbeiten**: Bilder, Videos, Dokumente kopieren
8. **Dateien speichern**: HTML, CSS, JS speichern
9. **SEO-Dateien erstellen**: sitemap.xml, robots.txt
10. **URL generieren**: Lokale Website-URL erstellen
11. **Status aktualisieren**: `website_status = 'generated'`

### Generierte Struktur
```
generated_pages/
└── dealroom-{id}/
    ├── index.html          # Hauptseite
    ├── sitemap.xml        # SEO-Sitemap
    ├── robots.txt         # SEO-Robots
    └── assets/
        ├── style.css      # Dynamisches CSS
        ├── script.js      # JavaScript (falls vorhanden)
        ├── images/        # Kopierte Bilder
        ├── videos/        # Kopierte Videos
        └── documents/     # Kopierte Dokumente
```

### Komponenten

#### DealroomGenerator (renderer.py)
- **Zentrale Koordinationsklasse**
- Orchestriert alle anderen Komponenten
- Verwaltet den kompletten Generierungsprozess

#### CSSGenerator (css_generator.py)
- **Dynamische CSS-Generierung**
- CSS-Variablen für Dealroom-Farben
- Responsive Design mit Mobile-first
- Moderne Animationen und Hover-Effekte

#### VideoProcessor (video_processor.py)
- **YouTube/Vimeo Integration**
- Automatische Embed-Code-Generierung
- Lokale Video-Unterstützung
- Responsive Video-Container

#### ImageProcessor (image_processor.py)
- **Bild-Kategorisierung** (Hero, Logo, Galerie)
- Responsive Bild-Galerien
- Lightbox-Funktionalität
- Thumbnail-Generierung

### Automatische Generierung

Das System verwendet Django-Signals für automatische Website-Generierung:

```python
@receiver(post_save, sender=Deal)
def auto_generate_website(sender, instance, created, **kwargs):
    """Generiert automatisch Website bei Dealroom-Änderungen"""
    if instance.status == 'active':
        generator = DealroomGenerator(instance)
        website_url = generator.generate_website()
```

## 📖 Verwendung

### 1. Dealroom erstellen

```python
from deals.models import Deal
from users.models import CustomUser

# Dealroom erstellen
dealroom = Deal.objects.create(
    title="Mein Dealroom",
    slug="mein-dealroom",
    template_type="modern",
    primary_color="#0d6efd",
    secondary_color="#6c757d",
    recipient_name="Max Mustermann",
    recipient_email="max@example.com",
    customer_name="Test Kunde",
    customer_email="kunde@example.com",
    # ... weitere Felder
)
```

### 2. Website manuell generieren

```python
from generator.renderer import DealroomGenerator

# Generator initialisieren
generator = DealroomGenerator(dealroom)

# Website generieren
website_url = generator.generate_website()
print(f"Website generiert: {website_url}")

# Website neu generieren
generator.regenerate_website()

# Website löschen
generator.delete_website()
```

### 3. CSS dynamisch generieren

```python
from generator.css_generator import CSSGenerator

# CSS-Generator
css_generator = CSSGenerator()
css_content = css_generator.generate(dealroom)

# CSS in Datei speichern
with open('style.css', 'w') as f:
    f.write(css_content)
```

### 4. Videos verarbeiten

```python
from generator.video_processor import VideoProcessor

# Video-Processor
video_processor = VideoProcessor()

# YouTube-Video verarbeiten
embed_code = video_processor.create_embed_code("https://youtube.com/watch?v=VIDEO_ID")

# Video-URL validieren
is_valid, message = video_processor.validate_video_url(url)
```

### 5. Bilder verarbeiten

```python
from generator.image_processor import ImageProcessor

# Image-Processor
image_processor = ImageProcessor()

# Alle Bilder verarbeiten
processed_images = image_processor.process_images(dealroom)

# Galerie-HTML generieren
gallery_html = image_processor.generate_gallery_html(images)
```

## 🔧 API-Dokumentation

### DealroomGenerator

#### `__init__(dealroom)`
Initialisiert den Generator mit einem Dealroom-Objekt.

#### `generate_website()`
Generiert eine komplette Website. Returns: Website-URL

#### `delete_website()`
Löscht die generierte Website.

#### `regenerate_website()`
Generiert die Website neu (löscht alte und erstellt neue).

### CSSGenerator

#### `generate(dealroom)`
Generiert CSS mit Dealroom-Farben. Returns: CSS-String

### VideoProcessor

#### `process_video(dealroom)`
Verarbeitet Videos eines Dealrooms. Returns: HTML-Code

#### `create_embed_code(url)`
Erstellt Embed-Code für YouTube/Vimeo. Returns: HTML-Code

#### `validate_video_url(url)`
Validiert Video-URL. Returns: (is_valid, message)

### ImageProcessor

#### `process_images(dealroom)`
Verarbeitet alle Bilder eines Dealrooms. Returns: Dict mit Kategorien

#### `generate_gallery_html(images)`
Generiert HTML für Bildergalerie. Returns: HTML-String

### Utility-Funktionen

#### `create_directory(path)`
Erstellt Verzeichnis falls nicht vorhanden.

#### `copy_media_files(source_file, destination_dir)`
Kopiert Media-Dateien in Zielverzeichnis.

#### `validate_file_path(path)`
Validiert Datei-Pfad auf Sicherheit.

## 🛠️ Entwicklung

### Tests ausführen

```bash
# Selenium-Tests (Browser-basiert)
python test_complete_system.py

# Django-Tests (ohne Browser)
python test_basic_functionality.py

# Spezifische Tests
python manage.py test deals.tests
python manage.py test users.tests
```

### Neues Template hinzufügen

1. **Template-Verzeichnis erstellen**:
```
generator/templates/mein_template/
├── base.html
├── style.css
└── script.js
```

2. **Template registrieren**:
```python
# generator/__init__.py
GENERATOR_CONFIG['supported_templates'].append('mein_template')

TEMPLATE_CONFIG['mein_template'] = {
    'name': 'Mein Template',
    'description': 'Beschreibung des Templates',
    'features': ['Feature 1', 'Feature 2'],
}
```

3. **Template-Mapping hinzufügen**:
```python
# generator/renderer.py
template_map = {
    'mein_template': 'generator/templates/mein_template/base.html',
    # ... bestehende Templates
}
```

### Neue Dateitypen hinzufügen

```python
# generator/utils.py
def is_new_file_type(filename):
    """Prüft ob Datei neuer Typ ist"""
    new_extensions = ['.newext']
    extension = get_file_extension(filename)
    return extension in new_extensions
```

## 🔍 Troubleshooting

### Häufige Probleme

#### 1. Website wird nicht generiert
```bash
# Status prüfen
python manage.py shell
>>> from deals.models import Deal
>>> deal = Deal.objects.get(id=1)
>>> print(deal.website_status)
>>> print(deal.generation_error)
```

#### 2. Bilder werden nicht angezeigt
```bash
# Media-Verzeichnis prüfen
ls -la media/
ls -la generated_pages/dealroom-1/assets/images/
```

#### 3. CSS-Farben werden nicht angewendet
```bash
# CSS-Datei prüfen
cat generated_pages/dealroom-1/assets/style.css
```

#### 4. Videos werden nicht eingebettet
```python
# Video-URL validieren
from generator.video_processor import VideoProcessor
processor = VideoProcessor()
is_valid, message = processor.validate_video_url(url)
print(message)
```

### Debug-Modus

```python
# Detaillierte Logs aktivieren
import logging
logging.basicConfig(level=logging.DEBUG)

# Generator mit Debug-Info
generator = DealroomGenerator(dealroom)
generator.generate_website()
```

### Performance-Optimierung

```python
# Große Dateien vermeiden
GENERATOR_CONFIG['max_file_size_mb'] = 10

# Caching aktivieren
from django.core.cache import cache
cache.set('generated_website', website_content, timeout=3600)
```

## 📝 Changelog

### Version 1.0.0
- ✅ Automatische Website-Generierung
- ✅ 4 responsive Templates
- ✅ YouTube/Vimeo Integration
- ✅ Dynamische CSS-Generierung
- ✅ Bild-Galerien und Lightbox
- ✅ SEO-Optimierung
- ✅ Django-Signals für automatische Generierung

## 🤝 Beitragen

1. Fork das Repository
2. Feature-Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'Add some AmazingFeature'`)
4. Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request erstellen

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

## 📞 Support

Bei Fragen oder Problemen:
- GitHub Issues erstellen
- Dokumentation durchsuchen
- Debug-Modus aktivieren

---

**Entwickelt mit ❤️ für das Dealroom Dashboard Team** 