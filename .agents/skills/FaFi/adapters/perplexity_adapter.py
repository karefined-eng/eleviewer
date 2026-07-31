"""
Perplexity Adapter
==================
Bidirektionaler Adapter für Perplexity AI.
- Export: Stellt Hub-Skills für Perplexity-Workflows bereit
- Import: Integriert Perplexity's Echtzeit-Websuche als Hub-Skill
"""

import json
import os
from typing import Dict, List, Any, Optional
from adapters.base_adapter import BaseAdapter


class PerplexityAdapter(BaseAdapter):
    """
    Bidirektionaler Adapter für Perplexity AI.
    
    Perplexity-spezifische Funktionen:
    - Echtzeit-Websuche mit Quellenangaben
    - Fokussierte Recherche (Academic, News, etc.)
    - Konversationsbasierte Suche
    """
    
    @property
    def platform_name(self) -> str:
        return "Perplexity"
    
    def format_skill_definition(self, skill: Dict) -> str:
        """
        Formatiert einen Skill für die Perplexity API.
        Perplexity verwendet ein ähnliches Format wie OpenAI.
        """
        interface = skill.get('interface', {})
        
        properties = {}
        required = []
        
        for inp in interface.get('inputs', []):
            properties[inp['name']] = {
                'type': self._map_type(inp['type']),
                'description': inp.get('description', '')
            }
            if inp.get('required', True):
                required.append(inp['name'])
        
        function_def = {
            'type': 'function',
            'function': {
                'name': skill['name'],
                'description': skill.get('description', ''),
                'parameters': {
                    'type': 'object',
                    'properties': properties,
                    'required': required
                }
            }
        }
        
        return json.dumps(function_def, indent=2, ensure_ascii=False)
    
    def format_agent_definition(self, agent: Dict) -> str:
        """Formatiert einen Agent für Perplexity."""
        interface = agent.get('interface', {})
        
        properties = {}
        required = []
        
        for inp in interface.get('inputs', []):
            properties[inp['name']] = {
                'type': self._map_type(inp['type']),
                'description': inp.get('description', '')
            }
            if inp.get('required', True):
                required.append(inp['name'])
        
        function_def = {
            'type': 'function',
            'function': {
                'name': f"agent_{agent['name']}",
                'description': f"[Multi-Step Agent] {agent.get('description', '')}",
                'parameters': {
                    'type': 'object',
                    'properties': properties,
                    'required': required
                }
            }
        }
        
        return json.dumps(function_def, indent=2, ensure_ascii=False)
    
    def _build_catalog(self, skills: List[str], agents: List[str]) -> str:
        """Baut den Perplexity-Katalog."""
        tools = [json.loads(s) for s in skills]
        tools.extend([json.loads(a) for a in agents])
        
        return json.dumps({'tools': tools}, indent=2, ensure_ascii=False)
    
    def _map_type(self, hub_type: str) -> str:
        """Mappt Hub-Typen auf JSON-Schema-Typen."""
        type_mapping = {
            'string': 'string',
            'number': 'number',
            'boolean': 'boolean',
            'array': 'array',
            'object': 'object',
            'file': 'string'
        }
        return type_mapping.get(hub_type, 'string')
    
    def generate_perplexity_skills(self) -> List[Dict]:
        """
        Generiert Skill-Manifeste für Perplexity-Funktionen.
        Diese können als importierte Skills in den Hub aufgenommen werden.
        """
        perplexity_skills = [
            {
                'name': 'perplexity_web_search',
                'description': 'Führt eine Echtzeit-Websuche mit Perplexity durch und gibt Ergebnisse mit Quellenangaben zurück.',
                'tags': ['perplexity', 'search', 'web', 'realtime', 'sources'],
                'capabilities': ['web_search', 'realtime_information', 'citation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'perplexity_api',
                    'target': {
                        'model': 'sonar',
                        'endpoint': '/chat/completions',
                        'search_mode': 'auto'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'query', 'type': 'string', 'description': 'Suchanfrage', 'required': True},
                        {'name': 'focus', 'type': 'string', 'description': 'Suchfokus (web, academic, news, youtube, reddit)', 'required': False, 'default': 'web'}
                    ],
                    'outputs': [
                        {'name': 'answer', 'type': 'string', 'description': 'Zusammengefasste Antwort'},
                        {'name': 'citations', 'type': 'array', 'description': 'Liste der Quellen mit URLs'}
                    ]
                }
            },
            {
                'name': 'perplexity_academic_search',
                'description': 'Durchsucht akademische Quellen und Forschungspapiere.',
                'tags': ['perplexity', 'academic', 'research', 'papers'],
                'capabilities': ['academic_search', 'research', 'citation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'perplexity_api',
                    'target': {
                        'model': 'sonar',
                        'endpoint': '/chat/completions',
                        'search_mode': 'academic'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'query', 'type': 'string', 'description': 'Forschungsfrage oder Thema', 'required': True},
                        {'name': 'recency', 'type': 'string', 'description': 'Zeitraum (day, week, month, year)', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'summary', 'type': 'string', 'description': 'Zusammenfassung der Forschungsergebnisse'},
                        {'name': 'papers', 'type': 'array', 'description': 'Liste relevanter Forschungspapiere'}
                    ]
                }
            },
            {
                'name': 'perplexity_news_search',
                'description': 'Sucht nach aktuellen Nachrichten zu einem Thema.',
                'tags': ['perplexity', 'news', 'current_events', 'realtime'],
                'capabilities': ['news_search', 'current_events'],
                'implementation': {
                    'type': 'remote',
                    'language': 'perplexity_api',
                    'target': {
                        'model': 'sonar',
                        'endpoint': '/chat/completions',
                        'search_mode': 'news'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'topic', 'type': 'string', 'description': 'Nachrichtenthema', 'required': True},
                        {'name': 'recency', 'type': 'string', 'description': 'Zeitraum (day, week)', 'required': False, 'default': 'day'}
                    ],
                    'outputs': [
                        {'name': 'summary', 'type': 'string', 'description': 'Zusammenfassung der Nachrichten'},
                        {'name': 'articles', 'type': 'array', 'description': 'Liste der Nachrichtenartikel'}
                    ]
                }
            },
            {
                'name': 'perplexity_deep_research',
                'description': 'Führt eine tiefgehende Recherche mit mehreren Iterationen durch.',
                'tags': ['perplexity', 'research', 'deep', 'comprehensive'],
                'capabilities': ['deep_research', 'comprehensive_analysis'],
                'implementation': {
                    'type': 'remote',
                    'language': 'perplexity_api',
                    'target': {
                        'model': 'sonar-deep-research',
                        'endpoint': '/chat/completions'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'topic', 'type': 'string', 'description': 'Forschungsthema', 'required': True},
                        {'name': 'depth', 'type': 'string', 'description': 'Recherchetiefe (standard, deep)', 'required': False, 'default': 'deep'}
                    ],
                    'outputs': [
                        {'name': 'report', 'type': 'string', 'description': 'Umfassender Recherchebericht'},
                        {'name': 'sources', 'type': 'array', 'description': 'Alle verwendeten Quellen'},
                        {'name': 'key_findings', 'type': 'array', 'description': 'Wichtigste Erkenntnisse'}
                    ]
                }
            }
        ]
        
        return perplexity_skills
    
    def generate_api_client_code(self) -> str:
        """
        Generiert Python-Code für die Perplexity API-Integration.
        """
        return '''
import os
import requests

class PerplexityClient:
    """Client für die Perplexity API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai"
    
    def search(self, query: str, focus: str = "web", recency: str = None) -> dict:
        """
        Führt eine Suche mit Perplexity durch.
        
        Args:
            query: Suchanfrage
            focus: Suchfokus (web, academic, news, youtube, reddit)
            recency: Zeitfilter (day, week, month, year)
        
        Returns:
            Dictionary mit answer und citations
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar",
            "messages": [{"role": "user", "content": query}],
            "search_domain_filter": [focus] if focus != "web" else None,
            "search_recency_filter": recency
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        )
        
        result = response.json()
        
        return {
            "answer": result["choices"][0]["message"]["content"],
            "citations": result.get("citations", [])
        }
'''
