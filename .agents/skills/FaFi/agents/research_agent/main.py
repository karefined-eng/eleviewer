"""
Research Agent
==============
Orchestriert mehrere Skills für umfassende Recherchen.
"""

import os
import sys
from typing import Dict, Any, List

# Füge Pfade hinzu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from skills.web_scraper.main import execute as scrape_web
from skills.text_summarizer.main import execute as summarize_text


def execute(topic: str, 
            depth: str = "standard",
            sources: List[str] = None) -> Dict[str, Any]:
    """
    Führt eine Recherche zu einem Thema durch.
    
    Args:
        topic: Das zu recherchierende Thema
        depth: Tiefe der Recherche (quick, standard, deep)
        sources: Optionale Liste von URLs
        
    Returns:
        Dictionary mit report, sources_used, key_findings
    """
    # Konfiguration basierend auf Tiefe
    config = {
        'quick': {'max_sources': 2, 'summary_length': 100},
        'standard': {'max_sources': 5, 'summary_length': 200},
        'deep': {'max_sources': 10, 'summary_length': 400}
    }
    
    settings = config.get(depth, config['standard'])
    
    # Sammle Inhalte
    collected_content = []
    sources_used = []
    
    if sources:
        # Nutze bereitgestellte Quellen
        for url in sources[:settings['max_sources']]:
            try:
                result = scrape_web(url, 'text')
                if result.get('content') and len(result['content']) > 100:
                    collected_content.append({
                        'url': url,
                        'title': result.get('title', 'Unbekannt'),
                        'content': result['content']
                    })
                    sources_used.append({
                        'url': url,
                        'title': result.get('title', 'Unbekannt')
                    })
            except Exception as e:
                print(f"Fehler bei {url}: {e}")
    
    # Generiere Bericht
    if collected_content:
        # Kombiniere alle Inhalte
        combined_text = "\n\n".join([
            f"Quelle: {c['title']}\n{c['content'][:2000]}"
            for c in collected_content
        ])
        
        # Zusammenfassung erstellen
        summary_result = summarize_text(
            combined_text,
            max_length=settings['summary_length'],
            style='formal'
        )
        
        report = f"""
# Recherchebericht: {topic}

## Zusammenfassung

{summary_result['summary']}

## Quellen

"""
        for i, source in enumerate(sources_used, 1):
            report += f"{i}. [{source['title']}]({source['url']})\n"
        
        # Extrahiere Key Findings (vereinfacht)
        key_findings = _extract_key_findings(collected_content, topic)
        
    else:
        report = f"""
# Recherchebericht: {topic}

Keine Inhalte gefunden. Bitte stellen Sie URLs als Quellen bereit.
"""
        key_findings = []
    
    return {
        'report': report,
        'sources_used': sources_used,
        'key_findings': key_findings
    }


def _extract_key_findings(content_list: List[Dict], topic: str) -> List[str]:
    """Extrahiert wichtige Erkenntnisse aus den Inhalten."""
    findings = []
    
    # Einfache Keyword-basierte Extraktion
    keywords = topic.lower().split()
    
    for content in content_list:
        text = content['content'].lower()
        sentences = text.replace('\n', ' ').split('.')
        
        for sentence in sentences:
            # Prüfe ob Satz relevant ist
            if any(kw in sentence for kw in keywords):
                clean_sentence = sentence.strip()
                if 20 < len(clean_sentence) < 200:
                    findings.append(clean_sentence.capitalize() + '.')
                    if len(findings) >= 5:
                        break
        
        if len(findings) >= 5:
            break
    
    return findings[:5]


# Für direkten Aufruf
if __name__ == "__main__":
    import json
    
    # Beispielaufruf
    result = execute(
        topic="Künstliche Intelligenz",
        depth="quick",
        sources=["https://de.wikipedia.org/wiki/K%C3%BCnstliche_Intelligenz"]
    )
    
    print(result['report'])
    print("\nKey Findings:")
    for finding in result['key_findings']:
        print(f"- {finding}")
