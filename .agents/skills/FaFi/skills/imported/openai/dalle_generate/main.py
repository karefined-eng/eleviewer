"""
OpenAI DALL-E Generate Skill
============================
Generiert Bilder mit DALL-E über die OpenAI API.
"""

import os
import json
from typing import Dict, Any, List, Optional


class DALLEGenerator:
    """
    Bildgenerierung mit DALL-E.
    """
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        self.api_base = os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
    
    def execute(
        self,
        prompt: str,
        model: str = 'dall-e-3',
        size: str = '1024x1024',
        quality: str = 'standard',
        n: int = 1
    ) -> Dict[str, Any]:
        """
        Generiert Bilder mit DALL-E.
        
        Args:
            prompt: Bildbeschreibung
            model: DALL-E Modell
            size: Bildgröße
            quality: Qualität
            n: Anzahl der Bilder
            
        Returns:
            Bilder-URLs und überarbeiteter Prompt
        """
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key, base_url=self.api_base)
            
            response = client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n
            )
            
            images = [img.url for img in response.data]
            revised_prompt = response.data[0].revised_prompt if response.data and hasattr(response.data[0], 'revised_prompt') else prompt
            
            return {
                'images': images,
                'revised_prompt': revised_prompt
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
                'prompt': prompt,
                'size': size,
                'quality': quality,
                'n': n
            }
            
            response = requests.post(
                f'{self.api_base}/images/generations',
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            data = response.json()
            
            images = [img['url'] for img in data.get('data', [])]
            revised_prompt = data['data'][0].get('revised_prompt', prompt) if data.get('data') else prompt
            
            return {
                'images': images,
                'revised_prompt': revised_prompt
            }
            
        except Exception as e:
            return {
                'images': [],
                'revised_prompt': prompt,
                'error': str(e)
            }


def execute(
    prompt: str,
    model: str = 'dall-e-3',
    size: str = '1024x1024',
    quality: str = 'standard',
    n: int = 1
) -> Dict[str, Any]:
    """
    Hauptfunktion für die Skill-Ausführung.
    """
    generator = DALLEGenerator()
    return generator.execute(prompt, model, size, quality, n)


if __name__ == '__main__':
    # Test
    result = execute('A futuristic city at sunset')
    print(json.dumps(result, indent=2))
