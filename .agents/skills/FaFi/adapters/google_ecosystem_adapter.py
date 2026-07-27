"""
Google Ecosystem Adapter
========================
Bidirektionaler Adapter für Google KI-Dienste:
- NotebookLM: Quellenbasierte Recherche und Zusammenfassung
- Gemini: Multimodale KI-Fähigkeiten
- Google AI Studio: Prompt-Engineering und Modell-Feinabstimmung
"""

import json
import os
from typing import Dict, List, Any, Optional
from adapters.base_adapter import BaseAdapter


class GoogleEcosystemAdapter(BaseAdapter):
    """
    Basis-Adapter für das Google KI-Ökosystem.
    Stellt gemeinsame Funktionalität für alle Google-Dienste bereit.
    """
    
    @property
    def platform_name(self) -> str:
        return "Google Ecosystem"
    
    def format_skill_definition(self, skill: Dict) -> str:
        """
        Formatiert einen Skill im Google Function Calling Format.
        Verwendet das Gemini-kompatible Format.
        """
        interface = skill.get('interface', {})
        
        # Baue Parameter-Schema für Gemini
        properties = {}
        required = []
        
        for inp in interface.get('inputs', []):
            properties[inp['name']] = {
                'type': self._map_type_google(inp['type']),
                'description': inp.get('description', '')
            }
            if inp.get('required', True):
                required.append(inp['name'])
        
        function_def = {
            'name': skill['name'],
            'description': skill.get('description', ''),
            'parameters': {
                'type': 'object',
                'properties': properties,
                'required': required
            }
        }
        
        return json.dumps(function_def, indent=2, ensure_ascii=False)
    
    def format_agent_definition(self, agent: Dict) -> str:
        """Formatiert einen Agent für Google-Dienste."""
        interface = agent.get('interface', {})
        
        properties = {}
        required = []
        
        for inp in interface.get('inputs', []):
            properties[inp['name']] = {
                'type': self._map_type_google(inp['type']),
                'description': inp.get('description', '')
            }
            if inp.get('required', True):
                required.append(inp['name'])
        
        function_def = {
            'name': f"agent_{agent['name']}",
            'description': f"[Orchestrierender Agent] {agent.get('description', '')}",
            'parameters': {
                'type': 'object',
                'properties': properties,
                'required': required
            }
        }
        
        return json.dumps(function_def, indent=2, ensure_ascii=False)
    
    def _build_catalog(self, skills: List[str], agents: List[str]) -> str:
        """Baut den Google-Ökosystem-Katalog."""
        tools = []
        
        for s in skills:
            func = json.loads(s)
            tools.append({'function_declarations': [func]})
        
        for a in agents:
            func = json.loads(a)
            tools.append({'function_declarations': [func]})
        
        return json.dumps({'tools': tools}, indent=2, ensure_ascii=False)
    
    def _map_type_google(self, hub_type: str) -> str:
        """Mappt Hub-Typen auf Google/Gemini-Typen."""
        type_mapping = {
            'string': 'STRING',
            'number': 'NUMBER',
            'boolean': 'BOOLEAN',
            'array': 'ARRAY',
            'object': 'OBJECT',
            'file': 'STRING'
        }
        return type_mapping.get(hub_type, 'STRING')


