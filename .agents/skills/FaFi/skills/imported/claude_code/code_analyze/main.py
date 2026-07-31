"""
Claude Code Analyze Skill
=========================
Analysiert Code mit Claude Code für Bugs, Sicherheit, Performance und Stil.
"""

import os
import json
import subprocess
from typing import Dict, Any, List, Optional


class ClaudeCodeAnalyzer:
    """
    Code-Analyse mit Claude Code.
    """
    
    def __init__(self):
        self.api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    
    def execute(
        self,
        code: str,
        language: Optional[str] = None,
        focus: str = 'all'
    ) -> Dict[str, Any]:
        """
        Analysiert Code.
        
        Args:
            code: Code zur Analyse
            language: Programmiersprache
            focus: Analysefokus (bugs, security, performance, style, all)
            
        Returns:
            Analyse mit issues und suggestions
        """
        # Baue den Analyse-Prompt
        focus_instructions = {
            'bugs': 'Focus on finding bugs, logic errors, and potential runtime issues.',
            'security': 'Focus on security vulnerabilities, injection risks, and unsafe patterns.',
            'performance': 'Focus on performance issues, inefficiencies, and optimization opportunities.',
            'style': 'Focus on code style, readability, and adherence to best practices.',
            'all': 'Analyze for bugs, security issues, performance problems, and style improvements.'
        }
        
        lang_hint = f' (Language: {language})' if language else ''
        
        prompt = f"""Analyze the following code{lang_hint}:

```
{code}
```

{focus_instructions.get(focus, focus_instructions['all'])}

Provide your analysis in the following JSON format:
{{
    "analysis": "Detailed analysis summary",
    "issues": [
        {{"type": "bug|security|performance|style", "line": number, "description": "Issue description", "severity": "high|medium|low"}}
    ],
    "suggestions": [
        {{"type": "improvement|refactoring|best_practice", "description": "Suggestion description", "code_snippet": "Optional improved code"}}
    ]
}}
"""
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model='claude-3-sonnet-20240229',
                max_tokens=4096,
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            # Parse JSON aus der Antwort
            response_text = response.content[0].text if response.content else '{}'
            
            # Versuche JSON zu extrahieren
            try:
                # Suche nach JSON-Block
                import re
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {
                        'analysis': response_text,
                        'issues': [],
                        'suggestions': []
                    }
            except json.JSONDecodeError:
                result = {
                    'analysis': response_text,
                    'issues': [],
                    'suggestions': []
                }
            
            return result
            
        except Exception as e:
            return {
                'analysis': f'Error during analysis: {str(e)}',
                'issues': [],
                'suggestions': [],
                'error': str(e)
            }


def execute(
    code: str,
    language: Optional[str] = None,
    focus: str = 'all'
) -> Dict[str, Any]:
    """
    Hauptfunktion für die Skill-Ausführung.
    """
    analyzer = ClaudeCodeAnalyzer()
    return analyzer.execute(code, language, focus)


if __name__ == '__main__':
    # Test
    test_code = '''
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        total = total + numbers[i]
    return total
'''
    result = execute(test_code, 'python', 'all')
    print(json.dumps(result, indent=2))
