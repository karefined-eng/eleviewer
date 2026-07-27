"""
Abacus AI Adapter
=================
Bidirektionaler Adapter für Abacus AI Plattform.
- Chat LLM: Konversations-KI mit Custom Models
- Deep Agent: Autonome Agenten für komplexe Aufgaben
- Abacus CLI: Kommandozeilen-Integration
"""

import json
import os
from typing import Dict, List, Any, Optional
from adapters.base_adapter import BaseAdapter


class AbacusAIAdapter(BaseAdapter):
    """
    Bidirektionaler Adapter für Abacus AI.
    
    Unterstützt:
    - Chat LLM für Konversationen
    - Deep Agent für autonome Aufgaben
    - CLI-Integration für Automatisierung
    """
    
    @property
    def platform_name(self) -> str:
        return "Abacus AI"
    
    def format_skill_definition(self, skill: Dict) -> str:
        """
        Formatiert einen Skill für Abacus AI.
        Abacus verwendet ein eigenes Format für Custom Functions.
        """
        interface = skill.get('interface', {})
        
        parameters = []
        for inp in interface.get('inputs', []):
            param = {
                'name': inp['name'],
                'type': self._map_type_abacus(inp['type']),
                'description': inp.get('description', ''),
                'required': inp.get('required', True)
            }
            if 'default' in inp:
                param['default'] = inp['default']
            parameters.append(param)
        
        returns = []
        for out in interface.get('outputs', []):
            returns.append({
                'name': out['name'],
                'type': self._map_type_abacus(out['type']),
                'description': out.get('description', '')
            })
        
        function_def = {
            'function_name': skill['name'],
            'description': skill.get('description', ''),
            'parameters': parameters,
            'returns': returns,
            'tags': skill.get('tags', []),
            'source': 'skill_agent_hub'
        }
        
        return json.dumps(function_def, indent=2, ensure_ascii=False)
    
    def format_agent_definition(self, agent: Dict) -> str:
        """Formatiert einen Agent für Abacus AI Deep Agent."""
        interface = agent.get('interface', {})
        orchestration = agent.get('orchestration', {})
        
        parameters = []
        for inp in interface.get('inputs', []):
            parameters.append({
                'name': inp['name'],
                'type': self._map_type_abacus(inp['type']),
                'description': inp.get('description', ''),
                'required': inp.get('required', True)
            })
        
        agent_def = {
            'agent_name': agent['name'],
            'description': agent.get('description', ''),
            'type': 'deep_agent',
            'parameters': parameters,
            'orchestration_strategy': orchestration.get('strategy', 'dynamic'),
            'capabilities': agent.get('capabilities', []),
            'dependencies': [d['name'] for d in agent.get('dependencies', [])],
            'source': 'skill_agent_hub'
        }
        
        return json.dumps(agent_def, indent=2, ensure_ascii=False)
    
    def _build_catalog(self, skills: List[str], agents: List[str]) -> str:
        """Baut den Abacus AI-Katalog."""
        catalog = {
            'source': 'skill_agent_hub',
            'version': '1.0',
            'functions': [json.loads(s) for s in skills],
            'agents': [json.loads(a) for a in agents]
        }
        
        return json.dumps(catalog, indent=2, ensure_ascii=False)
    
    def _map_type_abacus(self, hub_type: str) -> str:
        """Mappt Hub-Typen auf Abacus AI-Typen."""
        type_mapping = {
            'string': 'str',
            'number': 'float',
            'boolean': 'bool',
            'array': 'list',
            'object': 'dict',
            'file': 'str'
        }
        return type_mapping.get(hub_type, 'str')
    
    def generate_abacus_skills(self) -> List[Dict]:
        """
        Generiert Skill-Manifeste für Abacus AI-Funktionen.
        """
        abacus_skills = [
            # Chat LLM Skills
            {
                'name': 'abacus_chat_completion',
                'description': 'Führt eine Chat-Completion mit einem Abacus AI Modell durch.',
                'tags': ['abacus', 'chat', 'llm', 'completion'],
                'capabilities': ['chat', 'text_generation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'abacus_api',
                    'target': {
                        'service': 'chat_llm',
                        'endpoint': '/chat/completions'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'messages', 'type': 'array', 'description': 'Chat-Nachrichten', 'required': True},
                        {'name': 'model', 'type': 'string', 'description': 'Modell-ID', 'required': False, 'default': 'default'},
                        {'name': 'temperature', 'type': 'number', 'description': 'Temperatur (0-1)', 'required': False, 'default': 0.7}
                    ],
                    'outputs': [
                        {'name': 'response', 'type': 'string', 'description': 'Modellantwort'},
                        {'name': 'usage', 'type': 'object', 'description': 'Token-Nutzung'}
                    ]
                }
            },
            {
                'name': 'abacus_custom_model_inference',
                'description': 'Führt Inferenz mit einem benutzerdefinierten Abacus AI Modell durch.',
                'tags': ['abacus', 'custom_model', 'inference', 'ml'],
                'capabilities': ['custom_inference', 'ml_prediction'],
                'implementation': {
                    'type': 'remote',
                    'language': 'abacus_api',
                    'target': {
                        'service': 'custom_model',
                        'endpoint': '/models/{model_id}/predict'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'model_id', 'type': 'string', 'description': 'ID des Custom Models', 'required': True},
                        {'name': 'input_data', 'type': 'object', 'description': 'Eingabedaten für das Modell', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'prediction', 'type': 'object', 'description': 'Modellvorhersage'},
                        {'name': 'confidence', 'type': 'number', 'description': 'Konfidenzwert'}
                    ]
                }
            },
            # Deep Agent Skills
            {
                'name': 'abacus_deep_agent_execute',
                'description': 'Startet einen Abacus Deep Agent für eine komplexe Aufgabe.',
                'tags': ['abacus', 'deep_agent', 'autonomous', 'task'],
                'capabilities': ['autonomous_execution', 'complex_tasks'],
                'implementation': {
                    'type': 'remote',
                    'language': 'abacus_api',
                    'target': {
                        'service': 'deep_agent',
                        'endpoint': '/agents/execute'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'task', 'type': 'string', 'description': 'Aufgabenbeschreibung', 'required': True},
                        {'name': 'context', 'type': 'object', 'description': 'Zusätzlicher Kontext', 'required': False},
                        {'name': 'max_steps', 'type': 'number', 'description': 'Maximale Schritte', 'required': False, 'default': 10}
                    ],
                    'outputs': [
                        {'name': 'result', 'type': 'object', 'description': 'Ergebnis der Aufgabe'},
                        {'name': 'steps', 'type': 'array', 'description': 'Ausgeführte Schritte'},
                        {'name': 'status', 'type': 'string', 'description': 'Ausführungsstatus'}
                    ]
                }
            },
            {
                'name': 'abacus_deep_agent_research',
                'description': 'Nutzt Abacus Deep Agent für umfassende Recherche.',
                'tags': ['abacus', 'deep_agent', 'research', 'analysis'],
                'capabilities': ['research', 'information_gathering'],
                'implementation': {
                    'type': 'remote',
                    'language': 'abacus_api',
                    'target': {
                        'service': 'deep_agent',
                        'endpoint': '/agents/research'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'topic', 'type': 'string', 'description': 'Forschungsthema', 'required': True},
                        {'name': 'depth', 'type': 'string', 'description': 'Recherchetiefe (shallow, medium, deep)', 'required': False, 'default': 'medium'},
                        {'name': 'sources', 'type': 'array', 'description': 'Bevorzugte Quellen', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'report', 'type': 'string', 'description': 'Recherchebericht'},
                        {'name': 'sources', 'type': 'array', 'description': 'Verwendete Quellen'},
                        {'name': 'key_insights', 'type': 'array', 'description': 'Wichtigste Erkenntnisse'}
                    ]
                }
            },
            # CLI Skills
            {
                'name': 'abacus_cli_execute',
                'description': 'Führt einen Abacus CLI-Befehl aus.',
                'tags': ['abacus', 'cli', 'command', 'automation'],
                'capabilities': ['cli_execution', 'automation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'abacus_cli',
                    'target': {
                        'service': 'cli',
                        'command_prefix': 'abacus'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'command', 'type': 'string', 'description': 'CLI-Befehl (ohne "abacus" Präfix)', 'required': True},
                        {'name': 'args', 'type': 'object', 'description': 'Befehlsargumente', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'output', 'type': 'string', 'description': 'Befehlsausgabe'},
                        {'name': 'exit_code', 'type': 'number', 'description': 'Exit-Code'}
                    ]
                }
            },
            {
                'name': 'abacus_dataset_upload',
                'description': 'Lädt einen Datensatz zu Abacus AI hoch.',
                'tags': ['abacus', 'dataset', 'upload', 'data'],
                'capabilities': ['data_upload', 'dataset_management'],
                'implementation': {
                    'type': 'remote',
                    'language': 'abacus_api',
                    'target': {
                        'service': 'datasets',
                        'endpoint': '/datasets/upload'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'name', 'type': 'string', 'description': 'Name des Datensatzes', 'required': True},
                        {'name': 'file_path', 'type': 'string', 'description': 'Pfad zur Datei', 'required': True},
                        {'name': 'description', 'type': 'string', 'description': 'Beschreibung', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'dataset_id', 'type': 'string', 'description': 'ID des hochgeladenen Datensatzes'},
                        {'name': 'status', 'type': 'string', 'description': 'Upload-Status'}
                    ]
                }
            }
        ]
        
        return abacus_skills
    
    def generate_cli_wrapper(self) -> str:
        """
        Generiert einen Python-Wrapper für die Abacus CLI.
        """
        return '''
import subprocess
import json
from typing import Dict, Any, Optional

class AbacusCLI:
    """Wrapper für die Abacus CLI."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path
    
    def execute(self, command: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Führt einen Abacus CLI-Befehl aus.
        
        Args:
            command: CLI-Befehl (z.B. "models list", "datasets upload")
            args: Befehlsargumente als Dictionary
        
        Returns:
            Dictionary mit output und exit_code
        """
        cmd_parts = ["abacus"] + command.split()
        
        if args:
            for key, value in args.items():
                if isinstance(value, bool):
                    if value:
                        cmd_parts.append(f"--{key}")
                else:
                    cmd_parts.extend([f"--{key}", str(value)])
        
        if self.config_path:
            cmd_parts.extend(["--config", self.config_path])
        
        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True
            )
            
            return {
                "output": result.stdout or result.stderr,
                "exit_code": result.returncode
            }
        except Exception as e:
            return {
                "output": str(e),
                "exit_code": -1
            }
    
    def list_models(self) -> Dict[str, Any]:
        """Listet alle verfügbaren Modelle."""
        return self.execute("models list")
    
    def list_datasets(self) -> Dict[str, Any]:
        """Listet alle Datensätze."""
        return self.execute("datasets list")
    
    def run_agent(self, task: str, **kwargs) -> Dict[str, Any]:
        """Startet einen Deep Agent."""
        args = {"task": task, **kwargs}
        return self.execute("agent run", args)
'''
    
    def generate_deep_agent_config(self) -> Dict:
        """
        Generiert eine Konfiguration für Abacus Deep Agent.
        """
        return {
            'agent_config': {
                'name': 'SkillHubAgent',
                'description': 'Agent mit Zugriff auf den Skill & Agent Hub',
                'capabilities': [
                    'web_search',
                    'code_execution',
                    'file_operations',
                    'data_analysis'
                ],
                'tools': {
                    'skill_hub': {
                        'type': 'external_api',
                        'base_url': 'https://skill-hub.example.com/api/v1',
                        'endpoints': {
                            'discover': '/discover',
                            'execute_skill': '/execute/skill/{name}',
                            'execute_agent': '/execute/agent/{name}'
                        }
                    }
                },
                'settings': {
                    'max_iterations': 20,
                    'timeout_seconds': 300,
                    'verbose': True
                }
            }
        }