class NotebookLMAdapter(GoogleEcosystemAdapter):
    """
    Spezialisierter Adapter für NotebookLM.
    
    NotebookLM-spezifische Funktionen:
    - Quellenbasierte Recherche
    - Audio-Übersichten (Podcast-Generierung)
    - Quellenverknüpfte Zusammenfassungen
    """
    
    @property
    def platform_name(self) -> str:
        return "NotebookLM"
    
    def generate_notebooklm_skills(self) -> List[Dict]:
        """
        Generiert Skill-Manifeste für NotebookLM-Funktionen.
        Diese können als importierte Skills in den Hub aufgenommen werden.
        """
        notebooklm_skills = [
            {
                'name': 'notebooklm_query_sources',
                'description': 'Durchsucht hochgeladene Quellen in NotebookLM und gibt relevante Informationen zurück.',
                'tags': ['notebooklm', 'google', 'research', 'sources', 'rag'],
                'capabilities': ['source_search', 'rag', 'research'],
                'implementation': {
                    'type': 'remote',
                    'language': 'notebooklm_api',
                    'target': {
                        'action': 'query_sources',
                        'requires_notebook_id': True
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'notebook_id', 'type': 'string', 'description': 'ID des NotebookLM-Notebooks', 'required': True},
                        {'name': 'query', 'type': 'string', 'description': 'Suchanfrage an die Quellen', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'answer', 'type': 'string', 'description': 'Antwort basierend auf den Quellen'},
                        {'name': 'citations', 'type': 'array', 'description': 'Liste der verwendeten Quellenzitate'}
                    ]
                }
            },
            {
                'name': 'notebooklm_generate_summary',
                'description': 'Erstellt eine Zusammenfassung aller Quellen in einem NotebookLM-Notebook.',
                'tags': ['notebooklm', 'google', 'summary', 'synthesis'],
                'capabilities': ['summarization', 'synthesis'],
                'implementation': {
                    'type': 'remote',
                    'language': 'notebooklm_api',
                    'target': {
                        'action': 'generate_summary',
                        'requires_notebook_id': True
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'notebook_id', 'type': 'string', 'description': 'ID des NotebookLM-Notebooks', 'required': True},
                        {'name': 'focus', 'type': 'string', 'description': 'Optionaler Fokus für die Zusammenfassung', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'summary', 'type': 'string', 'description': 'Generierte Zusammenfassung'}
                    ]
                }
            },
            {
                'name': 'notebooklm_generate_audio_overview',
                'description': 'Generiert eine Audio-Übersicht (Podcast-Stil) aus den Quellen.',
                'tags': ['notebooklm', 'google', 'audio', 'podcast'],
                'capabilities': ['audio_generation', 'content_creation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'notebooklm_api',
                    'target': {
                        'action': 'generate_audio_overview',
                        'requires_notebook_id': True
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'notebook_id', 'type': 'string', 'description': 'ID des NotebookLM-Notebooks', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'audio_url', 'type': 'string', 'description': 'URL zur generierten Audio-Datei'},
                        {'name': 'transcript', 'type': 'string', 'description': 'Transkript der Audio-Übersicht'}
                    ]
                }
            }
        ]
        
        return notebooklm_skills


class GeminiAdapter(GoogleEcosystemAdapter):
    """
    Spezialisierter Adapter für Google Gemini.
    
    Gemini-spezifische Funktionen:
    - Multimodale Verarbeitung (Text, Bild, Video, Audio)
    - Lange Kontextfenster
    - Code-Ausführung
    """
    
    @property
    def platform_name(self) -> str:
        return "Gemini"
    
    def generate_gemini_skills(self) -> List[Dict]:
        """
        Generiert Skill-Manifeste für Gemini-Funktionen.
        """
        gemini_skills = [
            {
                'name': 'gemini_analyze_image',
                'description': 'Analysiert ein Bild mit Gemini Vision und beschreibt dessen Inhalt.',
                'tags': ['gemini', 'google', 'vision', 'image', 'multimodal'],
                'capabilities': ['image_analysis', 'vision', 'multimodal'],
                'implementation': {
                    'type': 'remote',
                    'language': 'gemini_api',
                    'target': {
                        'model': 'gemini-2.0-flash',
                        'capability': 'vision'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'image_url', 'type': 'string', 'description': 'URL oder Base64 des Bildes', 'required': True},
                        {'name': 'prompt', 'type': 'string', 'description': 'Spezifische Frage zum Bild', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'description', 'type': 'string', 'description': 'Beschreibung/Analyse des Bildes'}
                    ]
                }
            },
            {
                'name': 'gemini_analyze_video',
                'description': 'Analysiert ein Video mit Gemini und extrahiert Informationen.',
                'tags': ['gemini', 'google', 'video', 'multimodal'],
                'capabilities': ['video_analysis', 'multimodal'],
                'implementation': {
                    'type': 'remote',
                    'language': 'gemini_api',
                    'target': {
                        'model': 'gemini-2.0-flash',
                        'capability': 'video'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'video_url', 'type': 'string', 'description': 'URL des Videos', 'required': True},
                        {'name': 'prompt', 'type': 'string', 'description': 'Spezifische Frage zum Video', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'analysis', 'type': 'string', 'description': 'Analyse des Videos'},
                        {'name': 'timestamps', 'type': 'array', 'description': 'Relevante Zeitstempel'}
                    ]
                }
            },
            {
                'name': 'gemini_code_execution',
                'description': 'Führt Python-Code in der Gemini-Sandbox aus.',
                'tags': ['gemini', 'google', 'code', 'execution', 'python'],
                'capabilities': ['code_execution', 'computation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'gemini_api',
                    'target': {
                        'model': 'gemini-2.0-flash',
                        'capability': 'code_execution'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'code', 'type': 'string', 'description': 'Python-Code zur Ausführung', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'output', 'type': 'string', 'description': 'Ausgabe der Code-Ausführung'},
                        {'name': 'error', 'type': 'string', 'description': 'Fehlermeldung, falls vorhanden'}
                    ]
                }
            },
            {
                'name': 'gemini_long_context',
                'description': 'Verarbeitet sehr lange Dokumente (bis zu 2M Token) mit Gemini.',
                'tags': ['gemini', 'google', 'long_context', 'document'],
                'capabilities': ['long_context', 'document_processing'],
                'implementation': {
                    'type': 'remote',
                    'language': 'gemini_api',
                    'target': {
                        'model': 'gemini-2.0-pro',
                        'capability': 'long_context'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'document', 'type': 'string', 'description': 'Das zu verarbeitende Dokument', 'required': True},
                        {'name': 'task', 'type': 'string', 'description': 'Aufgabe (z.B. Zusammenfassung, Q&A)', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'result', 'type': 'string', 'description': 'Ergebnis der Verarbeitung'}
                    ]
                }
            }
        ]
        
        return gemini_skills
    
    def generate_gemini_tools_config(self) -> Dict:
        """
        Generiert eine Gemini Tools-Konfiguration für Function Calling.
        """
        skills = self.get_all_skills()
        
        function_declarations = []
        for skill in skills:
            func_def = json.loads(self.format_skill_definition(skill))
            function_declarations.append(func_def)
        
        return {
            'tools': [{
                'function_declarations': function_declarations
            }],
            'tool_config': {
                'function_calling_config': {
                    'mode': 'AUTO'
                }
            }
        }


