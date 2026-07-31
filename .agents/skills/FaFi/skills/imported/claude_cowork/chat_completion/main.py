"""
Claude Chat Completion Skill
============================
Führt Chat-Completions mit Claude über die Anthropic API aus.
"""

import os
import json
from typing import Dict, Any, List, Optional


class ClaudeChatCompletion:
    """
    Chat-Completion mit Claude.
    """
    
    def __init__(self):
        self.api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        self.api_base = os.environ.get('ANTHROPIC_API_BASE', 'https://api.anthropic.com/v1')
    
    def execute(
        self,
        messages: List[Dict[str, str]],
        model: str = 'claude-3-sonnet-20240229',
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Führt eine Chat-Completion durch.
        
        Args:
            messages: Chat-Nachrichten
            model: Claude-Modell
            max_tokens: Maximale Token-Anzahl
            temperature: Temperatur
            system: System-Prompt
            
        Returns:
            Antwort mit response, usage und stop_reason
        """
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            kwargs = {
                'model': model,
                'max_tokens': max_tokens,
                'messages': messages,
                'temperature': temperature
            }
            
            if system:
                kwargs['system'] = system
            
            response = client.messages.create(**kwargs)
            
            return {
                'response': response.content[0].text if response.content else '',
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                },
                'stop_reason': response.stop_reason
            }
            
        except ImportError:
            # Fallback zu requests
            import requests
            
            headers = {
                'x-api-key': self.api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            payload = {
                'model': model,
                'max_tokens': max_tokens,
                'messages': messages,
                'temperature': temperature
            }
            
            if system:
                payload['system'] = system
            
            response = requests.post(
                f'{self.api_base}/messages',
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'response': data['content'][0]['text'] if data.get('content') else '',
                'usage': data.get('usage', {}),
                'stop_reason': data.get('stop_reason', '')
            }
            
        except Exception as e:
            return {
                'response': '',
                'usage': {},
                'stop_reason': 'error',
                'error': str(e)
            }


def execute(
    messages: List[Dict[str, str]],
    model: str = 'claude-3-sonnet-20240229',
    max_tokens: int = 4096,
    temperature: float = 0.7,
    system: Optional[str] = None
) -> Dict[str, Any]:
    """
    Hauptfunktion für die Skill-Ausführung.
    """
    executor = ClaudeChatCompletion()
    return executor.execute(messages, model, max_tokens, temperature, system)


if __name__ == '__main__':
    # Test
    result = execute([{'role': 'user', 'content': 'Hello!'}])
    print(json.dumps(result, indent=2))
