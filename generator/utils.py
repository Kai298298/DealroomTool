"""
Utility-Funktionen für den Website-Generator
==========================================

Hilfsfunktionen für Datei-Operationen, Validierung und
allgemeine Utilities für den Generator.
"""

import os
import shutil
import re
from pathlib import Path
from typing import Optional, Union


def create_directory(directory_path: str) -> bool:
    """
    Erstellt ein Verzeichnis falls es nicht existiert
    
    Args:
        directory_path: Pfad zum zu erstellenden Verzeichnis
        
    Returns:
        bool: True wenn erfolgreich erstellt oder bereits existiert
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception:
        return False


def copy_media_files(source_dir: str, target_dir: str) -> bool:
    """
    Kopiert Mediendateien von einem Verzeichnis zu einem anderen
    
    Args:
        source_dir: Quellverzeichnis
        target_dir: Zielverzeichnis
        
    Returns:
        bool: True wenn erfolgreich kopiert
    """
    try:
        if not os.path.exists(source_dir):
            return False
            
        create_directory(target_dir)
        
        for filename in os.listdir(source_dir):
            source_file = os.path.join(source_dir, filename)
            target_file = os.path.join(target_dir, filename)
            
            if os.path.isfile(source_file):
                shutil.copy2(source_file, target_file)
                
        return True
    except Exception:
        return False


def validate_file_path(file_path: str) -> bool:
    """
    Validiert einen Dateipfad
    
    Args:
        file_path: Zu validierender Pfad
        
    Returns:
        bool: True wenn Pfad gültig ist
    """
    try:
        # Prüfe ob Pfad existiert und lesbar ist
        return os.path.exists(file_path) and os.access(file_path, os.R_OK)
    except Exception:
        return False


def get_file_size_mb(file_path: str) -> float:
    """
    Gibt die Dateigröße in MB zurück
    
    Args:
        file_path: Pfad zur Datei
        
    Returns:
        float: Dateigröße in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0.0


def sanitize_filename(filename: str) -> str:
    """
    Bereinigt einen Dateinamen für sicheres Speichern
    
    Args:
        filename: Ursprünglicher Dateiname
        
    Returns:
        str: Bereinigter Dateiname
    """
    # Entferne ungültige Zeichen
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Ersetze Leerzeichen durch Unterstriche
    filename = filename.replace(' ', '_')
    
    # Begrenze Länge
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
        
    return filename


def get_file_extension(file_path: str) -> str:
    """
    Gibt die Dateiendung zurück
    
    Args:
        file_path: Pfad zur Datei
        
    Returns:
        str: Dateiendung (mit Punkt)
    """
    return os.path.splitext(file_path)[1].lower()


def is_image_file(file_path: str) -> bool:
    """
    Prüft ob es sich um eine Bilddatei handelt
    
    Args:
        file_path: Pfad zur Datei
        
    Returns:
        bool: True wenn Bilddatei
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
    return get_file_extension(file_path) in image_extensions


def is_video_file(file_path: str) -> bool:
    """
    Prüft ob es sich um eine Videodatei handelt
    
    Args:
        file_path: Pfad zur Datei
        
    Returns:
        bool: True wenn Videodatei
    """
    video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'}
    return get_file_extension(file_path) in video_extensions


def is_document_file(file_path: str) -> bool:
    """
    Prüft ob es sich um eine Dokumentdatei handelt
    
    Args:
        file_path: Pfad zur Datei
        
    Returns:
        bool: True wenn Dokumentdatei
    """
    document_extensions = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.ppt', '.pptx'}
    return get_file_extension(file_path) in document_extensions


def format_file_size(size_bytes: int) -> str:
    """
    Formatiert eine Dateigröße in lesbare Form
    
    Args:
        size_bytes: Größe in Bytes
        
    Returns:
        str: Formatierte Größe (z.B. "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def ensure_unique_filename(file_path: str) -> str:
    """
    Stellt sicher, dass ein Dateiname eindeutig ist
    
    Args:
        file_path: Ursprünglicher Dateipfad
        
    Returns:
        str: Eindeutiger Dateipfad
    """
    if not os.path.exists(file_path):
        return file_path
        
    directory, filename = os.path.split(file_path)
    name, ext = os.path.splitext(filename)
    
    counter = 1
    while os.path.exists(file_path):
        new_filename = f"{name}_{counter}{ext}"
        file_path = os.path.join(directory, new_filename)
        counter += 1
        
    return file_path 