class GoogleAIStudioAdapter(GoogleEcosystemAdapter):
    """
    Spezialisierter Adapter für Google AI Studio.
    
    AI Studio-spezifische Funktionen:
    - Prompt-Bibliothek
    - Modell-Tuning
    - Batch-Verarbeitung
    """
    
    @property
    def platform_name(self) -> str:
        return "Google AI Studio"
    
    def generate_aistudio_skills(self) -> List[Dict]:
        """
        Generiert Skill-Manifeste für Google AI Studio-Funktionen.
        """
        aistudio_skills = [
            {
                'name': 'aistudio_run_prompt',
                'description': 'Führt einen gespeicherten Prompt aus der AI Studio Bibliothek aus.',
                'tags': ['aistudio', 'google', 'prompt', 'template'],
                'capabilities': ['prompt_execution', 'templating'],
                'implementation': {
                    'type': 'remote',
                    'language': 'aistudio_api',
                    'target': {
                        'action': 'run_prompt'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'prompt_id', 'type': 'string', 'description': 'ID des gespeicherten Prompts', 'required': True},
                        {'name': 'variables', 'type': 'object', 'description': 'Variablen für den Prompt', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'response', 'type': 'string', 'description': 'Antwort des Modells'}
                    ]
                }
            },
            {
                'name': 'aistudio_batch_process',
                'description': 'Verarbeitet mehrere Eingaben im Batch-Modus.',
                'tags': ['aistudio', 'google', 'batch', 'bulk'],
                'capabilities': ['batch_processing', 'bulk_operations'],
                'implementation': {
                    'type': 'remote',
                    'language': 'aistudio_api',
                    'target': {
                        'action': 'batch_process'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'inputs', 'type': 'array', 'description': 'Liste der zu verarbeitenden Eingaben', 'required': True},
                        {'name': 'prompt_template', 'type': 'string', 'description': 'Prompt-Template mit {input} Platzhalter', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'results', 'type': 'array', 'description': 'Liste der Ergebnisse'}
                    ]
                }
            }
        ]
        
        return aistudio_skills
    
    def generate_prompt_library_entry(self, skill: Dict) -> Dict:
        """
        Generiert einen Eintrag für die AI Studio Prompt-Bibliothek.
        """
        interface = skill.get('interface', {})
        
        # Baue Prompt-Template
        input_vars = [inp['name'] for inp in interface.get('inputs', [])]
        var_placeholders = ', '.join([f'{{{v}}}' for v in input_vars])
        
        return {
            'name': f"Hub: {skill['name']}",
            'description': skill.get('description', ''),
            'prompt_template': f"Führe die folgende Aufgabe aus: {skill.get('description', '')}\n\nEingaben: {var_placeholders}\n\nAusgabe:",
            'variables': input_vars,
            'model_settings': {
                'model': 'gemini-2.0-flash',
                'temperature': 0.7,
                'max_output_tokens': 2048
            },
            'tags': skill.get('tags', [])
        }
