"""
HubSpot & HubSpot Breeze Adapter
================================
Bidirektionaler Adapter für HubSpot CRM und HubSpot Breeze AI.
- Export: Stellt Hub-Skills für HubSpot Workflows bereit
- Import: Integriert HubSpot CRM-Funktionen und Breeze AI als Hub-Skills
"""

import json
import os
from typing import Dict, List, Any, Optional
from adapters.base_adapter import BaseAdapter


class HubSpotAdapter(BaseAdapter):
    """
    Bidirektionaler Adapter für HubSpot CRM.
    
    Unterstützt:
    - Kontakte, Unternehmen, Deals, Tickets
    - Workflows und Automatisierung
    - HubSpot Breeze AI Integration
    - MCP-Server-Integration
    """
    
    @property
    def platform_name(self) -> str:
        return "HubSpot"
    
    def format_skill_definition(self, skill: Dict) -> str:
        """
        Formatiert einen Skill für HubSpot Custom Actions.
        HubSpot Workflows können Custom Code Actions verwenden.
        """
        interface = skill.get('interface', {})
        
        # Baue HubSpot Custom Action Definition
        inputs = []
        for inp in interface.get('inputs', []):
            inputs.append({
                'fieldName': inp['name'],
                'fieldType': self._map_type_hubspot(inp['type']),
                'label': inp['name'].replace('_', ' ').title(),
                'description': inp.get('description', ''),
                'required': inp.get('required', True)
            })
        
        outputs = []
        for out in interface.get('outputs', []):
            outputs.append({
                'fieldName': out['name'],
                'fieldType': self._map_type_hubspot(out['type']),
                'label': out['name'].replace('_', ' ').title()
            })
        
        action_def = {
            'actionType': 'CUSTOM_CODE',
            'actionName': f"hub_{skill['name']}",
            'description': skill.get('description', ''),
            'inputs': inputs,
            'outputs': outputs,
            'executionUrl': f"https://skill-hub.example.com/api/v1/execute/skill/{skill['name']}"
        }
        
        return json.dumps(action_def, indent=2, ensure_ascii=False)
    
    def format_agent_definition(self, agent: Dict) -> str:
        """Formatiert einen Agent für HubSpot."""
        interface = agent.get('interface', {})
        
        inputs = []
        for inp in interface.get('inputs', []):
            inputs.append({
                'fieldName': inp['name'],
                'fieldType': self._map_type_hubspot(inp['type']),
                'label': inp['name'].replace('_', ' ').title(),
                'description': inp.get('description', ''),
                'required': inp.get('required', True)
            })
        
        action_def = {
            'actionType': 'CUSTOM_CODE',
            'actionName': f"hub_agent_{agent['name']}",
            'description': f"[Orchestrierender Agent] {agent.get('description', '')}",
            'inputs': inputs,
            'executionUrl': f"https://skill-hub.example.com/api/v1/execute/agent/{agent['name']}"
        }
        
        return json.dumps(action_def, indent=2, ensure_ascii=False)
    
    def _build_catalog(self, skills: List[str], agents: List[str]) -> str:
        """Baut den HubSpot-Katalog."""
        actions = [json.loads(s) for s in skills]
        actions.extend([json.loads(a) for a in agents])
        
        catalog = {
            'source': 'skill_agent_hub',
            'version': '1.0',
            'customActions': actions
        }
        
        return json.dumps(catalog, indent=2, ensure_ascii=False)
    
    def _map_type_hubspot(self, hub_type: str) -> str:
        """Mappt Hub-Typen auf HubSpot-Feldtypen."""
        type_mapping = {
            'string': 'STRING',
            'number': 'NUMBER',
            'boolean': 'BOOLEAN',
            'array': 'STRING',  # HubSpot verwendet JSON-Strings für Arrays
            'object': 'STRING',  # HubSpot verwendet JSON-Strings für Objekte
            'file': 'STRING'
        }
        return type_mapping.get(hub_type, 'STRING')
    
    def generate_hubspot_skills(self) -> List[Dict]:
        """
        Generiert Skill-Manifeste für HubSpot CRM-Funktionen.
        Diese nutzen den vorhandenen HubSpot MCP-Server.
        """
        hubspot_skills = [
            # Kontakte
            {
                'name': 'hubspot_create_contact',
                'description': 'Erstellt einen neuen Kontakt in HubSpot.',
                'tags': ['hubspot', 'crm', 'contact', 'create'],
                'capabilities': ['crm', 'contact_management'],
                'implementation': {
                    'type': 'remote',
                    'language': 'mcp',
                    'target': {
                        'server': 'hubspot',
                        'tool': 'create_contact'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'email', 'type': 'string', 'description': 'E-Mail-Adresse', 'required': True},
                        {'name': 'firstname', 'type': 'string', 'description': 'Vorname', 'required': False},
                        {'name': 'lastname', 'type': 'string', 'description': 'Nachname', 'required': False},
                        {'name': 'phone', 'type': 'string', 'description': 'Telefonnummer', 'required': False},
                        {'name': 'company', 'type': 'string', 'description': 'Unternehmen', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'contact_id', 'type': 'string', 'description': 'ID des erstellten Kontakts'},
                        {'name': 'status', 'type': 'string', 'description': 'Erstellungsstatus'}
                    ]
                }
            },
            {
                'name': 'hubspot_search_contacts',
                'description': 'Durchsucht Kontakte in HubSpot.',
                'tags': ['hubspot', 'crm', 'contact', 'search'],
                'capabilities': ['crm', 'search'],
                'implementation': {
                    'type': 'remote',
                    'language': 'mcp',
                    'target': {
                        'server': 'hubspot',
                        'tool': 'search_contacts'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'query', 'type': 'string', 'description': 'Suchbegriff', 'required': True},
                        {'name': 'limit', 'type': 'number', 'description': 'Maximale Anzahl Ergebnisse', 'required': False, 'default': 10}
                    ],
                    'outputs': [
                        {'name': 'contacts', 'type': 'array', 'description': 'Liste der gefundenen Kontakte'},
                        {'name': 'total', 'type': 'number', 'description': 'Gesamtanzahl Treffer'}
                    ]
                }
            },
            {
                'name': 'hubspot_update_contact',
                'description': 'Aktualisiert einen bestehenden Kontakt in HubSpot.',
                'tags': ['hubspot', 'crm', 'contact', 'update'],
                'capabilities': ['crm', 'contact_management'],
                'implementation': {
                    'type': 'remote',
                    'language': 'mcp',
                    'target': {
                        'server': 'hubspot',
                        'tool': 'update_contact'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'contact_id', 'type': 'string', 'description': 'ID des Kontakts', 'required': True},
                        {'name': 'properties', 'type': 'object', 'description': 'Zu aktualisierende Eigenschaften', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'status', 'type': 'string', 'description': 'Aktualisierungsstatus'}
                    ]
                }
            },
            # Unternehmen
            {
                'name': 'hubspot_create_company',
                'description': 'Erstellt ein neues Unternehmen in HubSpot.',
                'tags': ['hubspot', 'crm', 'company', 'create'],
                'capabilities': ['crm', 'company_management'],
                'implementation': {
                    'type': 'remote',
                    'language': 'mcp',
                    'target': {
                        'server': 'hubspot',
                        'tool': 'create_company'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'name', 'type': 'string', 'description': 'Unternehmensname', 'required': True},
                        {'name': 'domain', 'type': 'string', 'description': 'Website-Domain', 'required': False},
                        {'name': 'industry', 'type': 'string', 'description': 'Branche', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'company_id', 'type': 'string', 'description': 'ID des erstellten Unternehmens'}
                    ]
                }
            },
            {
                'name': 'hubspot_search_companies',
                'description': 'Durchsucht Unternehmen in HubSpot.',
                'tags': ['hubspot', 'crm', 'company', 'search'],
                'capabilities': ['crm', 'search'],
                'implementation': {
                    'type': 'remote',
                    'language': 'mcp',
                    'target': {
                        'server': 'hubspot',
                        'tool': 'search_companies'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'query', 'type': 'string', 'description': 'Suchbegriff', 'required': True},
                        {'name': 'limit', 'type': 'number', 'description': 'Maximale Anzahl Ergebnisse', 'required': False, 'default': 10}
                    ],
                    'outputs': [
                        {'name': 'companies', 'type': 'array', 'description': 'Liste der gefundenen Unternehmen'}
                    ]
                }
            },
            # Deals
            {
                'name': 'hubspot_create_deal',
                'description': 'Erstellt einen neuen Deal in HubSpot.',
                'tags': ['hubspot', 'crm', 'deal', 'sales', 'create'],
                'capabilities': ['crm', 'sales', 'deal_management'],
                'implementation': {
                    'type': 'remote',
                    'language': 'mcp',
                    'target': {
                        'server': 'hubspot',
                        'tool': 'create_deal'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'dealname', 'type': 'string', 'description': 'Name des Deals', 'required': True},
                        {'name': 'amount', 'type': 'number', 'description': 'Deal-Wert', 'required': False},
                        {'name': 'pipeline', 'type': 'string', 'description': 'Pipeline-ID', 'required': False},
                        {'name': 'dealstage', 'type': 'string', 'description': 'Deal-Phase', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'deal_id', 'type': 'string', 'description': 'ID des erstellten Deals'}
                    ]
                }
            },
            {
                'name': 'hubspot_get_deal_pipeline',
                'description': 'Ruft Informationen über Deal-Pipelines ab.',
                'tags': ['hubspot', 'crm', 'deal', 'pipeline'],
                'capabilities': ['crm', 'pipeline_management'],
                'implementation': {
                    'type': 'remote',
                    'language': 'mcp',
                    'target': {
                        'server': 'hubspot',
                        'tool': 'get_pipelines'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'pipeline_id', 'type': 'string', 'description': 'Pipeline-ID (optional für alle)', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'pipelines', 'type': 'array', 'description': 'Liste der Pipelines mit Phasen'}
                    ]
                }
            },
            # Tickets
            {
                'name': 'hubspot_create_ticket',
                'description': 'Erstellt ein neues Support-Ticket in HubSpot.',
                'tags': ['hubspot', 'crm', 'ticket', 'support', 'create'],
                'capabilities': ['crm', 'support', 'ticket_management'],
                'implementation': {
                    'type': 'remote',
                    'language': 'mcp',
                    'target': {
                        'server': 'hubspot',
                        'tool': 'create_ticket'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'subject', 'type': 'string', 'description': 'Ticket-Betreff', 'required': True},
                        {'name': 'content', 'type': 'string', 'description': 'Ticket-Inhalt', 'required': True},
                        {'name': 'priority', 'type': 'string', 'description': 'Priorität (LOW, MEDIUM, HIGH)', 'required': False, 'default': 'MEDIUM'}
                    ],
                    'outputs': [
                        {'name': 'ticket_id', 'type': 'string', 'description': 'ID des erstellten Tickets'}
                    ]
                }
            }
        ]
        
        return hubspot_skills
    
    def generate_hubspot_breeze_skills(self) -> List[Dict]:
        """
        Generiert Skill-Manifeste für HubSpot Breeze AI-Funktionen.
        """
        breeze_skills = [
            {
                'name': 'breeze_content_assistant',
                'description': 'Nutzt HubSpot Breeze AI zum Erstellen von Marketing-Inhalten.',
                'tags': ['hubspot', 'breeze', 'ai', 'content', 'marketing'],
                'capabilities': ['content_generation', 'marketing', 'ai_assistant'],
                'implementation': {
                    'type': 'remote',
                    'language': 'hubspot_breeze_api',
                    'target': {
                        'service': 'content_assistant',
                        'endpoint': '/breeze/content/generate'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'content_type', 'type': 'string', 'description': 'Art des Inhalts (email, blog, social, landing_page)', 'required': True},
                        {'name': 'topic', 'type': 'string', 'description': 'Thema oder Beschreibung', 'required': True},
                        {'name': 'tone', 'type': 'string', 'description': 'Tonalität (professional, casual, friendly)', 'required': False, 'default': 'professional'},
                        {'name': 'length', 'type': 'string', 'description': 'Länge (short, medium, long)', 'required': False, 'default': 'medium'}
                    ],
                    'outputs': [
                        {'name': 'content', 'type': 'string', 'description': 'Generierter Inhalt'},
                        {'name': 'suggestions', 'type': 'array', 'description': 'Verbesserungsvorschläge'}
                    ]
                }
            },
            {
                'name': 'breeze_copilot_chat',
                'description': 'Interagiert mit HubSpot Breeze Copilot für CRM-Aufgaben.',
                'tags': ['hubspot', 'breeze', 'copilot', 'ai', 'assistant'],
                'capabilities': ['ai_assistant', 'crm_automation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'hubspot_breeze_api',
                    'target': {
                        'service': 'copilot',
                        'endpoint': '/breeze/copilot/chat'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'message', 'type': 'string', 'description': 'Nachricht an den Copilot', 'required': True},
                        {'name': 'context', 'type': 'object', 'description': 'CRM-Kontext (contact_id, deal_id, etc.)', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'response', 'type': 'string', 'description': 'Copilot-Antwort'},
                        {'name': 'actions', 'type': 'array', 'description': 'Vorgeschlagene Aktionen'}
                    ]
                }
            },
            {
                'name': 'breeze_customer_agent',
                'description': 'Nutzt Breeze Customer Agent für automatisierten Kundensupport.',
                'tags': ['hubspot', 'breeze', 'customer_agent', 'support', 'ai'],
                'capabilities': ['customer_support', 'ai_agent', 'automation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'hubspot_breeze_api',
                    'target': {
                        'service': 'customer_agent',
                        'endpoint': '/breeze/agent/respond'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'customer_message', 'type': 'string', 'description': 'Kundennachricht', 'required': True},
                        {'name': 'conversation_id', 'type': 'string', 'description': 'Konversations-ID', 'required': False},
                        {'name': 'contact_id', 'type': 'string', 'description': 'HubSpot Kontakt-ID', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'response', 'type': 'string', 'description': 'Agent-Antwort'},
                        {'name': 'confidence', 'type': 'number', 'description': 'Konfidenzwert'},
                        {'name': 'escalate', 'type': 'boolean', 'description': 'Eskalation empfohlen'}
                    ]
                }
            },
            {
                'name': 'breeze_prospecting_agent',
                'description': 'Nutzt Breeze Prospecting Agent für Lead-Generierung.',
                'tags': ['hubspot', 'breeze', 'prospecting', 'leads', 'sales'],
                'capabilities': ['lead_generation', 'prospecting', 'sales_automation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'hubspot_breeze_api',
                    'target': {
                        'service': 'prospecting_agent',
                        'endpoint': '/breeze/prospecting/analyze'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'company_domain', 'type': 'string', 'description': 'Domain des Zielunternehmens', 'required': True},
                        {'name': 'ideal_customer_profile', 'type': 'object', 'description': 'ICP-Kriterien', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'company_info', 'type': 'object', 'description': 'Unternehmensinformationen'},
                        {'name': 'contacts', 'type': 'array', 'description': 'Potenzielle Ansprechpartner'},
                        {'name': 'fit_score', 'type': 'number', 'description': 'ICP-Übereinstimmung (0-100)'}
                    ]
                }
            },
            {
                'name': 'breeze_social_agent',
                'description': 'Nutzt Breeze Social Agent für Social Media Management.',
                'tags': ['hubspot', 'breeze', 'social', 'marketing', 'automation'],
                'capabilities': ['social_media', 'content_scheduling', 'marketing_automation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'hubspot_breeze_api',
                    'target': {
                        'service': 'social_agent',
                        'endpoint': '/breeze/social/generate'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'platform', 'type': 'string', 'description': 'Plattform (linkedin, twitter, facebook, instagram)', 'required': True},
                        {'name': 'topic', 'type': 'string', 'description': 'Thema des Posts', 'required': True},
                        {'name': 'goal', 'type': 'string', 'description': 'Ziel (engagement, awareness, conversion)', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'post_content', 'type': 'string', 'description': 'Generierter Post-Inhalt'},
                        {'name': 'hashtags', 'type': 'array', 'description': 'Empfohlene Hashtags'},
                        {'name': 'best_time', 'type': 'string', 'description': 'Empfohlene Veröffentlichungszeit'}
                    ]
                }
            }
        ]
        
        return breeze_skills
    
    def generate_mcp_integration_code(self) -> str:
        """
        Generiert Code für die MCP-Server-Integration mit HubSpot.
        """
        return '''
import subprocess
import json
from typing import Dict, Any, List

class HubSpotMCPClient:
    """Client für die HubSpot MCP-Server-Integration."""
    
    def __init__(self, server_name: str = "hubspot"):
        self.server_name = server_name
    
    def _execute_mcp(self, tool: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Führt einen MCP-Tool-Aufruf aus."""
        cmd = [
            "manus-mcp-cli",
            "tool", "call", tool,
            "--server", self.server_name,
            "--input", json.dumps(args)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"error": result.stderr}
    
    def create_contact(self, email: str, **properties) -> Dict[str, Any]:
        """Erstellt einen neuen Kontakt."""
        args = {"email": email, **properties}
        return self._execute_mcp("create_contact", args)
    
    def search_contacts(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Durchsucht Kontakte."""
        return self._execute_mcp("search_contacts", {"query": query, "limit": limit})
    
    def create_deal(self, dealname: str, **properties) -> Dict[str, Any]:
        """Erstellt einen neuen Deal."""
        args = {"dealname": dealname, **properties}
        return self._execute_mcp("create_deal", args)
    
    def create_company(self, name: str, **properties) -> Dict[str, Any]:
        """Erstellt ein neues Unternehmen."""
        args = {"name": name, **properties}
        return self._execute_mcp("create_company", args)
'''
