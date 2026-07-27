"""
File Reader Skill
=================
Liest verschiedene Dateiformate und extrahiert Text.
"""

import os
from typing import Dict, Any
from datetime import datetime


def execute(file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """
    Liest eine Datei und extrahiert deren Inhalt.
    
    Args:
        file_path: Pfad zur Datei
        encoding: Zeichenkodierung für Textdateien
        
    Returns:
        Dictionary mit content, file_type, metadata
    """
    if not os.path.exists(file_path):
        return {
            'content': f"Datei nicht gefunden: {file_path}",
            'file_type': 'unknown',
            'metadata': {}
        }
    
    # Metadaten sammeln
    stat = os.stat(file_path)
    metadata = {
        'size_bytes': stat.st_size,
        'size_human': _human_readable_size(stat.st_size),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
    }
    
    # Dateityp erkennen
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    file_type = _detect_file_type(ext)
    
    # Inhalt basierend auf Typ extrahieren
    try:
        if file_type == 'text':
            content = _read_text_file(file_path, encoding)
        elif file_type == 'json':
            content = _read_json_file(file_path)
        elif file_type == 'csv':
            content = _read_csv_file(file_path, encoding)
        elif file_type == 'pdf':
            content = _read_pdf_file(file_path)
        elif file_type == 'docx':
            content = _read_docx_file(file_path)
        elif file_type == 'markdown':
            content = _read_text_file(file_path, encoding)
        else:
            content = f"Dateityp '{ext}' wird nicht unterstützt"
            
    except Exception as e:
        content = f"Fehler beim Lesen: {str(e)}"
    
    return {
        'content': content,
        'file_type': file_type,
        'metadata': metadata
    }


def _detect_file_type(ext: str) -> str:
    """Erkennt den Dateityp basierend auf der Erweiterung."""
    type_mapping = {
        '.txt': 'text',
        '.md': 'markdown',
        '.json': 'json',
        '.csv': 'csv',
        '.pdf': 'pdf',
        '.docx': 'docx',
        '.doc': 'doc',
        '.py': 'text',
        '.js': 'text',
        '.html': 'text',
        '.xml': 'text',
        '.yaml': 'text',
        '.yml': 'text'
    }
    return type_mapping.get(ext, 'unknown')


def _human_readable_size(size_bytes: int) -> str:
    """Konvertiert Bytes in lesbare Größe."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def _read_text_file(file_path: str, encoding: str) -> str:
    """Liest eine Textdatei."""
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()


def _read_json_file(file_path: str) -> str:
    """Liest eine JSON-Datei und formatiert sie."""
    import json
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return json.dumps(data, indent=2, ensure_ascii=False)


def _read_csv_file(file_path: str, encoding: str) -> str:
    """Liest eine CSV-Datei und konvertiert zu Text."""
    import csv
    rows = []
    with open(file_path, 'r', encoding=encoding) as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(' | '.join(row))
    return '\n'.join(rows)


def _read_pdf_file(file_path: str) -> str:
    """Liest eine PDF-Datei."""
    try:
        import subprocess
        result = subprocess.run(
            ['pdftotext', '-layout', file_path, '-'],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception:
        return "PDF-Extraktion fehlgeschlagen. pdftotext nicht verfügbar."


def _read_docx_file(file_path: str) -> str:
    """Liest eine DOCX-Datei."""
    try:
        from docx import Document
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs]
        return '\n\n'.join(paragraphs)
    except ImportError:
        return "python-docx nicht installiert"
    except Exception as e:
        return f"Fehler beim Lesen der DOCX: {str(e)}"


# Für direkten Aufruf
if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) > 1:
        path = sys.argv[1]
        result = execute(path)
        print(f"Typ: {result['file_type']}")
        print(f"Metadaten: {json.dumps(result['metadata'], indent=2)}")
        print(f"\nInhalt:\n{result['content'][:1000]}...")
