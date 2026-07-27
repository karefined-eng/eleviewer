"""
Microsoft 365 Copilot Adapter
=============================
Bidirektionaler Adapter für Microsoft 365 Copilot.
- Export: Stellt Hub-Skills als Copilot Plugins bereit
- Import: Integriert M365-Dienste (Outlook, Teams, SharePoint, etc.) als Hub-Skills
"""

import json
from typing import Dict, List, Any, Optional
from adapters.base_adapter import BaseAdapter


class Microsoft365CopilotAdapter(BaseAdapter):
    """
    Bidirektionaler Adapter für Microsoft 365 Copilot.
    
    Unterstützt:
    - Copilot Plugin Manifest (für Export)
    - Microsoft Graph API Integration (für Import)
    - Teams Message Extensions
    - Outlook Add-ins
    """
    
    @property
    def platform_name(self) -> str:
        return "Microsoft 365 Copilot"
    
    def format_skill_definition(self, skill: Dict) -> str:
        """
        Formatiert einen Skill als Copilot Plugin Action.
        Copilot verwendet OpenAPI-basierte Plugin-Definitionen.
        """
        interface = skill.get('interface', {})
        
        # Baue OpenAPI-kompatible Operation
        parameters = []
        required_params = []
        
        for inp in interface.get('inputs', []):
            param = {
                'name': inp['name'],
                'in': 'query',
                'description': inp.get('description', ''),
                'schema': {
                    'type': self._map_type_openapi(inp['type'])
                }
            }
            if inp.get('required', True):
                param['required'] = True
                required_params.append(inp['name'])
            parameters.append(param)
        
        action_def = {
            'operationId': f"hub_{skill['name']}",
            'summary': skill.get('description', ''),
            'description': f"Skill aus dem Skill & Agent Hub: {skill.get('description', '')}",
            'parameters': parameters,
            'responses': {
                '200': {
                    'description': 'Erfolgreiche Ausführung',
                    'content': {
                        'application/json': {
                            'schema': self._build_response_schema(interface.get('outputs', []))
                        }
                    }
                }
            }
        }
        
        return json.dumps(action_def, indent=2, ensure_ascii=False)
    
    def format_agent_definition(self, agent: Dict) -> str:
        """
        Formatiert einen Agent als Copilot Plugin mit mehreren Actions.
        """
        interface = agent.get('interface', {})
        
        action_def = {
            'operationId': f"hub_agent_{agent['name']}",
            'summary': f"[Agent] {agent.get('description', '')}",
            'description': f"Orchestrierender Agent aus dem Skill & Agent Hub. Kombiniert mehrere Skills zur Aufgabenerfüllung.",
            'parameters': self._build_parameters(interface.get('inputs', [])),
            'responses': {
                '200': {
                    'description': 'Erfolgreiche Ausführung',
                    'content': {
                        'application/json': {
                            'schema': self._build_response_schema(interface.get('outputs', []))
                        }
                    }
                }
            }
        }
        
        return json.dumps(action_def, indent=2, ensure_ascii=False)
    
    def _build_catalog(self, skills: List[str], agents: List[str]) -> str:
        """Baut den Microsoft 365 Copilot Plugin Katalog."""
        paths = {}
        
        for s in skills:
            action = json.loads(s)
            operation_id = action['operationId']
            paths[f"/skills/{operation_id.replace('hub_', '')}"] = {
                'post': action
            }
        
        for a in agents:
            action = json.loads(a)
            operation_id = action['operationId']
            paths[f"/agents/{operation_id.replace('hub_agent_', '')}"] = {
                'post': action
            }
        
        catalog = {
            'openapi': '3.1.0',
            'info': {
                'title': 'Skill & Agent Hub für Microsoft 365 Copilot',
                'version': '1.0.0',
                'description': 'Zentrale Skill-Bibliothek für Multi-Plattform-Orchestrierung'
            },
            'servers': [
                {'url': 'https://skill-hub.example.com/api/v1'}
            ],
            'paths': paths
        }
        
        return json.dumps(catalog, indent=2, ensure_ascii=False)
    
    def generate_copilot_plugin_manifest(self) -> Dict:
        """
        Generiert ein vollständiges Copilot Plugin Manifest.
        Kann direkt für die Registrierung im Microsoft 365 Admin Center verwendet werden.
        """
        return {
            '$schema': 'https://developer.microsoft.com/json-schemas/copilot/plugin/v2.1/schema.json',
            'schema_version': 'v2.1',
            'name_for_human': 'Skill & Agent Hub',
            'name_for_model': 'skill_agent_hub',
            'description_for_human': 'Zugriff auf eine zentrale Bibliothek von KI-Skills und Agents für erweiterte Automatisierung.',
            'description_for_model': 'Ein Hub für wiederverwendbare Skills und orchestrierende Agents. Nutze dieses Plugin, um Aufgaben wie Textzusammenfassung, Web-Scraping, Datenanalyse und mehr auszuführen.',
            'auth': {
                'type': 'none'  # Für Produktionsumgebung: 'oauth' oder 'api_key'
            },
            'api': {
                'type': 'openapi',
                'url': 'https://skill-hub.example.com/api/v1/openapi.json'
            },
            'logo_url': 'https://skill-hub.example.com/logo.png',
            'contact_email': 'support@skill-hub.example.com',
            'legal_info_url': 'https://skill-hub.example.com/legal',
            'capabilities': {
                'conversation_starters': [
                    'Fasse diesen Text zusammen',
                    'Analysiere diese Daten',
                    'Recherchiere zu diesem Thema'
                ]
            }
        }
    
    def generate_graph_api_skills(self) -> List[Dict]:
        """
        Generiert Skill-Manifeste für Microsoft Graph API Funktionen.
        Diese können als importierte Skills in den Hub aufgenommen werden.
        """
        graph_skills = [
            {
                'name': 'm365_send_email',
                'description': 'Sendet eine E-Mail über Microsoft 365 Outlook.',
                'tags': ['microsoft', 'outlook', 'email', 'communication'],
                'capabilities': ['send_email', 'communication'],
                'implementation': {
                    'type': 'remote',
                    'language': 'graph_api',
                    'target': {
                        'endpoint': '/me/sendMail',
                        'method': 'POST',
                        'scopes': ['Mail.Send']
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'to', 'type': 'string', 'description': 'Empfänger-E-Mail', 'required': True},
                        {'name': 'subject', 'type': 'string', 'description': 'Betreff', 'required': True},
                        {'name': 'body', 'type': 'string', 'description': 'E-Mail-Inhalt', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'status', 'type': 'string', 'description': 'Sendestatus'}
                    ]
                }
            },
            {
                'name': 'm365_create_event',
                'description': 'Erstellt einen Kalendereintrag in Microsoft 365.',
                'tags': ['microsoft', 'calendar', 'event', 'scheduling'],
                'capabilities': ['create_event', 'scheduling'],
                'implementation': {
                    'type': 'remote',
                    'language': 'graph_api',
                    'target': {
                        'endpoint': '/me/events',
                        'method': 'POST',
                        'scopes': ['Calendars.ReadWrite']
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'subject', 'type': 'string', 'description': 'Titel des Termins', 'required': True},
                        {'name': 'start', 'type': 'string', 'description': 'Startzeit (ISO 8601)', 'required': True},
                        {'name': 'end', 'type': 'string', 'description': 'Endzeit (ISO 8601)', 'required': True},
                        {'name': 'attendees', 'type': 'array', 'description': 'Liste der Teilnehmer-E-Mails', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'event_id', 'type': 'string', 'description': 'ID des erstellten Termins'}
                    ]
                }
            },
            {
                'name': 'm365_search_files',
                'description': 'Durchsucht OneDrive und SharePoint nach Dateien.',
                'tags': ['microsoft', 'onedrive', 'sharepoint', 'search', 'files'],
                'capabilities': ['file_search', 'document_retrieval'],
                'implementation': {
                    'type': 'remote',
                    'language': 'graph_api',
                    'target': {
                        'endpoint': '/me/drive/root/search(q=\'{query}\')',
                        'method': 'GET',
                        'scopes': ['Files.Read']
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'query', 'type': 'string', 'description': 'Suchbegriff', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'files', 'type': 'array', 'description': 'Liste der gefundenen Dateien'}
                    ]
                }
            },
            {
                'name': 'm365_send_teams_message',
                'description': 'Sendet eine Nachricht in einen Microsoft Teams Kanal.',
                'tags': ['microsoft', 'teams', 'chat', 'communication'],
                'capabilities': ['send_message', 'team_communication'],
                'implementation': {
                    'type': 'remote',
                    'language': 'graph_api',
                    'target': {
                        'endpoint': '/teams/{team_id}/channels/{channel_id}/messages',
                        'method': 'POST',
                        'scopes': ['ChannelMessage.Send']
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'team_id', 'type': 'string', 'description': 'ID des Teams', 'required': True},
                        {'name': 'channel_id', 'type': 'string', 'description': 'ID des Kanals', 'required': True},
                        {'name': 'message', 'type': 'string', 'description': 'Nachrichtentext', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'message_id', 'type': 'string', 'description': 'ID der gesendeten Nachricht'}
                    ]
                }
            }
        ]
        
        return graph_skills
    
    def _map_type_openapi(self, hub_type: str) -> str:
        """Mappt Hub-Typen auf OpenAPI-Typen."""
        type_mapping = {
            'string': 'string',
            'number': 'number',
            'boolean': 'boolean',
            'array': 'array',
            'object': 'object',
            'file': 'string'
        }
        return type_mapping.get(hub_type, 'string')
    
    def _build_parameters(self, inputs: List[Dict]) -> List[Dict]:
        """Baut Parameter-Liste für OpenAPI."""
        parameters = []
        for inp in inputs:
            param = {
                'name': inp['name'],
                'in': 'query',
                'description': inp.get('description', ''),
                'required': inp.get('required', True),
                'schema': {
                    'type': self._map_type_openapi(inp['type'])
                }
            }
            parameters.append(param)
        return parameters
    
    def _build_response_schema(self, outputs: List[Dict]) -> Dict:
        """Baut Response-Schema für OpenAPI."""
        properties = {}
        for out in outputs:
            properties[out['name']] = {
                'type': self._map_type_openapi(out['type']),
                'description': out.get('description', '')
            }
        
        return {
            'type': 'object',
            'properties': properties
        }
