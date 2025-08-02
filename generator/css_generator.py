"""
CSS-Generator für dynamische Styles basierend auf Dealroom-Daten
==============================================================

Diese Datei generiert dynamisches CSS basierend auf den Farben und
Einstellungen eines Dealrooms. Das CSS wird zur Laufzeit erstellt
und passt sich automatisch an die benutzerdefinierten Farben an.

Funktionsweise:
1. Nimmt einen Dealroom als Input
2. Extrahiert die benutzerdefinierten Farben (primary_color, secondary_color)
3. Generiert vollständiges CSS mit CSS-Variablen
4. Erstellt responsive, moderne Styles
5. Fügt Animationen und Hover-Effekte hinzu

Verwendung:
    css_generator = CSSGenerator()
    css_content = css_generator.generate(dealroom)
"""


class CSSGenerator:
    """
    Generiert dynamisches CSS basierend auf Dealroom-Daten
    
    Diese Klasse erstellt vollständiges CSS für die generierten Websites.
    Das CSS verwendet CSS-Variablen (Custom Properties) um sich dynamisch
    an die benutzerdefinierten Farben des Dealrooms anzupassen.
    
    Features:
    - Responsive Design (Mobile-first)
    - CSS-Variablen für dynamische Farben
    - Moderne Animationen und Transitions
    - Hover-Effekte und Interaktionen
    - Flexbox und Grid Layouts
    - Status-Badges und Utility-Klassen
    """
    
    def generate(self, dealroom):
        """
        Generiert CSS mit benutzerdefinierten Farben und Styles
        
        Erstellt vollständiges CSS basierend auf den Farben und
        Einstellungen des Dealrooms. Das CSS ist responsiv und
        modern gestaltet.
        
        Args:
            dealroom: Dealroom-Model-Objekt mit Farben und Einstellungen
            
        Returns:
            str: Vollständiges CSS als String
        """
        
        # CSS-Template mit CSS-Variablen für dynamische Farben
        css_template = f"""
/* Dealroom Website - {dealroom.title} */
/* Generiert am: {dealroom.last_generation or 'Unbekannt'} */
/* Template: {dealroom.template_type} */

/* CSS-Variablen für dynamische Farben */
/* Diese Variablen werden mit den Dealroom-Farben gefüllt */
:root {{
    --primary-color: {dealroom.primary_color};      /* Hauptfarbe des Dealrooms */
    --secondary-color: {dealroom.secondary_color};  /* Sekundärfarbe des Dealrooms */
    --text-color: #333333;                         /* Standard-Textfarbe */
    --background-color: #ffffff;                   /* Hintergrundfarbe */
    --light-gray: #f8f9fa;                        /* Helles Grau für Hintergründe */
    --border-color: #dee2e6;                      /* Rahmenfarbe */
    --shadow: 0 2px 10px rgba(0,0,0,0.1);        /* Standard-Schatten */
    --transition: all 0.3s ease;                  /* Standard-Animation */
}}

/* CSS Reset und Basis-Styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--background-color);
}}

/* Header-Styles */
/* Hero-Bereich mit Gradient-Hintergrund */
.header {{
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 2rem 0;
    text-align: center;
}}

.header h1 {{
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    font-weight: 700;
}}

.header p {{
    font-size: 1.2rem;
    opacity: 0.9;
}}

/* Navigation-Styles */
/* Sticky Navigation mit Schatten */
.nav {{
    background: white;
    box-shadow: var(--shadow);
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 1000;
}}

.nav-container {{
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
}}

.nav-logo {{
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary-color);
}}

.nav-menu {{
    display: flex;
    list-style: none;
    gap: 2rem;
}}

.nav-menu a {{
    text-decoration: none;
    color: var(--text-color);
    font-weight: 500;
    transition: var(--transition);
}}

.nav-menu a:hover {{
    color: var(--primary-color);
}}

/* Hauptinhalt-Styles */
.main {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}}

.section {{
    margin-bottom: 4rem;
}}

.section-title {{
    font-size: 2rem;
    color: var(--primary-color);
    margin-bottom: 1.5rem;
    text-align: center;
}}

/* Hero-Section Styles */
/* Prominenter Bereich mit Call-to-Action */
.hero {{
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 4rem 2rem;
    text-align: center;
    border-radius: 10px;
    margin-bottom: 3rem;
}}

.hero h2 {{
    font-size: 3rem;
    margin-bottom: 1rem;
    font-weight: 700;
}}

.hero p {{
    font-size: 1.3rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}}

/* Call-to-Action Button */
.cta-button {{
    background-color: white;
    color: var(--primary-color);
    padding: 1rem 2rem;
    border: none;
    border-radius: 50px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: var(--transition);
    text-decoration: none;
    display: inline-block;
}}

.cta-button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    text-decoration: none;
    color: var(--primary-color);
}}

/* Info-Cards Grid */
/* Responsive Grid für Informationskarten */
.info-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-bottom: 3rem;
}}

.info-card {{
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: var(--shadow);
    transition: var(--transition);
}}

.info-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 5px 20px rgba(0,0,0,0.15);
}}

.info-card h3 {{
    color: var(--primary-color);
    margin-bottom: 1rem;
    font-size: 1.5rem;
}}

.info-card p {{
    color: #666;
    line-height: 1.6;
}}

/* Video-Section Styles */
/* Responsive Video-Container */
.video-section {{
    text-align: center;
    margin: 3rem 0;
}}

.video-container {{
    max-width: 800px;
    margin: 0 auto;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: var(--shadow);
}}

.video-container iframe {{
    width: 100%;
    height: 450px;
    border: none;
}}

/* Datei-Galerie Styles */
/* Grid für Dateien und Dokumente */
.file-gallery {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}}

.file-item {{
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: var(--shadow);
    text-align: center;
    transition: var(--transition);
}}

.file-item:hover {{
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.15);
}}

.file-item h4 {{
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}}

.file-item p {{
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}}

.file-link {{
    background: var(--primary-color);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    text-decoration: none;
    font-size: 0.9rem;
    transition: var(--transition);
}}

.file-link:hover {{
    background: var(--secondary-color);
    text-decoration: none;
    color: white;
}}

/* Kontakt-Section Styles */
/* Hervorgehobener Kontaktbereich */
.contact-section {{
    background: var(--light-gray);
    padding: 3rem 2rem;
    border-radius: 10px;
    text-align: center;
}}

.contact-info {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}}

.contact-item {{
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: var(--shadow);
}}

.contact-item h4 {{
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}}

.contact-item p {{
    color: #666;
}}

/* Footer-Styles */
/* Dunkler Footer mit Copyright */
.footer {{
    background: var(--text-color);
    color: white;
    text-align: center;
    padding: 2rem;
    margin-top: 4rem;
}}

.footer p {{
    opacity: 0.8;
}}

/* Responsive Design */
/* Mobile-first Ansatz mit Breakpoints */
@media (max-width: 768px) {{
    .header h1 {{
        font-size: 2rem;
    }}
    
    .hero h2 {{
        font-size: 2.5rem;
    }}
    
    .nav-menu {{
        flex-direction: column;
        gap: 1rem;
    }}
    
    .info-grid {{
        grid-template-columns: 1fr;
    }}
    
    .file-gallery {{
        grid-template-columns: 1fr;
    }}
    
    .contact-info {{
        grid-template-columns: 1fr;
    }}
}}

/* Loading-Animation */
/* Spinner für Ladezustände */
.loading {{
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255,255,255,.3);
    border-radius: 50%;
    border-top-color: #fff;
    animation: spin 1s ease-in-out infinite;
}}

@keyframes spin {{
    to {{ transform: rotate(360deg); }}
}}

/* Status-Badges */
/* Farbkodierte Status-Anzeigen */
.status-badge {{
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
}}

.status-active {{
    background: #28a745;
    color: white;
}}

.status-draft {{
    background: #6c757d;
    color: white;
}}

.status-inactive {{
    background: #ffc107;
    color: #212529;
}}

/* Utility-Klassen */
/* Hilfsklassen für häufige Styling-Aufgaben */
.text-center {{ text-align: center; }}
.text-primary {{ color: var(--primary-color); }}
.text-secondary {{ color: var(--secondary-color); }}
.mb-1 {{ margin-bottom: 0.5rem; }}
.mb-2 {{ margin-bottom: 1rem; }}
.mb-3 {{ margin-bottom: 1.5rem; }}
.mt-1 {{ margin-top: 0.5rem; }}
.mt-2 {{ margin-top: 1rem; }}
.mt-3 {{ margin-top: 1.5rem; }}
"""
        
        return css_template 