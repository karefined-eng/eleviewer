"""
Claude Adapter (Bidirektional)
==============================
Bidirektionaler Adapter für Claude-basierte Plattformen (Claude Cowork, Claude Code).
- Export: Stellt Hub-Skills als Tool-Definitionen im Anthropic-Format bereit
- Import: Integriert Claude/Anthropic-spezifische Fähigkeiten als Hub-Skills
"""

import json
from typing import Dict, List, Any
from adapters.base_adapter import BaseAdapter


class ClaudeAdapter(BaseAdapter):
    """
    Bidirektionaler Adapter für Claude (Cowork und Code).
    
    Unterstützt:
    - Export von Hub-Skills als Claude Tool-Definitionen
    - Export von Hub-Agents als Claude Tools
    - Import von Claude/Anthropic-API-Funktionen als Hub-Skills
    - MCP-Server-Integration
    """
    
    @property
    def platform_name(self) -> str:
        return "Claude"
    
    def format_skill_definition(self, skill: Dict) -> str:
        """
        Formatiert einen Skill als Claude Tool-Definition.
        
        Claude verwendet ein JSON-Schema-basiertes Format für Tools.
        """
        interface = skill.get('interface', {})
        
        # Baue Input-Schema
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
        
        tool_definition = {
            'name': f"skill_{skill['name']}",
            'description': skill.get('description', ''),
            'input_schema': {
                'type': 'object',
                'properties': properties,
                'required': required
            }
        }
        
        return json.dumps(tool_definition, indent=2, ensure_ascii=False)
    
    def format_agent_definition(self, agent: Dict) -> str:
        """
        Formatiert einen Agent als Claude Tool-Definition.
        Agents werden als komplexere Tools mit Orchestrierungsfähigkeit dargestellt.
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
        
        # Füge spezielle Agent-Eigenschaften hinzu
        tool_definition = {
            'name': f"agent_{agent['name']}",
            'description': f"[AGENT] {agent.get('description', '')} - Orchestriert mehrere Skills zur Aufgabenerfüllung.",
            'input_schema': {
                'type': 'object',
                'properties': properties,
                'required': required
            }
        }
        
        return json.dumps(tool_definition, indent=2, ensure_ascii=False)
    
    def _build_catalog(self, skills: List[str], agents: List[str]) -> str:
        """Baut den Claude-spezifischen Katalog."""
        all_tools = skills + agents
        
        catalog = {
            'tools': [json.loads(t) for t in all_tools]
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
            'file': 'string'  # Dateipfade als Strings
        }
        return type_mapping.get(hub_type, 'string')
    
    # ============== Bidirektionale Import-Funktionen ==============
    
    def generate_claude_skills(self) -> List[Dict]:
        """
        Generiert Skill-Manifeste für Claude/Anthropic-spezifische Funktionen.
        Diese Skills ermöglichen den Zugriff auf Claude-Features vom Hub aus.
        """
        claude_skills = [
            # Chat Completion
            {
                'name': 'claude_chat_completion',
                'description': 'Führt eine Chat-Completion mit Claude durch.',
                'tags': ['claude', 'anthropic', 'chat', 'llm', 'imported'],
                'capabilities': ['chat', 'text_generation', 'reasoning'],
                'implementation': {
                    'type': 'remote',
                    'language': 'anthropic_api',
                    'target': {
                        'service': 'anthropic',
                        'endpoint': '/messages'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'messages', 'type': 'array', 'description': 'Chat-Nachrichten', 'required': True},
                        {'name': 'model', 'type': 'string', 'description': 'Modell (claude-3-opus, claude-3-sonnet, claude-3-haiku)', 'required': False, 'default': 'claude-3-sonnet-20240229'},
                        {'name': 'max_tokens', 'type': 'number', 'description': 'Maximale Token-Anzahl', 'required': False, 'default': 4096},
                        {'name': 'temperature', 'type': 'number', 'description': 'Temperatur (0-1)', 'required': False, 'default': 0.7},
                        {'name': 'system', 'type': 'string', 'description': 'System-Prompt', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'response', 'type': 'string', 'description': 'Claude-Antwort'},
                        {'name': 'usage', 'type': 'object', 'description': 'Token-Nutzung'},
                        {'name': 'stop_reason', 'type': 'string', 'description': 'Grund für das Stoppen'}
                    ]
                }
            },
            # Vision/Multimodal
            {
                'name': 'claude_vision_analysis',
                'description': 'Analysiert Bilder mit Claude Vision.',
                'tags': ['claude', 'anthropic', 'vision', 'image', 'multimodal', 'imported'],
                'capabilities': ['image_analysis', 'vision', 'multimodal'],
                'implementation': {
                    'type': 'remote',
                    'language': 'anthropic_api',
                    'target': {
                        'service': 'anthropic',
                        'endpoint': '/messages'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'image', 'type': 'string', 'description': 'Bild als Base64 oder URL', 'required': True},
                        {'name': 'prompt', 'type': 'string', 'description': 'Frage oder Anweisung zum Bild', 'required': True},
                        {'name': 'model', 'type': 'string', 'description': 'Modell', 'required': False, 'default': 'claude-3-sonnet-20240229'}
                    ],
                    'outputs': [
                        {'name': 'analysis', 'type': 'string', 'description': 'Bildanalyse'},
                        {'name': 'details', 'type': 'object', 'description': 'Zusätzliche Details'}
                    ]
                }
            },
            # Tool Use
            {
                'name': 'claude_tool_use',
                'description': 'Nutzt Claude mit Tool-Calling für strukturierte Aufgaben.',
                'tags': ['claude', 'anthropic', 'tools', 'function_calling', 'imported'],
                'capabilities': ['tool_use', 'function_calling', 'structured_output'],
                'implementation': {
                    'type': 'remote',
                    'language': 'anthropic_api',
                    'target': {
                        'service': 'anthropic',
                        'endpoint': '/messages'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'messages', 'type': 'array', 'description': 'Chat-Nachrichten', 'required': True},
                        {'name': 'tools', 'type': 'array', 'description': 'Tool-Definitionen', 'required': True},
                        {'name': 'model', 'type': 'string', 'description': 'Modell', 'required': False, 'default': 'claude-3-sonnet-20240229'}
                    ],
                    'outputs': [
                        {'name': 'response', 'type': 'string', 'description': 'Textantwort'},
                        {'name': 'tool_calls', 'type': 'array', 'description': 'Tool-Aufrufe'},
                        {'name': 'stop_reason', 'type': 'string', 'description': 'Grund für das Stoppen'}
                    ]
                }
            },
            # Extended Thinking
            {
                'name': 'claude_extended_thinking',
                'description': 'Nutzt Claude mit erweitertem Denken für komplexe Probleme.',
                'tags': ['claude', 'anthropic', 'reasoning', 'thinking', 'imported'],
                'capabilities': ['extended_thinking', 'complex_reasoning', 'problem_solving'],
                'implementation': {
                    'type': 'remote',
                    'language': 'anthropic_api',
                    'target': {
                        'service': 'anthropic',
                        'endpoint': '/messages'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'problem', 'type': 'string', 'description': 'Komplexes Problem oder Frage', 'required': True},
                        {'name': 'thinking_budget', 'type': 'number', 'description': 'Token-Budget für Denken', 'required': False, 'default': 10000},
                        {'name': 'model', 'type': 'string', 'description': 'Modell', 'required': False, 'default': 'claude-3-opus-20240229'}
                    ],
                    'outputs': [
                        {'name': 'thinking', 'type': 'string', 'description': 'Denkprozess'},
                        {'name': 'answer', 'type': 'string', 'description': 'Finale Antwort'},
                        {'name': 'confidence', 'type': 'number', 'description': 'Konfidenz (0-1)'}
                    ]
                }
            },
            # Batch Processing
            {
                'name': 'claude_batch_process',
                'description': 'Verarbeitet mehrere Anfragen im Batch-Modus.',
                'tags': ['claude', 'anthropic', 'batch', 'bulk', 'imported'],
                'capabilities': ['batch_processing', 'bulk_operations'],
                'implementation': {
                    'type': 'remote',
                    'language': 'anthropic_api',
                    'target': {
                        'service': 'anthropic',
                        'endpoint': '/batches'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'requests', 'type': 'array', 'description': 'Liste von Anfragen', 'required': True},
                        {'name': 'model', 'type': 'string', 'description': 'Modell', 'required': False, 'default': 'claude-3-haiku-20240307'}
                    ],
                    'outputs': [
                        {'name': 'batch_id', 'type': 'string', 'description': 'Batch-ID'},
                        {'name': 'results', 'type': 'array', 'description': 'Ergebnisse'},
                        {'name': 'status', 'type': 'string', 'description': 'Batch-Status'}
                    ]
                }
            }
        ]
        
        return claude_skills
    
    def generate_mcp_server_config(self) -> Dict:
        """
        Generiert eine MCP-Server-Konfiguration für Claude.
        Ermöglicht die Integration als Model Context Protocol Server.
        """
        return {
            'name': 'skill-agent-hub',
            'version': '2.0.0',
            'description': 'Zentraler Skill und Agent Hub für Multi-Plattform-Orchestrierung (Bidirektional)',
            'tools': self._get_mcp_tools(),
            'resources': self._get_mcp_resources()
        }
    
    def _get_mcp_tools(self) -> List[Dict]:
        """Generiert MCP-Tool-Definitionen."""
        tools = []
        
        # Discovery-Tool
        tools.append({
            'name': 'hub_discover',
            'description': 'Sucht nach passenden Skills und Agents basierend auf einer Aufgabenbeschreibung',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'Natürlichsprachliche Beschreibung der gesuchten Fähigkeit'
                    },
                    'type': {
                        'type': 'string',
                        'enum': ['skill', 'agent', 'all'],
                        'description': 'Art der gesuchten Einheit'
                    }
                },
                'required': ['query']
            }
        })
        
        # Execute-Tool
        tools.append({
            'name': 'hub_execute',
            'description': 'Führt einen Skill oder Agent aus dem Hub aus',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'description': 'Name des Skills oder Agents'
                    },
                    'inputs': {
                        'type': 'object',
                        'description': 'Input-Parameter für die Ausführung'
                    }
                },
                'required': ['name']
            }
        })
        
        # List-Tool
        tools.append({
            'name': 'hub_list',
            'description': 'Listet alle verfügbaren Skills und Agents auf',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'type': {
                        'type': 'string',
                        'enum': ['skill', 'agent', 'all'],
                        'description': 'Filterung nach Typ'
                    },
                    'include_imported': {
                        'type': 'boolean',
                        'description': 'Importierte Skills einschließen'
                    }
                }
            }
        })
        
        return tools
    
    def _get_mcp_resources(self) -> List[Dict]:
        """Generiert MCP-Resource-Definitionen."""
        return [
            {
                'uri': 'hub://catalog',
                'name': 'Skill & Agent Katalog',
                'description': 'Vollständiger Katalog aller verfügbaren Skills und Agents',
                'mimeType': 'application/json'
            },
            {
                'uri': 'hub://schema',
                'name': 'Manifest Schema',
                'description': 'JSON-Schema für Skill/Agent-Manifeste',
                'mimeType': 'application/json'
            },
            {
                'uri': 'hub://imported',
                'name': 'Importierte Skills',
                'description': 'Liste aller importierten Skills von externen Plattformen',
                'mimeType': 'application/json'
            }
        ]


class ClaudeCoworkAdapter(ClaudeAdapter):
    """
    Spezialisierter bidirektionaler Adapter für Claude Cowork.
    """
    
    @property
    def platform_name(self) -> str:
        return "Claude Cowork"
    
    def generate_cowork_skills(self) -> List[Dict]:
        """
        Generiert Skill-Manifeste für Claude Cowork-spezifische Funktionen.
        """
        cowork_skills = [
            # Projekt-Management
            {
                'name': 'cowork_create_project',
                'description': 'Erstellt ein neues Claude Cowork Projekt.',
                'tags': ['claude', 'cowork', 'project', 'create', 'imported'],
                'capabilities': ['project_management'],
                'implementation': {
                    'type': 'remote',
                    'language': 'cowork_api',
                    'target': {
                        'service': 'cowork',
                        'endpoint': '/projects/create'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'name', 'type': 'string', 'description': 'Projektname', 'required': True},
                        {'name': 'description', 'type': 'string', 'description': 'Projektbeschreibung', 'required': False},
                        {'name': 'instructions', 'type': 'string', 'description': 'Projekt-Anweisungen für Claude', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'project_id', 'type': 'string', 'description': 'Projekt-ID'},
                        {'name': 'status', 'type': 'string', 'description': 'Erstellungsstatus'}
                    ]
                }
            },
            # Artefakt-Erstellung
            {
                'name': 'cowork_create_artifact',
                'description': 'Erstellt ein Artefakt in einem Claude Cowork Projekt.',
                'tags': ['claude', 'cowork', 'artifact', 'create', 'imported'],
                'capabilities': ['artifact_management'],
                'implementation': {
                    'type': 'remote',
                    'language': 'cowork_api',
                    'target': {
                        'service': 'cowork',
                        'endpoint': '/artifacts/create'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'project_id', 'type': 'string', 'description': 'Projekt-ID', 'required': True},
                        {'name': 'type', 'type': 'string', 'description': 'Artefakt-Typ (code, document, image, etc.)', 'required': True},
                        {'name': 'content', 'type': 'string', 'description': 'Artefakt-Inhalt', 'required': True},
                        {'name': 'title', 'type': 'string', 'description': 'Artefakt-Titel', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'artifact_id', 'type': 'string', 'description': 'Artefakt-ID'},
                        {'name': 'url', 'type': 'string', 'description': 'Artefakt-URL'}
                    ]
                }
            },
            # Konversation fortsetzen
            {
                'name': 'cowork_continue_conversation',
                'description': 'Setzt eine bestehende Cowork-Konversation fort.',
                'tags': ['claude', 'cowork', 'conversation', 'chat', 'imported'],
                'capabilities': ['conversation_management'],
                'implementation': {
                    'type': 'remote',
                    'language': 'cowork_api',
                    'target': {
                        'service': 'cowork',
                        'endpoint': '/conversations/message'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'conversation_id', 'type': 'string', 'description': 'Konversations-ID', 'required': True},
                        {'name': 'message', 'type': 'string', 'description': 'Nachricht', 'required': True},
                        {'name': 'attachments', 'type': 'array', 'description': 'Anhänge (Dateien, Bilder)', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'response', 'type': 'string', 'description': 'Claude-Antwort'},
                        {'name': 'artifacts', 'type': 'array', 'description': 'Erstellte Artefakte'}
                    ]
                }
            },
            # Wissensquelle hinzufügen
            {
                'name': 'cowork_add_knowledge',
                'description': 'Fügt eine Wissensquelle zu einem Cowork-Projekt hinzu.',
                'tags': ['claude', 'cowork', 'knowledge', 'rag', 'imported'],
                'capabilities': ['knowledge_management', 'rag'],
                'implementation': {
                    'type': 'remote',
                    'language': 'cowork_api',
                    'target': {
                        'service': 'cowork',
                        'endpoint': '/knowledge/add'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'project_id', 'type': 'string', 'description': 'Projekt-ID', 'required': True},
                        {'name': 'source_type', 'type': 'string', 'description': 'Quellentyp (file, url, text)', 'required': True},
                        {'name': 'content', 'type': 'string', 'description': 'Inhalt oder URL', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'knowledge_id', 'type': 'string', 'description': 'Wissens-ID'},
                        {'name': 'status', 'type': 'string', 'description': 'Verarbeitungsstatus'}
                    ]
                }
            }
        ]
        
        return cowork_skills
    
    def generate_workspace_integration(self) -> str:
        """
        Generiert Integrationsanweisungen für Claude Cowork Workspaces.
        """
        return """
