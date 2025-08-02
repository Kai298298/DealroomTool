"""
Video-Processor für Dealroom-Videos
==================================

Diese Datei verarbeitet Videos für die generierten Webseiten.
Sie unterstützt sowohl YouTube/Vimeo-Links als auch lokale Video-Dateien.

Funktionsweise:
1. YouTube/Vimeo-Links werden in Embed-Code umgewandelt
2. Lokale Videos werden als HTML5-Video-Element eingebettet
3. Verschiedene Video-Formate werden unterstützt
4. Responsive Video-Container werden erstellt

Unterstützte Formate:
- YouTube: youtube.com/watch?v=..., youtu.be/...
- Vimeo: vimeo.com/..., player.vimeo.com/video/...
- Lokale Videos: MP4, WebM, OGG

Verwendung:
    video_processor = VideoProcessor()
    embed_code = video_processor.process_video(dealroom)
"""
import re
import os
from django.conf import settings


class VideoProcessor:
    """
    Verarbeitet Videos für die Webseiten
    
    Diese Klasse kümmert sich um alle Video-bezogenen Aufgaben:
    - YouTube/Vimeo-Links in Embed-Code umwandeln
    - Lokale Videos als HTML5-Video einbetten
    - Video-URLs validieren
    - Responsive Video-Container erstellen
    
    Features:
    - Automatische Erkennung von YouTube/Vimeo-Links
    - HTML5-Video-Support für lokale Dateien
    - Responsive Design
    - Fallback für nicht unterstützte Browser
    """
    
    def process_video(self, dealroom):
        """
        Verarbeitet zentrale Videos eines Dealrooms
        
        Prüft ob ein YouTube/Vimeo-Link oder eine lokale Video-Datei
        vorhanden ist und erstellt entsprechenden HTML-Code.
        
        Args:
            dealroom: Dealroom-Model-Objekt mit Video-Daten
            
        Returns:
            str: HTML-Code für Video-Einbettung oder None
        """
        
        # Prüfe zuerst YouTube/Vimeo-Links
        if dealroom.central_video_url:
            embed_code = self.create_embed_code(dealroom.central_video_url)
            if embed_code:
                return embed_code
        
        # Fallback: Lokale Video-Datei
        elif dealroom.central_video_file:
            return self.process_local_video(dealroom.central_video_file)
        
        # Kein Video vorhanden
        return None
    
    def create_embed_code(self, url):
        """
        Erstellt YouTube/Vimeo Embed-Code
        
        Konvertiert YouTube- oder Vimeo-Links in iframe-Embed-Code
        für die Einbettung in die Website.
        
        Args:
            url: YouTube oder Vimeo URL
            
        Returns:
            str: HTML iframe-Code oder None bei Fehlern
        """
        
        # YouTube-Links verarbeiten
        if 'youtube.com' in url or 'youtu.be' in url:
            video_id = self.extract_youtube_id(url)
            if video_id:
                # Responsive YouTube-Embed mit 16:9 Aspect Ratio
                return f'''
                <div class="video-container">
                    <iframe 
                        src="https://www.youtube.com/embed/{video_id}" 
                        frameborder="0" 
                        allowfullscreen
                        style="width: 100%; height: 0; padding-bottom: 56.25%; position: relative;">
                    </iframe>
                </div>
                '''
        
        # Vimeo-Links verarbeiten
        elif 'vimeo.com' in url:
            video_id = self.extract_vimeo_id(url)
            if video_id:
                # Responsive Vimeo-Embed mit 16:9 Aspect Ratio
                return f'''
                <div class="video-container">
                    <iframe 
                        src="https://player.vimeo.com/video/{video_id}" 
                        frameborder="0" 
                        allowfullscreen
                        style="width: 100%; height: 0; padding-bottom: 56.25%; position: relative;">
                    </iframe>
                </div>
                '''
        
        # Nicht unterstützte Video-Plattform
        return None
    
    def extract_youtube_id(self, url):
        """
        Extrahiert YouTube Video-ID aus verschiedenen URL-Formaten
        
        Unterstützt verschiedene YouTube-URL-Formate:
        - youtube.com/watch?v=VIDEO_ID
        - youtu.be/VIDEO_ID
        - youtube.com/embed/VIDEO_ID
        
        Args:
            url: YouTube URL
            
        Returns:
            str: YouTube Video-ID oder None
        """
        # Verschiedene YouTube-URL-Patterns
        patterns = [
            # Standard YouTube-Watch-URL
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            # YouTube-Embed-URL
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            # YouTube-Short-URL
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
        ]
        
        # Alle Patterns durchgehen
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def extract_vimeo_id(self, url):
        """
        Extrahiert Vimeo Video-ID aus verschiedenen URL-Formaten
        
        Unterstützt verschiedene Vimeo-URL-Formate:
        - vimeo.com/VIDEO_ID
        - player.vimeo.com/video/VIDEO_ID
        
        Args:
            url: Vimeo URL
            
        Returns:
            str: Vimeo Video-ID oder None
        """
        # Verschiedene Vimeo-URL-Patterns
        patterns = [
            # Standard Vimeo-URL
            r'vimeo\.com/(\d+)',
            # Vimeo-Player-URL
            r'player\.vimeo\.com/video/(\d+)',
        ]
        
        # Alle Patterns durchgehen
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def process_local_video(self, video_file):
        """
        Verarbeitet lokales Video als HTML5-Video
        
        Erstellt HTML5-Video-Element mit verschiedenen Formaten
        für maximale Browser-Kompatibilität.
        
        Args:
            video_file: Django FileField-Objekt
            
        Returns:
            str: HTML5-Video-Code oder None
        """
        if video_file and hasattr(video_file, 'url'):
            video_url = video_file.url
            video_name = os.path.basename(video_file.name)
            
            # HTML5-Video mit mehreren Formaten für Kompatibilität
            return f'''
            <div class="video-container">
                <video controls style="width: 100%; max-width: 800px;">
                    <!-- MP4 Format (am besten unterstützt) -->
                    <source src="{video_url}" type="video/mp4">
                    <!-- WebM Format (moderne Browser) -->
                    <source src="{video_url}" type="video/webm">
                    <!-- OGG Format (ältere Browser) -->
                    <source src="{video_url}" type="video/ogg">
                    
                    <!-- Fallback für Browser ohne Video-Support -->
                    <p>Ihr Browser unterstützt keine Video-Wiedergabe.</p>
                    <a href="{video_url}" download="{video_name}" class="btn btn-primary">
                        <i class="fas fa-download"></i> Video herunterladen
                    </a>
                </video>
            </div>
            '''
        
        return None
    
    def validate_video_url(self, url):
        """
        Validiert Video-URL und gibt Feedback
        
        Prüft ob eine URL ein unterstütztes Video-Format ist
        und gibt entsprechendes Feedback zurück.
        
        Args:
            url: Zu validierende URL
            
        Returns:
            tuple: (is_valid, message)
        """
        if not url:
            return False, "Keine URL angegeben"
        
        # YouTube-URLs validieren
        if 'youtube.com' in url or 'youtu.be' in url:
            video_id = self.extract_youtube_id(url)
            if not video_id:
                return False, "Ungültige YouTube-URL"
            return True, f"YouTube Video erkannt (ID: {video_id})"
        
        # Vimeo-URLs validieren
        elif 'vimeo.com' in url:
            video_id = self.extract_vimeo_id(url)
            if not video_id:
                return False, "Ungültige Vimeo-URL"
            return True, f"Vimeo Video erkannt (ID: {video_id})"
        
        # Nicht unterstützte Plattform
        return False, "Nicht unterstützte Video-Plattform (nur YouTube/Vimeo)"
    
    def get_video_thumbnail(self, url):
        """
        Generiert Thumbnail-URL für Videos
        
        Erstellt Thumbnail-URLs für YouTube und Vimeo Videos.
        
        Args:
            url: Video-URL
            
        Returns:
            str: Thumbnail-URL oder None
        """
        # YouTube Thumbnail
        if 'youtube.com' in url or 'youtu.be' in url:
            video_id = self.extract_youtube_id(url)
            if video_id:
                return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        
        # Vimeo Thumbnail (würde API-Aufruf benötigen)
        elif 'vimeo.com' in url:
            video_id = self.extract_vimeo_id(url)
            if video_id:
                # Für Vimeo bräuchte man die API
                return None
        
        return None 