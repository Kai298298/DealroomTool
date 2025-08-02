"""
CSS-Generator für dynamische Styles
==================================

Generiert CSS-Code basierend auf Dealroom-Konfigurationen
wie Farben, Layouts und Design-Elementen.
"""


class CSSGenerator:
    """
    Generiert dynamisches CSS für Dealroom-Websites
    """
    
    def __init__(self, dealroom):
        """
        Initialisiert den CSS-Generator
        
        Args:
            dealroom: Dealroom-Objekt mit Design-Konfiguration
        """
        self.dealroom = dealroom
        self.primary_color = dealroom.primary_color or '#0d6efd'
        self.secondary_color = dealroom.secondary_color or '#6c757d'
    
    def generate_css(self) -> str:
        """
        Generiert das komplette CSS für die Website
        
        Returns:
            str: CSS-Code
        """
        css_parts = [
            self._generate_reset_css(),
            self._generate_variables_css(),
            self._generate_base_styles(),
            self._generate_header_styles(),
            self._generate_hero_styles(),
            self._generate_content_styles(),
            self._generate_footer_styles(),
            self._generate_responsive_styles()
        ]
        
        return '\n\n'.join(css_parts)
    
    def _generate_reset_css(self) -> str:
        """Generiert CSS-Reset"""
        return """
/* CSS Reset */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
}
"""
    
    def _generate_variables_css(self) -> str:
        """Generiert CSS-Variablen"""
        return f"""
/* CSS Variables */
:root {{
    --primary-color: {self.primary_color};
    --secondary-color: {self.secondary_color};
    --text-color: #333;
    --light-gray: #f8f9fa;
    --border-color: #dee2e6;
}}
"""
    
    def _generate_base_styles(self) -> str:
        """Generiert Basis-Styles"""
        return """
/* Base Styles */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
}

.btn {
    display: inline-block;
    padding: 10px 20px;
    background-color: var(--primary-color);
    color: white;
    text-decoration: none;
    border-radius: 5px;
    transition: background-color 0.3s;
}

.btn:hover {
    background-color: var(--secondary-color);
}
"""
    
    def _generate_header_styles(self) -> str:
        """Generiert Header-Styles"""
        return """
/* Header Styles */
.header {
    background-color: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    padding: 1rem 0;
}

.nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary-color);
}
"""
    
    def _generate_hero_styles(self) -> str:
        """Generiert Hero-Section Styles"""
        return """
/* Hero Section */
.hero {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 4rem 0;
    text-align: center;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.hero p {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}
"""
    
    def _generate_content_styles(self) -> str:
        """Generiert Content-Styles"""
        return """
/* Content Styles */
.content {
    padding: 3rem 0;
}

.section {
    margin-bottom: 3rem;
}

.section h2 {
    color: var(--primary-color);
    margin-bottom: 1rem;
}

/* File Download Section */
.files-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-top: 1rem;
}

.file-card {
    background: white;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.2s, box-shadow 0.2s;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.file-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.file-icon {
    flex-shrink: 0;
    width: 50px;
    height: 50px;
    background: var(--light-gray);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
}

.file-icon::before {
    content: "📄";
}

.file-icon-pdf::before { content: "📕"; }
.file-icon-doc::before { content: "📘"; }
.file-icon-docx::before { content: "📘"; }
.file-icon-xls::before { content: "📊"; }
.file-icon-xlsx::before { content: "📊"; }
.file-icon-ppt::before { content: "📑"; }
.file-icon-pptx::before { content: "📑"; }
.file-icon-jpg::before { content: "🖼️"; }
.file-icon-jpeg::before { content: "🖼️"; }
.file-icon-png::before { content: "🖼️"; }
.file-icon-gif::before { content: "🖼️"; }
.file-icon-mp4::before { content: "🎥"; }
.file-icon-mov::before { content: "🎥"; }
.file-icon-avi::before { content: "🎥"; }
.file-icon-mp3::before { content: "🎵"; }
.file-icon-wav::before { content: "🎵"; }
.file-icon-zip::before { content: "📦"; }
.file-icon-rar::before { content: "📦"; }
.file-icon-txt::before { content: "📄"; }

.file-info {
    flex: 1;
    min-width: 0;
}

.file-info h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
    color: var(--text-color);
}

.file-info p {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    color: #666;
    line-height: 1.4;
}

.file-size {
    font-size: 0.8rem;
    color: #888;
    font-weight: 500;
}

.file-actions {
    flex-shrink: 0;
}

.btn-download {
    background: var(--primary-color);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    text-decoration: none;
    font-size: 0.9rem;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: background-color 0.2s;
}

.btn-download:hover {
    background: var(--secondary-color);
    color: white;
    text-decoration: none;
}

.download-icon::before {
    content: "⬇️";
    font-size: 0.8rem;
}

/* Contact Info Styles */
.contact-info p {
    margin-bottom: 0.5rem;
}

.contact-info a {
    color: var(--primary-color);
    text-decoration: none;
}

.contact-info a:hover {
    text-decoration: underline;
}
"""
    
    def _generate_footer_styles(self) -> str:
        """Generiert Footer-Styles"""
        return """
/* Footer Styles */
.footer {
    background-color: var(--light-gray);
    padding: 2rem 0;
    text-align: center;
    margin-top: 3rem;
}
"""
    
    def _generate_responsive_styles(self) -> str:
        """Generiert responsive Styles"""
        return """
/* Responsive Design */
@media (max-width: 768px) {
    .hero h1 {
        font-size: 2rem;
    }
    
    .hero p {
        font-size: 1rem;
    }
    
    .container {
        padding: 0 10px;
    }
}
""" 