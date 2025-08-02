"""
Video-Processor für YouTube/Vimeo Integration
===========================================

Verarbeitet Video-URLs und erstellt eingebettete Player.
"""

import re
from urllib.parse import urlparse, parse_qs


class VideoProcessor:
    """
    Verarbeitet Video-URLs und erstellt eingebettete Player
    """
    
    def __init__(self):
        """Initialisiert den Video-Processor"""
        self.youtube_pattern = r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)'
        self.vimeo_pattern = r'vimeo\.com\/(\d+)'
    
    def extract_video_id(self, url: str) -> str:
        """
        Extrahiert die Video-ID aus einer URL
        
        Args:
            url: Video-URL
            
        Returns:
            str: Video-ID oder leerer String
        """
        if not url:
            return ""
            
        # YouTube
        youtube_match = re.search(self.youtube_pattern, url)
        if youtube_match:
            return youtube_match.group(1)
        
        # Vimeo
        vimeo_match = re.search(self.vimeo_pattern, url)
        if vimeo_match:
            return vimeo_match.group(1)
        
        return ""
    
    def get_video_type(self, url: str) -> str:
        """
        Bestimmt den Typ des Videos
        
        Args:
            url: Video-URL
            
        Returns:
            str: 'youtube', 'vimeo' oder 'unknown'
        """
        if re.search(self.youtube_pattern, url):
            return 'youtube'
        elif re.search(self.vimeo_pattern, url):
            return 'vimeo'
        else:
            return 'unknown'
    
    def create_embed_code(self, url: str, width: int = 560, height: int = 315) -> str:
        """
        Erstellt HTML-Embed-Code für ein Video
        
        Args:
            url: Video-URL
            width: Breite des Players
            height: Höhe des Players
            
        Returns:
            str: HTML-Embed-Code
        """
        video_id = self.extract_video_id(url)
        video_type = self.get_video_type(url)
        
        if not video_id:
            return f'<p>Ungültige Video-URL: {url}</p>'
        
        if video_type == 'youtube':
            return self._create_youtube_embed(video_id, width, height)
        elif video_type == 'vimeo':
            return self._create_vimeo_embed(video_id, width, height)
        else:
            return f'<p>Nicht unterstützter Video-Typ: {url}</p>'
    
    def _create_youtube_embed(self, video_id: str, width: int, height: int) -> str:
        """Erstellt YouTube Embed-Code"""
        return f'''
        <div class="video-container">
            <iframe 
                width="{width}" 
                height="{height}" 
                src="https://www.youtube.com/embed/{video_id}" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen>
            </iframe>
        </div>
        '''
    
    def _create_vimeo_embed(self, video_id: str, width: int, height: int) -> str:
        """Erstellt Vimeo Embed-Code"""
        return f'''
        <div class="video-container">
            <iframe 
                width="{width}" 
                height="{height}" 
                src="https://player.vimeo.com/video/{video_id}" 
                frameborder="0" 
                allow="autoplay; fullscreen; picture-in-picture" 
                allowfullscreen>
            </iframe>
        </div>
        '''
    
    def validate_video_url(self, url: str) -> bool:
        """
        Validiert eine Video-URL
        
        Args:
            url: Zu validierende URL
            
        Returns:
            bool: True wenn URL gültig ist
        """
        if not url:
            return False
            
        video_type = self.get_video_type(url)
        return video_type in ['youtube', 'vimeo'] 