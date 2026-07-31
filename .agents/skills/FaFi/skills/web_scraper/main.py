"""
Web Scraper Skill
=================
Extrahiert Inhalte von Webseiten.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from urllib.parse import urljoin


def execute(url: str, extract_type: str = "text", selector: str = None) -> Dict[str, Any]:
    """
    Extrahiert Inhalte von einer Webseite.
    
    Args:
        url: Die URL der Webseite
        extract_type: Art der Extraktion (text, links, images, all)
        selector: Optionaler CSS-Selektor
        
    Returns:
        Dictionary mit content, links, images, title
    """
    # Hole Webseite
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; SkillHub/1.0)'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        return {
            'content': f"Fehler beim Abrufen der URL: {str(e)}",
            'links': [],
            'images': [],
            'title': ''
        }
    
    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Wende Selektor an, falls angegeben
    if selector:
        target = soup.select(selector)
        if not target:
            return {
                'content': f"Kein Element mit Selektor '{selector}' gefunden",
                'links': [],
                'images': [],
                'title': soup.title.string if soup.title else ''
            }
        # Erstelle neue Soup aus ausgewählten Elementen
        soup = BeautifulSoup(''.join(str(t) for t in target), 'html.parser')
    
    result = {
        'content': '',
        'links': [],
        'images': [],
        'title': ''
    }
    
    # Titel extrahieren
    if soup.title:
        result['title'] = soup.title.string.strip() if soup.title.string else ''
    
    # Text extrahieren
    if extract_type in ['text', 'all']:
        # Entferne Script und Style Tags
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        result['content'] = soup.get_text(separator='\n', strip=True)
    
    # Links extrahieren
    if extract_type in ['links', 'all']:
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            full_url = urljoin(url, href)
            links.append({
                'url': full_url,
                'text': text
            })
        result['links'] = links
    
    # Bilder extrahieren
    if extract_type in ['images', 'all']:
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            alt = img.get('alt', '')
            full_url = urljoin(url, src)
            images.append({
                'url': full_url,
                'alt': alt
            })
        result['images'] = images
    
    return result


# Für direkten Aufruf
if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
        extract_type = sys.argv[2] if len(sys.argv) > 2 else 'text'
        
        result = execute(url, extract_type)
        print(json.dumps(result, indent=2, ensure_ascii=False))
