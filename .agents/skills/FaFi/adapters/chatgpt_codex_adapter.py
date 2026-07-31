"""
ChatGPT Codex Adapter (Bidirektional)
=====================================
Bidirektionaler Adapter für ChatGPT Codex (OpenAI).
- Export: Stellt Hub-Skills im OpenAI Function Calling Format bereit
- Import: Integriert OpenAI-spezifische Fähigkeiten als Hub-Skills
"""

import json
from typing import Dict, List, Any
from adapters.base_adapter import BaseAdapter


class ChatGPTCodexAdapter(BaseAdapter):
    """
    Bidirektionaler Adapter für ChatGPT Codex.
    
    Unterstützt:
    - Export von Hub-Skills im OpenAI Function Calling Format
    - Export von Hub-Agents als Multi-Step Functions
    - Import von OpenAI API-Funktionen als Hub-Skills
    - GPT Actions Schema-Generierung
    """
    
    @property
    def platform_name(self) -> str:
        return "ChatGPT Codex"
    
    def format_skill_definition(self, skill: Dict) -> str:
        """
        Formatiert einen Skill im OpenAI Function Calling Format.
        """
        interface = skill.get('interface', {})
        
        # Baue Parameter-Schema nach OpenAI-Spezifikation
        properties = {}
        required = []
        
        for inp in interface.get('inputs', []):
            prop = {
                'type': self._map_type(inp['type']),
                'description': inp.get('description', '')
            }
            
            if inp['type'] == 'array':
                prop['items'] = {'type': 'string'}  # Default
            
            if 'enum' in inp:
                prop['enum'] = inp['enum']
            
            properties[inp['name']] = prop
            
            if inp.get('required', True):
                required.append(inp['name'])
        
        # OpenAI Function Format
        function_def = {
            'type': 'function',
            'function': {
                'name': skill['name'],
                'description': skill.get('description', ''),
                'parameters': {
                    'type': 'object',
                    'properties': properties,
                    'required': required,
                    'additionalProperties': False
                }
            }
        }
        
        return json.dumps(function_def, indent=2, ensure_ascii=False)
    
    def format_agent_definition(self, agent: Dict) -> str:
        """
        Formatiert einen Agent im OpenAI Function Calling Format.
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
        
        function_def = {
            'type': 'function',
            'function': {
                'name': f"agent_{agent['name']}",
                'description': f"[Multi-Step Agent] {agent.get('description', '')}",
                'parameters': {
                    'type': 'object',
                    'properties': properties,
                    'required': required,
                    'additionalProperties': False
                }
            }
        }
        
        return json.dumps(function_def, indent=2, ensure_ascii=False)
    
    def _build_catalog(self, skills: List[str], agents: List[str]) -> str:
        """Baut den OpenAI-kompatiblen Katalog."""
        tools = []
        
        for s in skills:
            tools.append(json.loads(s))
        
        for a in agents:
            tools.append(json.loads(a))
        
        return json.dumps({'tools': tools, 'bidirectional': True}, indent=2, ensure_ascii=False)
    
    def _map_type(self, hub_type: str) -> str:
        """Mappt Hub-Typen auf JSON-Schema-Typen für OpenAI."""
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
    
    def generate_openai_skills(self) -> List[Dict]:
        """
        Generiert Skill-Manifeste für OpenAI-spezifische Funktionen.
        Diese Skills ermöglichen den Zugriff auf OpenAI-Features vom Hub aus.
        """
        openai_skills = [
            # Chat Completion
            {
                'name': 'openai_chat_completion',
                'description': 'Führt eine Chat-Completion mit GPT-Modellen durch.',
                'tags': ['openai', 'gpt', 'chat', 'llm', 'imported'],
                'capabilities': ['chat', 'text_generation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'openai_api',
                    'target': {
                        'service': 'openai',
                        'endpoint': '/chat/completions'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'messages', 'type': 'array', 'description': 'Chat-Nachrichten', 'required': True},
                        {'name': 'model', 'type': 'string', 'description': 'Modell (gpt-4o, gpt-4-turbo, gpt-3.5-turbo)', 'required': False, 'default': 'gpt-4o'},
                        {'name': 'temperature', 'type': 'number', 'description': 'Temperatur (0-2)', 'required': False, 'default': 0.7},
                        {'name': 'max_tokens', 'type': 'number', 'description': 'Maximale Token-Anzahl', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'response', 'type': 'string', 'description': 'GPT-Antwort'},
                        {'name': 'usage', 'type': 'object', 'description': 'Token-Nutzung'},
                        {'name': 'finish_reason', 'type': 'string', 'description': 'Grund für das Beenden'}
                    ]
                }
            },
            # Vision
            {
                'name': 'openai_vision_analyze',
                'description': 'Analysiert Bilder mit GPT-4 Vision.',
                'tags': ['openai', 'gpt', 'vision', 'image', 'multimodal', 'imported'],
                'capabilities': ['image_analysis', 'vision', 'multimodal'],
                'implementation': {
                    'type': 'remote',
                    'language': 'openai_api',
                    'target': {
                        'service': 'openai',
                        'endpoint': '/chat/completions'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'image', 'type': 'string', 'description': 'Bild als URL oder Base64', 'required': True},
                        {'name': 'prompt', 'type': 'string', 'description': 'Frage oder Anweisung zum Bild', 'required': True},
                        {'name': 'detail', 'type': 'string', 'description': 'Detailgrad (low, high, auto)', 'required': False, 'default': 'auto'}
                    ],
                    'outputs': [
                        {'name': 'analysis', 'type': 'string', 'description': 'Bildanalyse'},
                        {'name': 'usage', 'type': 'object', 'description': 'Token-Nutzung'}
                    ]
                }
            },
            # DALL-E Bildgenerierung
            {
                'name': 'openai_dalle_generate',
                'description': 'Generiert Bilder mit DALL-E.',
                'tags': ['openai', 'dalle', 'image', 'generation', 'imported'],
                'capabilities': ['image_generation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'openai_api',
                    'target': {
                        'service': 'openai',
                        'endpoint': '/images/generations'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'prompt', 'type': 'string', 'description': 'Bildbeschreibung', 'required': True},
                        {'name': 'model', 'type': 'string', 'description': 'Modell (dall-e-3, dall-e-2)', 'required': False, 'default': 'dall-e-3'},
                        {'name': 'size', 'type': 'string', 'description': 'Größe (1024x1024, 1792x1024, 1024x1792)', 'required': False, 'default': '1024x1024'},
                        {'name': 'quality', 'type': 'string', 'description': 'Qualität (standard, hd)', 'required': False, 'default': 'standard'},
                        {'name': 'n', 'type': 'number', 'description': 'Anzahl der Bilder', 'required': False, 'default': 1}
                    ],
                    'outputs': [
                        {'name': 'images', 'type': 'array', 'description': 'Generierte Bilder (URLs)'},
                        {'name': 'revised_prompt', 'type': 'string', 'description': 'Überarbeiteter Prompt'}
                    ]
                }
            },
            # Whisper Transkription
            {
                'name': 'openai_whisper_transcribe',
                'description': 'Transkribiert Audio mit Whisper.',
                'tags': ['openai', 'whisper', 'audio', 'transcription', 'speech', 'imported'],
                'capabilities': ['speech_to_text', 'transcription'],
                'implementation': {
                    'type': 'remote',
                    'language': 'openai_api',
                    'target': {
                        'service': 'openai',
                        'endpoint': '/audio/transcriptions'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'audio_file', 'type': 'string', 'description': 'Pfad zur Audiodatei', 'required': True},
                        {'name': 'language', 'type': 'string', 'description': 'Sprache (ISO-639-1)', 'required': False},
                        {'name': 'response_format', 'type': 'string', 'description': 'Format (json, text, srt, vtt)', 'required': False, 'default': 'text'}
                    ],
                    'outputs': [
                        {'name': 'text', 'type': 'string', 'description': 'Transkribierter Text'},
                        {'name': 'segments', 'type': 'array', 'description': 'Zeitsegmente (bei json-Format)'}
                    ]
                }
            },
            # TTS Sprachsynthese
            {
                'name': 'openai_tts_generate',
                'description': 'Generiert Sprache aus Text mit OpenAI TTS.',
                'tags': ['openai', 'tts', 'speech', 'audio', 'generation', 'imported'],
                'capabilities': ['text_to_speech', 'audio_generation'],
                'implementation': {
                    'type': 'remote',
                    'language': 'openai_api',
                    'target': {
                        'service': 'openai',
                        'endpoint': '/audio/speech'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'text', 'type': 'string', 'description': 'Text zur Sprachsynthese', 'required': True},
                        {'name': 'voice', 'type': 'string', 'description': 'Stimme (alloy, echo, fable, onyx, nova, shimmer)', 'required': False, 'default': 'alloy'},
                        {'name': 'model', 'type': 'string', 'description': 'Modell (tts-1, tts-1-hd)', 'required': False, 'default': 'tts-1'},
                        {'name': 'speed', 'type': 'number', 'description': 'Geschwindigkeit (0.25-4.0)', 'required': False, 'default': 1.0}
                    ],
                    'outputs': [
                        {'name': 'audio_file', 'type': 'string', 'description': 'Pfad zur Audiodatei'},
                        {'name': 'duration', 'type': 'number', 'description': 'Dauer in Sekunden'}
                    ]
                }
            },
            # Embeddings
            {
                'name': 'openai_embeddings',
                'description': 'Generiert Text-Embeddings mit OpenAI.',
                'tags': ['openai', 'embeddings', 'vector', 'semantic', 'imported'],
                'capabilities': ['embeddings', 'semantic_search'],
                'implementation': {
                    'type': 'remote',
                    'language': 'openai_api',
                    'target': {
                        'service': 'openai',
                        'endpoint': '/embeddings'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'input', 'type': 'string', 'description': 'Text für Embedding', 'required': True},
                        {'name': 'model', 'type': 'string', 'description': 'Modell', 'required': False, 'default': 'text-embedding-3-small'}
                    ],
                    'outputs': [
                        {'name': 'embedding', 'type': 'array', 'description': 'Embedding-Vektor'},
                        {'name': 'dimensions', 'type': 'number', 'description': 'Anzahl der Dimensionen'}
                    ]
                }
            },
            # Assistants API
            {
                'name': 'openai_assistant_run',
                'description': 'Führt einen OpenAI Assistant aus.',
                'tags': ['openai', 'assistant', 'agent', 'automation', 'imported'],
                'capabilities': ['assistant', 'agent_execution'],
                'implementation': {
                    'type': 'remote',
                    'language': 'openai_api',
                    'target': {
                        'service': 'openai',
                        'endpoint': '/assistants'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'assistant_id', 'type': 'string', 'description': 'Assistant-ID', 'required': True},
                        {'name': 'message', 'type': 'string', 'description': 'Nachricht an den Assistant', 'required': True},
                        {'name': 'thread_id', 'type': 'string', 'description': 'Thread-ID (optional für Fortsetzung)', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'response', 'type': 'string', 'description': 'Assistant-Antwort'},
                        {'name': 'thread_id', 'type': 'string', 'description': 'Thread-ID'},
                        {'name': 'run_id', 'type': 'string', 'description': 'Run-ID'}
                    ]
                }
            },
            # Code Interpreter
            {
                'name': 'openai_code_interpreter',
                'description': 'Nutzt den OpenAI Code Interpreter für Datenanalyse.',
                'tags': ['openai', 'code', 'interpreter', 'analysis', 'imported'],
                'capabilities': ['code_execution', 'data_analysis'],
                'implementation': {
                    'type': 'remote',
                    'language': 'openai_api',
                    'target': {
                        'service': 'openai',
                        'endpoint': '/assistants'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'task', 'type': 'string', 'description': 'Aufgabenbeschreibung', 'required': True},
                        {'name': 'files', 'type': 'array', 'description': 'Dateien für die Analyse', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'result', 'type': 'string', 'description': 'Analyseergebnis'},
                        {'name': 'code', 'type': 'string', 'description': 'Ausgeführter Code'},
                        {'name': 'output_files', 'type': 'array', 'description': 'Generierte Dateien'}
                    ]
                }
            },
            # Moderation
            {
                'name': 'openai_moderation',
                'description': 'Prüft Text auf unangemessene Inhalte.',
                'tags': ['openai', 'moderation', 'safety', 'content', 'imported'],
                'capabilities': ['content_moderation', 'safety'],
                'implementation': {
                    'type': 'remote',
                    'language': 'openai_api',
                    'target': {
                        'service': 'openai',
                        'endpoint': '/moderations'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'input', 'type': 'string', 'description': 'Text zur Prüfung', 'required': True}
                    ],
                    'outputs': [
                        {'name': 'flagged', 'type': 'boolean', 'description': 'Wurde der Text markiert?'},
                        {'name': 'categories', 'type': 'object', 'description': 'Kategorien mit Flags'},
                        {'name': 'scores', 'type': 'object', 'description': 'Kategorien mit Scores'}
                    ]
                }
            },
            # Fine-Tuning
            {
                'name': 'openai_finetune_create',
                'description': 'Startet einen Fine-Tuning-Job.',
                'tags': ['openai', 'finetune', 'training', 'model', 'imported'],
                'capabilities': ['model_training', 'fine_tuning'],
                'implementation': {
                    'type': 'remote',
                    'language': 'openai_api',
                    'target': {
                        'service': 'openai',
                        'endpoint': '/fine_tuning/jobs'
                    }
                },
                'interface': {
                    'inputs': [
                        {'name': 'training_file', 'type': 'string', 'description': 'ID der Trainingsdatei', 'required': True},
                        {'name': 'model', 'type': 'string', 'description': 'Basismodell', 'required': True},
                        {'name': 'hyperparameters', 'type': 'object', 'description': 'Hyperparameter', 'required': False}
                    ],
                    'outputs': [
                        {'name': 'job_id', 'type': 'string', 'description': 'Fine-Tuning-Job-ID'},
                        {'name': 'status', 'type': 'string', 'description': 'Job-Status'}
                    ]
                }
            }
        ]
        
        return openai_skills
    
    def generate_openai_tools_array(self) -> List[Dict]:
        """
        Generiert ein Array von Tools für die OpenAI API.
        Kann direkt im `tools`-Parameter verwendet werden.
        """
        tools = []
        
        for skill in self.get_all_skills():
            tools.append(json.loads(self.format_skill_definition(skill)))
        
        for agent in self.get_all_agents():
            tools.append(json.loads(self.format_agent_definition(agent)))
        
        return tools
    
    def generate_assistant_instructions(self) -> str:
        """
        Generiert Anweisungen für einen OpenAI Assistant.
        """
        skills = self.get_all_skills()
        agents = self.get_all_agents()
        
        instructions = """
