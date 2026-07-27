"""
Manus Shell Execute Skill
=========================
Führt Shell-Befehle in der Manus-Sandbox aus.
"""

import os
import json
import subprocess
from typing import Dict, Any, Optional


class ManusShellExecutor:
    """
    Shell-Befehlsausführung in Manus.
    """
    
    def __init__(self):
        self.default_shell = '/bin/bash'
    
    def execute(
        self,
        command: str,
        session: str = 'default',
        timeout: int = 30,
        working_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Führt einen Shell-Befehl aus.
        
        Args:
            command: Shell-Befehl
            session: Session-ID
            timeout: Timeout in Sekunden
            working_dir: Arbeitsverzeichnis
            
        Returns:
            Ausgabe mit output, exit_code und success
        """
        try:
            # Setze Arbeitsverzeichnis
            cwd = working_dir or os.path.expanduser('~')
            
            # Führe Befehl aus
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                executable=self.default_shell
            )
            
            # Kombiniere stdout und stderr
            output = result.stdout
            if result.stderr:
                output += '\n' + result.stderr if output else result.stderr
            
            return {
                'output': output.strip(),
                'exit_code': result.returncode,
                'success': result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {
                'output': f'Command timed out after {timeout} seconds',
                'exit_code': -1,
                'success': False,
                'error': 'timeout'
            }
        except Exception as e:
            return {
                'output': str(e),
                'exit_code': -1,
                'success': False,
                'error': str(e)
            }


def execute(
    command: str,
    session: str = 'default',
    timeout: int = 30,
    working_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Hauptfunktion für die Skill-Ausführung.
    """
    executor = ManusShellExecutor()
    return executor.execute(command, session, timeout, working_dir)


if __name__ == '__main__':
    # Test
    result = execute('echo "Hello from Manus Shell!"')
    print(json.dumps(result, indent=2))
