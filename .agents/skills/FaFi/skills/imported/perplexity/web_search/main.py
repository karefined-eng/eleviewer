"""
Perplexity Web Search Skill (Imported)
======================================
Führt Echtzeit-Websuchen mit der Perplexity API durch.
"""

import os
import requests
from typing import Dict, Any, List


def execute(query: str, focus: str = "web") -> Dict[str, Any]:
    """
    Führt eine Websuche mit Perplexity durch.
    
    Args:
        query: Suchanfrage
        focus: Suchfokus (web, academic, news, youtube, reddit)
        
    Returns:
        Dictionary mit answer und citations
    """
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    
    if not api_key:
        return {
            "answer": "Fehler: PERPLEXITY_API_KEY nicht konfiguriert",
            "citations": []
        }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Baue die Anfrage
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "Du bist ein hilfreicher Recherche-Assistent. Antworte präzise und gib immer Quellen an."
            },
            {
                "role": "user",
                "content": query
            }
        ]
    }
    
    # Füge Suchfilter hinzu
    if focus != "web":
        payload["search_domain_filter"] = [focus]
    
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            citations = result.get("citations", [])
            
            # Formatiere Zitate
            formatted_citations = []
            for i, citation in enumerate(citations, 1):
                if isinstance(citation, str):
                    formatted_citations.append({
                        "index": i,
                        "url": citation
                    })
                elif isinstance(citation, dict):
                    formatted_citations.append({
                        "index": i,
                        "url": citation.get("url", ""),
                        "title": citation.get("title", "")
                    })
            
            return {
                "answer": answer,
                "citations": formatted_citations
            }
        else:
            return {
                "answer": f"API-Fehler: {response.status_code} - {response.text}",
                "citations": []
            }
            
    except requests.exceptions.Timeout:
        return {
            "answer": "Fehler: Zeitüberschreitung bei der Anfrage",
            "citations": []
        }
    except Exception as e:
        return {
            "answer": f"Fehler: {str(e)}",
            "citations": []
        }


# Für direkten Aufruf
if __name__ == "__main__":
    import json
    
    result = execute("Was sind die neuesten Entwicklungen in der KI?", "news")
    print(json.dumps(result, indent=2, ensure_ascii=False))