You have access to a Skill & Agent Hub that provides reusable capabilities.

## Available Skills

"""
        for skill in skills:
            instructions += f"- **{skill['name']}**: {skill.get('description', '')}\n"
        
        instructions += """

## Available Agents

"""
        for agent in agents:
            instructions += f"- **{agent['name']}**: {agent.get('description', '')}\n"
        
        instructions += """

## Bidirectional Integration

The Hub can also use OpenAI capabilities:

```python
# Generate image with DALL-E
result = hub.execute_skill('openai_dalle_generate', {
    'prompt': 'A futuristic city',
    'size': '1024x1024'
})

# Transcribe audio
result = hub.execute_skill('openai_whisper_transcribe', {
    'audio_file': '/path/to/audio.mp3'
})
```

## Usage Guidelines

1. When a task matches a skill's capability, use that skill
2. For complex multi-step tasks, consider using an agent
3. Skills can be chained - output from one can be input to another
4. If unsure which skill to use, describe the task and I'll help select

## Extending the Hub

New skills can be added by creating a manifest.json in the skills directory.
The hub automatically discovers and registers new capabilities.
"""
        
        return instructions
    
    def generate_gpt_action_schema(self) -> Dict:
        """
        Generiert ein Schema für GPT Actions (Custom GPTs).
        """
        paths = {}
        
        # Skill-Endpunkte
        for skill in self.get_all_skills():
            interface = skill.get('interface', {})
            
            request_body = {
                'type': 'object',
                'properties': {},
                'required': []
            }
            
            for inp in interface.get('inputs', []):
                request_body['properties'][inp['name']] = {
                    'type': self._map_type(inp['type']),
                    'description': inp.get('description', '')
                }
                if inp.get('required', True):
                    request_body['required'].append(inp['name'])
            
            paths[f"/skills/{skill['name']}/execute"] = {
                'post': {
                    'operationId': f"execute_{skill['name']}",
                    'summary': skill.get('description', ''),
                    'requestBody': {
                        'required': True,
                        'content': {
                            'application/json': {
                                'schema': request_body
                            }
                        }
                    },
                    'responses': {
                        '200': {
                            'description': 'Successful execution',
                            'content': {
                                'application/json': {
                                    'schema': {'type': 'object'}
                                }
                            }
                        }
                    }
                }
            }
        
        return {
            'openapi': '3.1.0',
            'info': {
                'title': 'Skill & Agent Hub API',
                'version': '2.0.0',
                'description': 'API für den Zugriff auf den zentralen Skill & Agent Hub (Bidirektional)'
            },
            'servers': [
                {'url': 'https://skill-hub.example.com/api/v1'}
            ],
            'paths': paths
        }
