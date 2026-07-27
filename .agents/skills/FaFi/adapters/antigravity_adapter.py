"""
Antigravity Adapter (Bidirektional)
===================================
Bidirektionaler Adapter für Antigravity AI Platform.
- Export: Stellt Hub-Skills für Antigravity-Workflows bereit
- Import: Integriert Antigravity-Actions und Workflows als Hub-Skills
"""

import json
from typing import Dict, List, Any
from adapters.base_adapter import BaseAdapter


class AntigravityAdapter(BaseAdapter):
    """
    Bidirektionaler Adapter für Antigravity.
    
    Unterstützt:
    - Export von Hub-Skills als Antigravity Actions
    - Export von Hub-Agents als Antigravity Workflows
    - Import von Antigravity-Actions als Hub-Skills
    - Import von Antigravity-Workflows als Hub-Agents
    """
    
    @property
    def platform_name(self) -> str:
        return "Antigravity"
    
    def format_skill_definition(self, skill: Dict) -> str:
        """
        Formatiert einen Skill für Antigravity.
        Antigravity verwendet ein modulares Action-Format.
        """
        interface = skill.get('interface', {})
        
        # Antigravity Action Format
        action_def = {
            'action_id': skill['name'],
            'action_type': 'skill',
            'display_name': skill['name'].replace('_', ' ').title(),
            'description': skill.get('description', ''),
            'category': self._infer_category(skill),
            'inputs': [],
            'outputs': [],
            'execution': {
                'type': skill.get('implementation_language', 'python'),
                'handler': skill.get('entrypoint', 'main.py')
            }
        }
        
        # Inputs
        for inp in interface.get('inputs', []):
            action_def['inputs'].append({
                'name': inp['name'],
                'type': self._map_type_antigravity(inp['type']),
                'label': inp['name'].replace('_', ' ').title(),
                'description': inp.get('description', ''),
                'required': inp.get('required', True),
                'default': inp.get('default')
            })
        
        # Outputs
        for out in interface.get('outputs', []):
            action_def['outputs'].append({
                'name': out['name'],
                'type': self._map_type_antigravity(out['type']),
                'label': out['name'].replace('_', ' ').title(),
                'description': out.get('description', '')
            })
        
        return json.dumps(action_def, indent=2, ensure_ascii=False)
    
    def format_agent_definition(self, agent: Dict) -> str:
        """
        Formatiert einen Agent für Antigravity.
        Agents werden als Workflow-Templates dargestellt.
        """
        interface = agent.get('interface', {})
        
        workflow_def = {
            'workflow_id': agent['name'],
            'workflow_type': 'agent',
            'display_name': agent['name'].replace('_', ' ').title(),
            'description': agent.get('description', ''),
            'category': 'Orchestration',
            'inputs': [],
            'outputs': [],
            'orchestration': {
                'strategy': 'dynamic',
                'capabilities': agent.get('capabilities', [])
            }
        }
        
        for inp in interface.get('inputs', []):
            workflow_def['inputs'].append({
                'name': inp['name'],
                'type': self._map_type_antigravity(inp['type']),
                'label': inp['name'].replace('_', ' ').title(),
                'description': inp.get('description', ''),
                'required': inp.get('required', True)
            })
        
        for out in interface.get('outputs', []):
            workflow_def['outputs'].append({
                'name': out['name'],
                'type': self._map_type_antigravity(out['type']),
                'label': out['name'].replace('_', ' ').title(),
                'description': out.get('description', '')
            })
        
        return json.dumps(workflow_def, indent=2, ensure_ascii=False)
    
    def _build_catalog(self, skills: List[str], agents: List[str]) -> str:
        """Baut den Antigravity-spezifischen Katalog."""
        catalog = {
            'version': '1.0',
            'platform': 'antigravity',
            'actions': [json.loads(s) for s in skills],
            'workflows': [json.loads(a) for a in agents]
        }
        
        return json.dumps(catalog, indent=2, ensure_ascii=False)
    
    def _map_type_antigravity(self, hub_type: str) -> str:
        """Mappt Hub-Typen auf Antigravity-Typen."""
        type_mapping = {
            'string': 'text',
            'number': 'number',
            'boolean': 'boolean',
            'array': 'list',
            'object': 'json',
            'file': 'file'
        }
        return type_mapping.get(hub_type, 'text')
    
    def _map_type_from_antigravity(self, ag_type: str) -> str:
        """Mappt Antigravity-Typen auf Hub-Typen."""
        type_mapping = {
            'text': 'string',
            'number': 'number',
            'boolean': 'boolean',
            'list': 'array',
            'json': 'object',
            'file': 'file'
        }
        return type_mapping.get(ag_type, 'string')
    
    def _infer_category(self, skill: Dict) -> str:
        """Inferiert eine Kategorie basierend auf Tags."""
        tags = skill.get('tags', [])
        
        category_mapping = {
            'text': 'Text Processing',
            'nlp': 'Text Processing',
            'data': 'Data Management',
            'file': 'File Operations',
            'web': 'Web & API',
            'api': 'Web & API',
            'email': 'Communication',
            'image': 'Media',
            'code': 'Development'
        }
        
        for tag in tags:
            if tag.lower() in category_mapping:
                return category_mapping[tag.lower()]
        
        return 'General'
    
    # ============== Bidirektionale Import-Funktionen ==============
    
    def generate_antigravity_skills(self) -> List[Dict]:
        """
        Generiert Skill-Manifeste für Antigravity-spezifische Funktionen.
        Diese Skills ermöglichen den Zugriff auf Antigravity-Features vom Hub aus.
        """
        antigravity_skills = [
            # Workflow-Ausführung
            {
                'name': 'antigravity_execute_workflow',
                'description': 'Führt einen Antigravity-Workflow aus.',
                'tags': ['antigravity', 'workflow', 'automation', 'imported'],
                'capabilities': ['workflow_execution', 'automation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'antigravity_api',
                    'target': {
                        'service': 'antigravity',
                        'endpoint': '/workflows/execute'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'workflow_id', 'type': 'string', 'description': 'ID des Workflows', 'required': True},
                        {'name': 'inputs', 'type': 'object', 'description': 'Workflow-Eingaben', 'required': True},
                        {'name': 'async_mode', 'type': 'boolean', 'description': 'Asynchrone Ausführung', 'required': False, 'default': False}
                    ],
                    'outputs': [
                        {'name': 'result', 'type': 'object', 'description': 'Workflow-Ergebnis'},
                        {'name': 'execution_id', 'type': 'string', 'description': 'Ausführungs-ID'},
                        {'name': 'status', 'type': 'string', 'description': 'Ausführungsstatus'}
                    ]
                }
            },
            # Action-Ausführung
            {
                'name': 'antigravity_execute_action',
                'description': 'Führt eine einzelne Antigravity-Action aus.',
                'tags': ['antigravity', 'action', 'automation', 'imported'],
                'capabilities': ['action_execution'],
                'implementation': {
                    'type': 'remote',
                    'language': 'antigravity_api',
                    'target': {
                        'service': 'antigravity',
                        'endpoint': '/actions/execute'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'action_id', 'type': 'string', 'description': 'ID der Action', 'required': True},
                        {'name': 'inputs', 'type': 'object', 'description': 'Action-Eingaben', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'result', 'type': 'object', 'description': 'Action-Ergebnis'},
                        {'name': 'status', 'type': 'string', 'description': 'Ausführungsstatus'}
                    ]
                }
            },
            # Workflow-Erstellung
            {
                'name': 'antigravity_create_workflow',
                'description': 'Erstellt einen neuen Antigravity-Workflow.',
                'tags': ['antigravity', 'workflow', 'create', 'imported'],
                'capabilities': ['workflow_management'],
                'implementation': {
                    'type': 'remote',
                    'language': 'antigravity_api',
                    'target': {
                        'service': 'antigravity',
                        'endpoint': '/workflows/create'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'name', 'type': 'string', 'description': 'Name des Workflows', 'required': True},
                        {'name': 'description', 'type': 'string', 'description': 'Beschreibung', 'required': False},
                        {'name': 'steps', 'type': 'array', 'description': 'Workflow-Schritte', 'required': True},
                        {'name': 'trigger', 'type': 'object', 'description': 'Trigger-Konfiguration', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'workflow_id', 'type': 'string', 'description': 'ID des erstellten Workflows'},
                        {'name': 'status', 'type': 'string', 'description': 'Erstellungsstatus'}
                    ]
                }
            },
            # Workflow-Liste
            {
                'name': 'antigravity_list_workflows',
                'description': 'Listet alle verfügbaren Antigravity-Workflows auf.',
                'tags': ['antigravity', 'workflow', 'list', 'imported'],
                'capabilities': ['workflow_management'],
                'implementation': {
                    'type': 'remote',
                    'language': 'antigravity_api',
                    'target': {
                        'service': 'antigravity',
                        'endpoint': '/workflows/list'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'category', 'type': 'string', 'description': 'Filter nach Kategorie', 'required': False},
                        {'name': 'limit', 'type': 'number', 'description': 'Maximale Anzahl', 'required': False, 'default': 50}
                    ],
                    'outputs': [
                        {'name': 'workflows', 'type': 'array', 'description': 'Liste der Workflows'},
                        {'name': 'total', 'type': 'number', 'description': 'Gesamtanzahl'}
                    ]
                }
            },
            # Daten-Connector
            {
                'name': 'antigravity_data_connector',
                'description': 'Verbindet mit einer Antigravity-Datenquelle.',
                'tags': ['antigravity', 'data', 'connector', 'imported'],
                'capabilities': ['data_integration'],
                'implementation': {
                    'type': 'remote',
                    'language': 'antigravity_api',
                    'target': {
                        'service': 'antigravity',
                        'endpoint': '/data/connect'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'connector_type', 'type': 'string', 'description': 'Typ des Connectors (database, api, file)', 'required': True},
                        {'name': 'config', 'type': 'object', 'description': 'Connector-Konfiguration', 'required': True},
                        {'name': 'query', 'type': 'string', 'description': 'Datenabfrage', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'data', 'type': 'array', 'description': 'Abgerufene Daten'},
                        {'name': 'schema', 'type': 'object', 'description': 'Datenschema'}
                    ]
                }
            },
            # Scheduling
            {
                'name': 'antigravity_schedule_workflow',
                'description': 'Plant die zeitgesteuerte Ausführung eines Workflows.',
                'tags': ['antigravity', 'workflow', 'schedule', 'automation', 'imported'],
                'capabilities': ['scheduling', 'automation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'antigravity_api',
                    'target': {
                        'service': 'antigravity',
                        'endpoint': '/workflows/schedule'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'workflow_id', 'type': 'string', 'description': 'ID des Workflows', 'required': True},
                        {'name': 'cron', 'type': 'string', 'description': 'Cron-Ausdruck', 'required': True},
                        {'name': 'inputs', 'type': 'object', 'description': 'Workflow-Eingaben', 'required': False},
                        {'name': 'enabled', 'type': 'boolean', 'description': 'Zeitplan aktiviert', 'required': False, 'default': True}
                    ],
                    'outputs': [
                        {'name': 'schedule_id', 'type': 'string', 'description': 'ID des Zeitplans'},
                        {'name': 'next_run', 'type': 'string', 'description': 'Nächste geplante Ausführung'}
                    ]
                }
            }
        ]
        
        return antigravity_skills
    
    def generate_antigravity_manifest(self) -> Dict:
        """
        Generiert ein Antigravity-Paket-Manifest.
        """
        return {
            'package': {
                'name': 'skill-agent-hub',
                'version': '2.0.0',
                'description': 'Zentraler Hub für wiederverwendbare Skills und Agents (Bidirektional)',
                'author': 'Manus AI',
                'license': 'MIT'
            },
            'dependencies': [],
            'actions': [s['name'] for s in self.get_all_skills()],
            'workflows': [a['name'] for a in self.get_all_agents()],
            'exports': {
                'actions': True,
                'workflows': True
            },
            'imports': {
                'enabled': True,
                'skills': [s['name'] for s in self.generate_antigravity_skills()]
            }
        }
    
    def generate_workflow_template(self, agent_name: str) -> Dict:
        """
        Generiert eine Workflow-Vorlage für einen Agent.
        """
        agent = self.registry.get_by_name(agent_name) if hasattr(self, 'registry') else None
        if not agent:
            return {}
        
        return {
            'workflow': {
                'id': agent_name,
                'name': agent['name'].replace('_', ' ').title(),
                'description': agent.get('description', ''),
                'trigger': {
                    'type': 'manual',
                    'inputs': agent.get('interface', {}).get('inputs', [])
                },
                'steps': [],  # Wird dynamisch gefüllt
                'outputs': agent.get('interface', {}).get('outputs', [])
            },
            'metadata': {
                'created_by': 'skill-agent-hub',
                'version': agent.get('version', '1.0.0')
            }
        }
    
    def generate_integration_guide(self) -> str:
        """
        Generiert eine Integrationsanleitung für Antigravity.
        """
        return """
# Antigravity Integration Guide (Bidirektional)

## Installation

1. Importiere das Skill-Hub-Paket in deinen Antigravity-Workspace
2. Die Actions und Workflows werden automatisch verfügbar

## Export: Hub-Skills in Antigravity nutzen

Actions können in Workflows per Drag-and-Drop hinzugefügt werden:

1. Öffne den Action-Katalog
2. Suche nach dem gewünschten Skill
3. Ziehe die Action in deinen Workflow
4. Konfiguriere die Inputs

## Import: Antigravity-Features im Hub nutzen

Der Hub kann Antigravity-Workflows und Actions aufrufen:

```python
# Workflow ausführen
result = hub.execute_skill('antigravity_execute_workflow', {
    'workflow_id': 'mein_workflow',
    'inputs': {'param1': 'wert1'}
})

# Action ausführen
result = hub.execute_skill('antigravity_execute_action', {
    'action_id': 'meine_action',
    'inputs': {'text': 'Eingabetext'}
})
```

## Dynamische Erweiterung

Neue Skills werden automatisch erkannt, wenn sie zum Hub hinzugefügt werden.
Aktualisiere den Katalog, um neue Capabilities zu sehen.

## API-Integration

```python
from antigravity import Client

client = Client()

# Skill ausführen
result = client.execute_action('text_summarizer', {
    'text': 'Langer Text...',
    'max_length': 100
})

# Agent ausführen
result = client.execute_workflow('research_agent', {
    'topic': 'AI Trends 2026'
})
```
"""