# Claude Cowork Integration (Bidirektional)

## Setup

1. Füge den Skill-Hub als MCP-Server hinzu:
   ```json
   {
     "mcpServers": {
       "skill-hub": {
         "command": "python",
         "args": ["/path/to/skill-agent-hub/adapters/mcp_server.py"]
       }
     }
   }
   ```

2. Die Skills und Agents sind dann über die MCP-Tools verfügbar:
   - `hub_discover`: Finde passende Skills
   - `hub_execute`: Führe Skills aus
   - `hub_list`: Liste alle verfügbaren Skills

## Bidirektionale Integration

Der Hub kann auch Cowork-Funktionen nutzen:

```python
# Projekt erstellen
result = hub.execute_skill('cowork_create_project', {
    'name': 'Mein Projekt',
    'description': 'Projektbeschreibung'
})

# Artefakt erstellen
result = hub.execute_skill('cowork_create_artifact', {
    'project_id': 'proj_123',
    'type': 'code',
    'content': 'print("Hello World")'
})
```

## Verwendung in Projekten

Referenziere Skills in deinen Projekt-Anweisungen:
```
Nutze den Skill 'text_summarizer' aus dem Hub, um lange Texte zusammenzufassen.
```
"""


class ClaudeCodeAdapter(ClaudeAdapter):
    """
    Spezialisierter bidirektionaler Adapter für Claude Code (CLI/IDE).
    """
    
    @property
    def platform_name(self) -> str:
        return "Claude Code"
    
    def generate_code_skills(self) -> List[Dict]:
        """
        Generiert Skill-Manifeste für Claude Code-spezifische Funktionen.
        """
        code_skills = [
            # Code-Analyse
            {
                'name': 'claude_code_analyze',
                'description': 'Analysiert Code mit Claude Code.',
                'tags': ['claude', 'code', 'analysis', 'review', 'imported'],
                'capabilities': ['code_analysis', 'code_review'],
                'implementation': {
                    'type': 'remote',
                    'language': 'claude_code_cli',
                    'target': {
                        'service': 'claude_code',
                        'command': 'analyze'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'code', 'type': 'string', 'description': 'Code zur Analyse', 'required': True},
                        {'name': 'language', 'type': 'string', 'description': 'Programmiersprache', 'required': False},
                        {'name': 'focus', 'type': 'string', 'description': 'Analysefokus (bugs, security, performance, style)', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'analysis', 'type': 'string', 'description': 'Analyseergebnis'},
                        {'name': 'issues', 'type': 'array', 'description': 'Gefundene Probleme'},
                        {'name': 'suggestions', 'type': 'array', 'description': 'Verbesserungsvorschläge'}
                    ]
                }
            },
            # Code-Generierung
            {
                'name': 'claude_code_generate',
                'description': 'Generiert Code mit Claude Code.',
                'tags': ['claude', 'code', 'generation', 'development', 'imported'],
                'capabilities': ['code_generation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'claude_code_cli',
                    'target': {
                        'service': 'claude_code',
                        'command': 'generate'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'description', 'type': 'string', 'description': 'Beschreibung des gewünschten Codes', 'required': True},
                        {'name': 'language', 'type': 'string', 'description': 'Ziel-Programmiersprache', 'required': True},
                        {'name': 'context', 'type': 'string', 'description': 'Zusätzlicher Kontext (bestehender Code, etc.)', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'code', 'type': 'string', 'description': 'Generierter Code'},
                        {'name': 'explanation', 'type': 'string', 'description': 'Erklärung des Codes'}
                    ]
                }
            },
            # Code-Refactoring
            {
                'name': 'claude_code_refactor',
                'description': 'Refaktoriert Code mit Claude Code.',
                'tags': ['claude', 'code', 'refactoring', 'improvement', 'imported'],
                'capabilities': ['code_refactoring'],
                'implementation': {
                    'type': 'remote',
                    'language': 'claude_code_cli',
                    'target': {
                        'service': 'claude_code',
                        'command': 'refactor'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'code', 'type': 'string', 'description': 'Code zum Refaktorieren', 'required': True},
                        {'name': 'goal', 'type': 'string', 'description': 'Refactoring-Ziel (readability, performance, modularity)', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'refactored_code', 'type': 'string', 'description': 'Refaktorierter Code'},
                        {'name': 'changes', 'type': 'array', 'description': 'Liste der Änderungen'}
                    ]
                }
            },
            # Test-Generierung
            {
                'name': 'claude_code_generate_tests',
                'description': 'Generiert Tests für Code mit Claude Code.',
                'tags': ['claude', 'code', 'testing', 'unit_tests', 'imported'],
                'capabilities': ['test_generation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'claude_code_cli',
                    'target': {
                        'service': 'claude_code',
                        'command': 'test'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'code', 'type': 'string', 'description': 'Code für den Tests generiert werden sollen', 'required': True},
                        {'name': 'framework', 'type': 'string', 'description': 'Test-Framework (pytest, jest, junit, etc.)', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'tests', 'type': 'string', 'description': 'Generierte Tests'},
                        {'name': 'coverage_estimate', 'type': 'number', 'description': 'Geschätzte Testabdeckung'}
                    ]
                }
            },
            # Dokumentation generieren
            {
                'name': 'claude_code_document',
                'description': 'Generiert Dokumentation für Code.',
                'tags': ['claude', 'code', 'documentation', 'docstring', 'imported'],
                'capabilities': ['documentation_generation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'claude_code_cli',
                    'target': {
                        'service': 'claude_code',
                        'command': 'document'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'code', 'type': 'string', 'description': 'Code zur Dokumentation', 'required': True},
                        {'name': 'style', 'type': 'string', 'description': 'Dokumentationsstil (google, numpy, sphinx)', 'required': False, 'default': 'google'}
                    ],
                    'outputs': [
                        {'name': 'documented_code', 'type': 'string', 'description': 'Code mit Dokumentation'},
                        {'name': 'readme', 'type': 'string', 'description': 'Generierte README'}
                    ]
                }
            }
        ]
        
        return code_skills
    
    def generate_slash_commands(self) -> List[Dict]:
        """
        Generiert Slash-Command-Definitionen für Claude Code.
        """
        commands = []
        
        for skill in self.get_all_skills():
            commands.append({
                'command': f"/skill-{skill['name']}",
                'description': skill.get('description', ''),
                'usage': f"/skill-{skill['name']} <inputs>"
            })
        
        for agent in self.get_all_agents():
            commands.append({
                'command': f"/agent-{agent['name']}",
                'description': f"[Agent] {agent.get('description', '')}",
                'usage': f"/agent-{agent['name']} <inputs>"
            })
        
        # Füge Hub-spezifische Befehle hinzu
        commands.extend([
            {
                'command': '/hub-discover',
                'description': 'Suche nach passenden Skills im Hub',
                'usage': '/hub-discover <beschreibung>'
            },
            {
                'command': '/hub-list',
                'description': 'Liste alle verfügbaren Skills',
                'usage': '/hub-list [type]'
            }
        ])
        
        return commands
