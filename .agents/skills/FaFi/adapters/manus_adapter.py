"""
Manus Adapter (Bidirektional)
=============================
Bidirektionaler Adapter für Manus 1.6 und höher.
- Export: Stellt Hub-Skills für Manus-Workflows bereit
- Import: Integriert Manus-spezifische Fähigkeiten als Hub-Skills
"""

import json
from typing import Dict, List, Any
from adapters.base_adapter import BaseAdapter


class ManusAdapter(BaseAdapter):
    """
    Bidirektionaler Adapter für Manus.
    
    Unterstützt:
    - Export von Hub-Skills im Manus Function-Calling-Format
    - Export von Hub-Agents als orchestrierende Funktionen
    - Import von Manus-Sandbox-Operationen als Hub-Skills
    - Import von Manus-Tools (Browser, Shell, File, etc.) als Hub-Skills
    """
    
    @property
    def platform_name(self) -> str:
        return "Manus"
    
    def format_skill_definition(self, skill: Dict) -> str:
        """
        Formatiert einen Skill für Manus.
        Manus verwendet ein Function-Calling-Format ähnlich OpenAI.
        """
        interface = skill.get('interface', {})
        
        # Baue Parameter-Schema
        properties = {}
        required = []
        
        for inp in interface.get('inputs', []):
            prop = {
                'type': self._map_type(inp['type']),
                'description': inp.get('description', '')
            }
            if 'default' in inp:
                prop['default'] = inp['default']
            if 'enum' in inp:
                prop['enum'] = inp['enum']
            
            properties[inp['name']] = prop
            
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
        """
        Formatiert einen Agent für Manus.
        """
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
        
        # Agent mit Orchestrierungs-Metadaten
        function_def = {
            'name': agent['name'],
            'description': f"[Orchestrierender Agent] {agent.get('description', '')}",
            'parameters': {
                'type': 'object',
                'properties': properties,
                'required': required
            },
            'metadata': {
                'type': 'agent',
                'capabilities': agent.get('capabilities', []),
                'dependencies': agent.get('dependencies', [])
            }
        }
        
        return json.dumps(function_def, indent=2, ensure_ascii=False)
    
    def _build_catalog(self, skills: List[str], agents: List[str]) -> str:
        """Baut den Manus-spezifischen Katalog."""
        all_functions = []
        
        for s in skills:
            func = json.loads(s)
            func['_type'] = 'skill'
            all_functions.append(func)
        
        for a in agents:
            func = json.loads(a)
            func['_type'] = 'agent'
            all_functions.append(func)
        
        catalog = {
            'version': '2.0',
            'platform': 'manus',
            'functions': all_functions,
            'bidirectional': True
        }
        
        return json.dumps(catalog, indent=2, ensure_ascii=False)
    
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
    
    # ============== Bidirektionale Import-Funktionen ==============
    
    def generate_manus_skills(self) -> List[Dict]:
        """
        Generiert Skill-Manifeste für Manus-spezifische Funktionen.
        Diese Skills ermöglichen den Zugriff auf Manus-Features vom Hub aus.
        """
        manus_skills = [
            # Shell-Operationen
            {
                'name': 'manus_shell_execute',
                'description': 'Führt Shell-Befehle in der Manus-Sandbox aus.',
                'tags': ['manus', 'shell', 'command', 'sandbox', 'imported'],
                'capabilities': ['shell_execution', 'command_line'],
                'implementation': {
                    'type': 'remote',
                    'language': 'manus_api',
                    'target': {
                        'service': 'manus',
                        'tool': 'shell'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'command', 'type': 'string', 'description': 'Shell-Befehl', 'required': True},
                        {'name': 'session', 'type': 'string', 'description': 'Session-ID', 'required': False, 'default': 'default'},
                        {'name': 'timeout', 'type': 'number', 'description': 'Timeout in Sekunden', 'required': False, 'default': 30}
                    ],
                    'outputs': [
                        {'name': 'output', 'type': 'string', 'description': 'Befehlsausgabe'},
                        {'name': 'exit_code', 'type': 'number', 'description': 'Exit-Code'}
                    ]
                }
            },
            # Datei-Operationen
            {
                'name': 'manus_file_read',
                'description': 'Liest eine Datei aus der Manus-Sandbox.',
                'tags': ['manus', 'file', 'read', 'sandbox', 'imported'],
                'capabilities': ['file_operations'],
                'implementation': {
                    'type': 'remote',
                    'language': 'manus_api',
                    'target': {
                        'service': 'manus',
                        'tool': 'file'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'path', 'type': 'string', 'description': 'Dateipfad', 'required': True},
                        {'name': 'range', 'type': 'array', 'description': 'Zeilenbereich [start, end]', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'content', 'type': 'string', 'description': 'Dateiinhalt'},
                        {'name': 'lines', 'type': 'number', 'description': 'Anzahl der Zeilen'}
                    ]
                }
            },
            {
                'name': 'manus_file_write',
                'description': 'Schreibt eine Datei in die Manus-Sandbox.',
                'tags': ['manus', 'file', 'write', 'sandbox', 'imported'],
                'capabilities': ['file_operations'],
                'implementation': {
                    'type': 'remote',
                    'language': 'manus_api',
                    'target': {
                        'service': 'manus',
                        'tool': 'file'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'path', 'type': 'string', 'description': 'Dateipfad', 'required': True},
                        {'name': 'content', 'type': 'string', 'description': 'Dateiinhalt', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'status', 'type': 'string', 'description': 'Schreibstatus'},
                        {'name': 'bytes_written', 'type': 'number', 'description': 'Geschriebene Bytes'}
                    ]
                }
            },
            # Browser-Operationen
            {
                'name': 'manus_browser_navigate',
                'description': 'Navigiert zu einer URL im Manus-Browser.',
                'tags': ['manus', 'browser', 'web', 'navigate', 'imported'],
                'capabilities': ['web_browsing'],
                'implementation': {
                    'type': 'remote',
                    'language': 'manus_api',
                    'target': {
                        'service': 'manus',
                        'tool': 'browser'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'url', 'type': 'string', 'description': 'Ziel-URL', 'required': True},
                        {'name': 'intent', 'type': 'string', 'description': 'Absicht (navigational, informational, transactional)', 'required': False, 'default': 'navigational'},
                        {'name': 'focus', 'type': 'string', 'description': 'Fokusbereich für informational', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'title', 'type': 'string', 'description': 'Seitentitel'},
                        {'name': 'content', 'type': 'string', 'description': 'Seiteninhalt (Zusammenfassung)'}
                    ]
                }
            },
            # Suche
            {
                'name': 'manus_search',
                'description': 'Führt eine Websuche über Manus durch.',
                'tags': ['manus', 'search', 'web', 'information', 'imported'],
                'capabilities': ['web_search', 'information_retrieval'],
                'implementation': {
                    'type': 'remote',
                    'language': 'manus_api',
                    'target': {
                        'service': 'manus',
                        'tool': 'search'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'queries', 'type': 'array', 'description': 'Suchanfragen (bis zu 3)', 'required': True},
                        {'name': 'type', 'type': 'string', 'description': 'Suchtyp (info, image, api, news, tool, data, research)', 'required': False, 'default': 'info'}
                    ],
                    'outputs': [
                        {'name': 'results', 'type': 'array', 'description': 'Suchergebnisse'},
                        {'name': 'sources', 'type': 'array', 'description': 'Quellen-URLs'}
                    ]
                }
            },
            # Parallele Verarbeitung
            {
                'name': 'manus_parallel_map',
                'description': 'Führt parallele Subtasks in Manus aus.',
                'tags': ['manus', 'parallel', 'map', 'batch', 'imported'],
                'capabilities': ['parallel_processing', 'batch_operations'],
                'implementation': {
                    'type': 'remote',
                    'language': 'manus_api',
                    'target': {
                        'service': 'manus',
                        'tool': 'map'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'prompt_template', 'type': 'string', 'description': 'Prompt-Template mit {{input}}', 'required': True},
                        {'name': 'inputs', 'type': 'array', 'description': 'Liste der Eingaben', 'required': True},
                        {'name': 'output_schema', 'type': 'array', 'description': 'Schema für Ausgaben', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'results', 'type': 'array', 'description': 'Ergebnisse aller Subtasks'},
                        {'name': 'success_count', 'type': 'number', 'description': 'Anzahl erfolgreicher Tasks'}
                    ]
                }
            },
            # Medien-Generierung
            {
                'name': 'manus_generate_media',
                'description': 'Generiert Medien (Bilder, Audio) über Manus.',
                'tags': ['manus', 'generate', 'media', 'image', 'audio', 'imported'],
                'capabilities': ['media_generation', 'image_generation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'manus_api',
                    'target': {
                        'service': 'manus',
                        'tool': 'generate'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'type', 'type': 'string', 'description': 'Medientyp (image, audio, speech)', 'required': True},
                        {'name': 'prompt', 'type': 'string', 'description': 'Generierungs-Prompt', 'required': True},
                        {'name': 'options', 'type': 'object', 'description': 'Zusätzliche Optionen', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'file_path', 'type': 'string', 'description': 'Pfad zur generierten Datei'},
                        {'name': 'url', 'type': 'string', 'description': 'URL der Datei'}
                    ]
                }
            },
            # Präsentationen
            {
                'name': 'manus_create_slides',
                'description': 'Erstellt Präsentationen über Manus.',
                'tags': ['manus', 'slides', 'presentation', 'pptx', 'imported'],
                'capabilities': ['presentation_creation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'manus_api',
                    'target': {
                        'service': 'manus',
                        'tool': 'slides'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'content_file', 'type': 'string', 'description': 'Pfad zur Inhaltsdatei (Markdown)', 'required': True},
                        {'name': 'slide_count', 'type': 'number', 'description': 'Anzahl der Folien', 'required': True},
                        {'name': 'generate_mode', 'type': 'string', 'description': 'Modus (html, image)', 'required': False, 'default': 'html'}
                    ],
                    'outputs': [
                        {'name': 'slides_uri', 'type': 'string', 'description': 'URI der Präsentation'},
                        {'name': 'export_path', 'type': 'string', 'description': 'Exportpfad'}
                    ]
                }
            },
            # Web-Entwicklung
            {
                'name': 'manus_webdev_init',
                'description': 'Initialisiert ein Web-Entwicklungsprojekt in Manus.',
                'tags': ['manus', 'webdev', 'project', 'init', 'imported'],
                'capabilities': ['web_development', 'project_scaffolding'],
                'implementation': {
                    'type': 'remote',
                    'language': 'manus_api',
                    'target': {
                        'service': 'manus',
                        'tool': 'webdev_init_project'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'name', 'type': 'string', 'description': 'Projektname', 'required': True},
                        {'name': 'title', 'type': 'string', 'description': 'Projekttitel', 'required': True},
                        {'name': 'description', 'type': 'string', 'description': 'Projektbeschreibung', 'required': True},
                        {'name': 'scaffold', 'type': 'string', 'description': 'Scaffold-Typ (web-static, web-db-user, mobile-app)', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'project_path', 'type': 'string', 'description': 'Projektpfad'},
                        {'name': 'status', 'type': 'string', 'description': 'Initialisierungsstatus'}
                    ]
                }
            },
            # Zeitplanung
            {
                'name': 'manus_schedule_task',
                'description': 'Plant eine zeitgesteuerte Aufgabe in Manus.',
                'tags': ['manus', 'schedule', 'cron', 'automation', 'imported'],
                'capabilities': ['task_scheduling', 'automation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'manus_api',
                    'target': {
                        'service': 'manus',
                        'tool': 'schedule'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'name', 'type': 'string', 'description': 'Aufgabenname', 'required': True},
                        {'name': 'prompt', 'type': 'string', 'description': 'Aufgabenbeschreibung', 'required': True},
                        {'name': 'type', 'type': 'string', 'description': 'Typ (cron, interval)', 'required': True},
                        {'name': 'cron', 'type': 'string', 'description': 'Cron-Ausdruck (für cron-Typ)', 'required': False},
                        {'name': 'interval', 'type': 'number', 'description': 'Intervall in Sekunden (für interval-Typ)', 'required': False},
                        {'name': 'repeat', 'type': 'boolean', 'description': 'Wiederholen', 'required': False, 'default': True}
                    ],
                    'outputs': [
                        {'name': 'schedule_id', 'type': 'string', 'description': 'Zeitplan-ID'},
                        {'name': 'next_run', 'type': 'string', 'description': 'Nächste Ausführung'}
                    ]
                }
            },
            # MCP-Integration
            {
                'name': 'manus_mcp_call',
                'description': 'Ruft ein MCP-Tool über Manus auf.',
                'tags': ['manus', 'mcp', 'tool', 'integration', 'imported'],
                'capabilities': ['mcp_integration', 'external_tools'],
                'implementation': {
                    'type': 'remote',
                    'language': 'manus_api',
                    'target': {
                        'service': 'manus',
                        'tool': 'mcp'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'server', 'type': 'string', 'description': 'MCP-Server-Name', 'required': True},
                        {'name': 'tool', 'type': 'string', 'description': 'Tool-Name', 'required': True},
                        {'name': 'input', 'type': 'object', 'description': 'Tool-Eingaben', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'result', 'type': 'object', 'description': 'Tool-Ergebnis'},
                        {'name': 'status', 'type': 'string', 'description': 'Ausführungsstatus'}
                    ]
                }
            }
        ]
        
        return manus_skills
    
    def generate_manus_instructions(self) -> str:
        """
        Generiert Anweisungen für die Integration in Manus.
        """
        skills = self.get_all_skills()
        agents = self.get_all_agents()
        
        instructions = """
# Skill-Hub Integration für Manus (Bidirektional)

## Verfügbare Skills

Die folgenden Skills können direkt aufgerufen werden:

"""
        for skill in skills:
            instructions += f"### {skill['name']}\n"
            instructions += f"{skill.get('description', 'Keine Beschreibung')}\n\n"
            
            interface = skill.get('interface', {})
            if interface.get('inputs'):
                instructions += "**Inputs:**\n"
                for inp in interface['inputs']:
                    req = "(erforderlich)" if inp.get('required', True) else "(optional)"
                    instructions += f"- `{inp['name']}` ({inp['type']}): {inp.get('description', '')} {req}\n"
            
            if interface.get('outputs'):
                instructions += "\n**Outputs:**\n"
                for out in interface['outputs']:
                    instructions += f"- `{out['name']}` ({out['type']}): {out.get('description', '')}\n"
            
            instructions += "\n---\n\n"
        
        instructions += """
## Verfügbare Agents

Die folgenden Agents orchestrieren mehrere Skills:

"""
        for agent in agents:
            instructions += f"### {agent['name']}\n"
            instructions += f"{agent.get('description', 'Keine Beschreibung')}\n\n"
            instructions += "---\n\n"
        
        instructions += """
## Bidirektionale Integration

Der Hub kann auch Manus-Funktionen nutzen:

```python
# Shell-Befehl ausführen
result = hub.execute_skill('manus_shell_execute', {
    'command': 'ls -la',
    'session': 'default'
})

# Datei lesen
result = hub.execute_skill('manus_file_read', {
    'path': '/home/ubuntu/data.txt'
})

# Websuche
result = hub.execute_skill('manus_search', {
    'queries': ['AI Trends 2026'],
    'type': 'info'
})
```

## Verwendung

Um einen Skill oder Agent zu nutzen:

1. **Direkter Aufruf**: Rufe die entsprechende Funktion mit den benötigten Parametern auf
2. **Discovery**: Beschreibe die Aufgabe, und das System findet passende Skills
3. **Orchestrierung**: Nutze einen Agent für komplexe, mehrstufige Aufgaben

## Erweiterung

Neue Skills können durch Hinzufügen einer `manifest.json` im `skills/`-Verzeichnis registriert werden.
"""
        
        return instructions
    
    def generate_scheduled_task_template(self, skill_name: str) -> Dict:
        """
        Generiert eine Vorlage für geplante Aufgaben in Manus.
        """
        skill = self.registry.get_by_name(skill_name) if hasattr(self, 'registry') else None
        if not skill:
            return {}
        
        return {
            'name': f"Scheduled: {skill_name}",
            'type': 'interval',
            'interval': 3600,  # Stündlich als Standard
            'repeat': True,
            'prompt': f"Führe den Skill '{skill_name}' aus dem Skill-Hub aus.",
            'playbook': f"1. Lade Skill-Definition für {skill_name}\n2. Bereite Inputs vor\n3. Führe Skill aus\n4. Verarbeite Outputs"
        }
