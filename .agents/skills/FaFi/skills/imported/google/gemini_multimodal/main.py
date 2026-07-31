"""
Gemini Multimodal Skill (Imported)
==================================
Nutzt Google Gemini für multimodale Verarbeitung.
"""

import os
import base64
import requests
from typing import Dict, Any, Optional


def execute(prompt: str, 
            media_type: str = "text", 
            media_url: str = None) -> Dict[str, Any]:
    """
    Führt eine multimodale Anfrage an Gemini durch.
    
    Args:
        prompt: Textanweisung oder Frage
        media_type: Art des Mediums (text, image, video, audio)
        media_url: URL oder Base64 des Mediums
        
    Returns:
        Dictionary mit response und metadata
    """
    api_key = os.environ.get("GOOGLE_AI_API_KEY")
    
    if not api_key:
        return {
            "response": "Fehler: GOOGLE_AI_API_KEY nicht konfiguriert",
            "metadata": {}
        }
    
    # Basis-URL für Gemini API
    base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    model = "gemini-2.0-flash"
    
    # Baue die Anfrage
    contents = []
    parts = []
    
    # Füge Text hinzu
    parts.append({"text": prompt})
    
    # Füge Medium hinzu, falls vorhanden
    if media_type != "text" and media_url:
        media_part = _prepare_media(media_type, media_url)
        if media_part:
            parts.insert(0, media_part)  # Medium vor dem Text
    
    contents.append({"parts": parts})
    
    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/{model}:generateContent?key={api_key}",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extrahiere Antwort
            candidates = result.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                text_response = " ".join([p.get("text", "") for p in parts])
            else:
                text_response = "Keine Antwort generiert"
            
            # Extrahiere Metadaten
            usage = result.get("usageMetadata", {})
            
            return {
                "response": text_response,
                "metadata": {
                    "model": model,
                    "prompt_tokens": usage.get("promptTokenCount", 0),
                    "response_tokens": usage.get("candidatesTokenCount", 0),
                    "total_tokens": usage.get("totalTokenCount", 0)
                }
            }
        else:
            return {
                "response": f"API-Fehler: {response.status_code} - {response.text}",
                "metadata": {}
            }
            
    except Exception as e:
        return {
            "response": f"Fehler: {str(e)}",
            "metadata": {}
        }


def _prepare_media(media_type: str, media_url: str) -> Optional[Dict]:
    """Bereitet Mediendaten für die API vor."""
    
    mime_types = {
        "image": "image/jpeg",
        "video": "video/mp4",
        "audio": "audio/mp3"
    }
    
    mime_type = mime_types.get(media_type, "application/octet-stream")
    
    # Prüfe ob Base64 oder URL
    if media_url.startswith("data:"):
        # Bereits Base64 mit Data-URL
        parts = media_url.split(",", 1)
        if len(parts) == 2:
            return {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": parts[1]
                }
            }
    elif media_url.startswith("http"):
        # URL - lade herunter und konvertiere zu Base64
        try:
            response = requests.get(media_url, timeout=30)
            if response.status_code == 200:
                data = base64.b64encode(response.content).decode("utf-8")
                
                # Versuche MIME-Type aus Response zu ermitteln
                content_type = response.headers.get("Content-Type", mime_type)
                
                return {
                    "inline_data": {
                        "mime_type": content_type,
                        "data": data
                    }
                }
        except:
            pass
    else:
        # Annahme: bereits Base64
        return {
            "inline_data": {
                "mime_type": mime_type,
                "data": media_url
            }
        }
    
    return None


def analyze_image(image_url: str, question: str = "Beschreibe dieses Bild.") -> Dict[str, Any]:
    """Hilfsfunktion zur Bildanalyse."""
    return execute(question, "image", image_url)


def analyze_video(video_url: str, question: str = "Was passiert in diesem Video?") -> Dict[str, Any]:
    """Hilfsfunktion zur Videoanalyse."""
    return execute(question, "video", video_url)


# Für direkten Aufruf
if __name__ == "__main__":
    import json
    
    # Beispiel: Textanfrage
    result = execute("Was ist künstliche Intelligenz?")
    print(json.dumps(result, indent=2, ensure_ascii=False))
