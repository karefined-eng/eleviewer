"""
OpenAI Chat Completion Skill
============================
Führt Chat-Completions mit GPT-Modellen über die OpenAI API aus.
"""

import os
import json
from typing import Dict, Any, List, Optional


class OpenAIChatCompletion:
    """
    Chat-Completion mit GPT-Modellen.
    """
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        self.api_base = os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
    
    def execute(
        self,
        messages: List[Dict[str, str]],
        model: str = 'gpt-4o',
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Führt eine Chat-Completion durch.
        
        Args:
            messages: Chat-Nachrichten
            model: GPT-Modell
            temperature: Temperatur
            max_tokens: Maximale Token-Anzahl
            
        Returns:
            Antwort mit response, usage und finish_reason
        """
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key, base_url=self.api_base)
            
            kwargs = {
                'model': model,
                'messages': messages,
                'temperature': temperature
            }
            
            if max_tokens:
                kwargs['max_tokens'] = max_tokens
            
            response = client.chat.completions.create(**kwargs)
            
            return {
                'response': response.choices[0].message.content if response.choices else '',
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                } if response.usage else {},
                'finish_reason': response.choices[0].finish_reason if response.choices else ''
            }
            
        except ImportError:
            # Fallback zu requests
            import requests
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': model,
                'messages': messages,
                'temperature': temperature
            }
            
            if max_tokens:
                payload['max_tokens'] = max_tokens
            
            response = requests.post(
                f'{self.api_base}/chat/completions',
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'response': data['choices'][0]['message']['content'] if data.get('choices') else '',
                'usage': data.get('usage', {}),
                'finish_reason': data['choices'][0].get('finish_reason', '') if data.get('choices') else ''
            }
            
        except Exception as e:
            return {
                'response': '',
                'usage': {},
                'finish_reason': 'error',
                'error': str(e)
            }


def execute(
    messages: List[Dict[str, str]],
    model: str = 'gpt-4o',
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> Dict[str, Any]:
    """
    Hauptfunktion für die Skill-Ausführung.
    """
    executor = OpenAIChatCompletion()
    return executor.execute(messages, model, temperature, max_tokens)


if __name__ == '__main__':
    # Test
    result = execute([{'role': 'user', 'content': 'Hello!'}])
    print(json.dumps(result, indent=2))
