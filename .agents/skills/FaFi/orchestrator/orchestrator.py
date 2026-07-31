"""
Orchestrator Engine
===================
Zentrale Engine zur dynamischen Orchestrierung von Skills und Agents.
Unterstützt verschiedene Ausführungsstrategien und automatische Planung.
"""

import json
import os
import sys
import subprocess
import importlib.util
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from registry.registry import SkillAgentRegistry
from orchestrator.discovery import DiscoveryService


class ExecutionStrategy(Enum):
    """Ausführungsstrategien für Orchestrierung."""
    SEQUENTIAL = "sequential"      # Schritte nacheinander
    PARALLEL = "parallel"          # Schritte parallel (wo möglich)
    CONDITIONAL = "conditional"    # Bedingte Ausführung
    DYNAMIC = "dynamic"            # Dynamische Planung zur Laufzeit


@dataclass
class ExecutionContext:
    """Kontext für die Ausführung eines Skills/Agents."""
    task_id: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    execution_log: List[Dict] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    status: str = "pending"
    error: Optional[str] = None


@dataclass
class ExecutionStep:
    """Ein einzelner Ausführungsschritt."""
    skill_name: str
    input_mapping: Dict[str, str]  # Mapping von Skill-Input zu Context-Variable
    output_mapping: Dict[str, str]  # Mapping von Skill-Output zu Context-Variable
    condition: Optional[str] = None  # Optionale Bedingung für Ausführung


class Orchestrator:
    """
    Zentrale Orchestrierungs-Engine.
    Koordiniert die Ausführung von Skills und Agents.
    """
    
    def __init__(self, 
                 registry: SkillAgentRegistry = None,
                 base_path: str = None):
        """
        Initialisiert den Orchestrator.
        
        Args:
            registry: Registry-Instanz
            base_path: Basispfad zum Skill-Hub
        """
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.registry = registry or SkillAgentRegistry(
            db_path=os.path.join(self.base_path, 'registry', 'registry.db'),
            base_path=self.base_path
        )
        self.discovery = DiscoveryService(self.registry)
        self._skill_cache: Dict[str, Callable] = {}
    
    def execute_skill(self, 
                      skill_name: str, 
                      inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt einen einzelnen Skill aus.
        
        Args:
            skill_name: Name des Skills
            inputs: Input-Parameter
            
        Returns:
            Output-Dictionary des Skills
        """
        # Hole Skill-Definition
        skill = self.registry.get_by_name(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' nicht gefunden")
        
        if skill['type'] != 'skill':
            raise ValueError(f"'{skill_name}' ist kein Skill, sondern ein {skill['type']}")
        
        # Validiere Inputs
        self._validate_inputs(skill, inputs)
        
        # Lade und führe Skill aus
        implementation = skill.get('implementation_language', 'python')
        
        if implementation == 'python':
            return self._execute_python_skill(skill, inputs)
        elif implementation == 'prompt':
            return self._execute_prompt_skill(skill, inputs)
        elif implementation == 'shell':
            return self._execute_shell_skill(skill, inputs)
        else:
            raise ValueError(f"Nicht unterstützte Implementierung: {implementation}")
    
    def execute_agent(self,
                      agent_name: str,
                      inputs: Dict[str, Any],
                      context: ExecutionContext = None) -> ExecutionContext:
        """
        Führt einen Agent aus.
        
        Args:
            agent_name: Name des Agents
            inputs: Input-Parameter
            context: Optionaler bestehender Kontext
            
        Returns:
            ExecutionContext mit Ergebnissen
        """
        # Hole Agent-Definition
        agent = self.registry.get_by_name(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' nicht gefunden")
        
        if agent['type'] != 'agent':
            raise ValueError(f"'{agent_name}' ist kein Agent, sondern ein {agent['type']}")
        
        # Erstelle oder nutze Kontext
        if context is None:
            context = ExecutionContext(
                task_id=f"{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                inputs=inputs
            )
        
        context.status = "running"
        
        try:
            # Lade Orchestrierungslogik
            manifest_path = agent['manifest_path']
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            orchestration = manifest.get('orchestration', {})
            strategy = ExecutionStrategy(orchestration.get('strategy', 'sequential'))
            
            if strategy == ExecutionStrategy.DYNAMIC:
                self._execute_dynamic(agent, context, orchestration)
            elif strategy == ExecutionStrategy.SEQUENTIAL:
                self._execute_sequential(agent, context, orchestration)
            elif strategy == ExecutionStrategy.PARALLEL:
                self._execute_parallel(agent, context, orchestration)
            elif strategy == ExecutionStrategy.CONDITIONAL:
                self._execute_conditional(agent, context, orchestration)
            
            context.status = "completed"
            context.completed_at = datetime.now()
            
        except Exception as e:
            context.status = "failed"
            context.error = str(e)
            context.execution_log.append({
                'timestamp': datetime.now().isoformat(),
                'event': 'error',
                'message': str(e),
                'traceback': traceback.format_exc()
            })
        
        return context
    
    def execute_task(self,
                     task_description: str,
                     inputs: Dict[str, Any] = None) -> ExecutionContext:
        """
        Führt eine Aufgabe basierend auf natürlichsprachlicher Beschreibung aus.
        Nutzt Discovery, um passende Skills zu finden und zu orchestrieren.
        
        Args:
            task_description: Beschreibung der Aufgabe
            inputs: Verfügbare Inputs
            
        Returns:
            ExecutionContext mit Ergebnissen
        """
        context = ExecutionContext(
            task_id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            inputs=inputs or {}
        )
        context.status = "planning"
        
        # Finde passende Skills
        composition = self.discovery.suggest_composition(task_description)
        
        context.execution_log.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'planning_complete',
            'composition': composition
        })
        
        context.status = "running"
        
        # Führe Schritte aus
        for step in composition['steps']:
            skill_name = step['suggested_skill']
            
            try:
                # Bereite Inputs vor (vereinfacht: nutze alle verfügbaren)
                skill = self.registry.get_by_name(skill_name)
                step_inputs = self._prepare_step_inputs(skill, context)
                
                # Führe Skill aus
                result = self.execute_skill(skill_name, step_inputs)
                
                # Speichere Outputs im Kontext
                context.variables[f"step_{step['step_number']}_output"] = result
                context.outputs.update(result)
                
                context.execution_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'event': 'step_completed',
                    'step': step['step_number'],
                    'skill': skill_name,
                    'result': result
                })
                
            except Exception as e:
                context.execution_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'event': 'step_failed',
                    'step': step['step_number'],
                    'skill': skill_name,
                    'error': str(e)
                })
                # Bei Fehler: versuche Alternative
                for alt_skill in step.get('alternatives', []):
                    try:
                        skill = self.registry.get_by_name(alt_skill)
                        step_inputs = self._prepare_step_inputs(skill, context)
                        result = self.execute_skill(alt_skill, step_inputs)
                        context.variables[f"step_{step['step_number']}_output"] = result
                        context.outputs.update(result)
                        break
                    except:
                        continue
        
        context.status = "completed"
        context.completed_at = datetime.now()
        return context
    
    def _validate_inputs(self, skill: Dict, inputs: Dict[str, Any]):
        """Validiert die Inputs gegen das Skill-Interface."""
        interface = skill.get('interface', {})
        
        for param in interface.get('inputs', []):
            if param.get('required', True) and param['name'] not in inputs:
                if 'default' not in param:
                    raise ValueError(f"Pflicht-Input '{param['name']}' fehlt für Skill '{skill['name']}'")
    
    def _execute_python_skill(self, skill: Dict, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Führt einen Python-Skill aus."""
        manifest_dir = os.path.dirname(skill['manifest_path'])
        entrypoint = skill.get('entrypoint', 'main.py')
        module_path = os.path.join(manifest_dir, entrypoint)
        
        if not os.path.exists(module_path):
            raise FileNotFoundError(f"Entrypoint nicht gefunden: {module_path}")
        
        # Dynamisches Laden des Moduls
        spec = importlib.util.spec_from_file_location(skill['name'], module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Suche nach execute-Funktion
        if hasattr(module, 'execute'):
            return module.execute(**inputs)
        elif hasattr(module, 'main'):
            return module.main(**inputs)
        else:
            raise AttributeError(f"Skill '{skill['name']}' hat keine execute() oder main() Funktion")
    
    def _execute_prompt_skill(self, skill: Dict, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Führt einen Prompt-basierten Skill aus."""
        manifest_dir = os.path.dirname(skill['manifest_path'])
        
        # Lade Manifest für Prompt-Template
        with open(skill['manifest_path'], 'r') as f:
            manifest = json.load(f)
        
        prompt_file = manifest.get('implementation', {}).get('prompt_template', 'prompt.txt')
        prompt_path = os.path.join(manifest_dir, prompt_file)
        
        with open(prompt_path, 'r') as f:
            prompt_template = f.read()
        
        # Ersetze Platzhalter
        prompt = prompt_template
        for key, value in inputs.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
        
        # Hier würde normalerweise ein LLM aufgerufen werden
        # Für die Demo geben wir das formatierte Prompt zurück
        return {
            'prompt': prompt,
            'note': 'Prompt-Skill bereit zur Ausführung mit LLM'
        }
    
    def _execute_shell_skill(self, skill: Dict, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Führt einen Shell-Skill aus."""
        manifest_dir = os.path.dirname(skill['manifest_path'])
        entrypoint = skill.get('entrypoint', 'run.sh')
        script_path = os.path.join(manifest_dir, entrypoint)
        
        # Bereite Umgebungsvariablen vor
        env = os.environ.copy()
        for key, value in inputs.items():
            env[f"INPUT_{key.upper()}"] = str(value)
        
        # Führe Script aus
        result = subprocess.run(
            ['bash', script_path],
            capture_output=True,
            text=True,
            env=env,
            cwd=manifest_dir
        )
        
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    
    def _execute_sequential(self, agent: Dict, context: ExecutionContext, orchestration: Dict):
        """Führt Schritte sequentiell aus."""
        steps = orchestration.get('steps', [])
        
        for i, step in enumerate(steps):
            skill_name = step['skill']
            input_mapping = step.get('input_mapping', {})
            output_mapping = step.get('output_mapping', {})
            
            # Bereite Inputs vor
            step_inputs = {}
            for skill_input, source in input_mapping.items():
                if source.startswith('$'):
                    # Variable aus Kontext
                    var_name = source[1:]
                    step_inputs[skill_input] = context.variables.get(var_name, context.inputs.get(var_name))
                else:
                    step_inputs[skill_input] = source
            
            # Führe Skill aus
            result = self.execute_skill(skill_name, step_inputs)
            
            # Speichere Outputs
            for skill_output, target in output_mapping.items():
                if target.startswith('$'):
                    context.variables[target[1:]] = result.get(skill_output)
                else:
                    context.outputs[target] = result.get(skill_output)
            
            context.execution_log.append({
                'timestamp': datetime.now().isoformat(),
                'event': 'step_completed',
                'step': i + 1,
                'skill': skill_name,
                'inputs': step_inputs,
                'outputs': result
            })
    
    def _execute_parallel(self, agent: Dict, context: ExecutionContext, orchestration: Dict):
        """Führt unabhängige Schritte parallel aus."""
        # Vereinfachte Implementierung: sequentiell mit Markierung
        # Für echte Parallelität würde man asyncio oder threading nutzen
        self._execute_sequential(agent, context, orchestration)
    
    def _execute_conditional(self, agent: Dict, context: ExecutionContext, orchestration: Dict):
        """Führt Schritte bedingt aus."""
        steps = orchestration.get('steps', [])
        
        for i, step in enumerate(steps):
            condition = step.get('condition')
            
            if condition:
                # Evaluiere Bedingung (vereinfacht)
                try:
                    # Ersetze Variablen in Bedingung
                    eval_condition = condition
                    for var_name, var_value in context.variables.items():
                        eval_condition = eval_condition.replace(f"${var_name}", repr(var_value))
                    
                    if not eval(eval_condition):
                        context.execution_log.append({
                            'timestamp': datetime.now().isoformat(),
                            'event': 'step_skipped',
                            'step': i + 1,
                            'reason': f"Bedingung nicht erfüllt: {condition}"
                        })
                        continue
                except Exception as e:
                    context.execution_log.append({
                        'timestamp': datetime.now().isoformat(),
                        'event': 'condition_error',
                        'step': i + 1,
                        'error': str(e)
                    })
                    continue
            
            # Führe Schritt aus (wie sequential)
            skill_name = step['skill']
            input_mapping = step.get('input_mapping', {})
            output_mapping = step.get('output_mapping', {})
            
            step_inputs = {}
            for skill_input, source in input_mapping.items():
                if source.startswith('$'):
                    var_name = source[1:]
                    step_inputs[skill_input] = context.variables.get(var_name, context.inputs.get(var_name))
                else:
                    step_inputs[skill_input] = source
            
            result = self.execute_skill(skill_name, step_inputs)
            
            for skill_output, target in output_mapping.items():
                if target.startswith('$'):
                    context.variables[target[1:]] = result.get(skill_output)
                else:
                    context.outputs[target] = result.get(skill_output)
    
    def _execute_dynamic(self, agent: Dict, context: ExecutionContext, orchestration: Dict):
        """Dynamische Orchestrierung basierend auf Ziel."""
        goal = orchestration.get('goal_description', '')
        
        # Nutze Discovery für dynamische Planung
        composition = self.discovery.suggest_composition(goal)
        
        context.execution_log.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'dynamic_plan_created',
            'composition': composition
        })
        
        # Führe geplante Schritte aus
        for step in composition['steps']:
            skill_name = step['suggested_skill']
            skill = self.registry.get_by_name(skill_name)
            
            if skill:
                step_inputs = self._prepare_step_inputs(skill, context)
                try:
                    result = self.execute_skill(skill_name, step_inputs)
                    context.outputs.update(result)
                    context.variables[f"step_{step['step_number']}_output"] = result
                except Exception as e:
                    context.execution_log.append({
                        'timestamp': datetime.now().isoformat(),
                        'event': 'dynamic_step_failed',
                        'skill': skill_name,
                        'error': str(e)
                    })
    
    def _prepare_step_inputs(self, skill: Dict, context: ExecutionContext) -> Dict[str, Any]:
        """Bereitet Inputs für einen Skill basierend auf dem Kontext vor."""
        step_inputs = {}
        interface = skill.get('interface', {})
        
        for param in interface.get('inputs', []):
            param_name = param['name']
            
            # Suche in verschiedenen Quellen
            if param_name in context.inputs:
                step_inputs[param_name] = context.inputs[param_name]
            elif param_name in context.variables:
                step_inputs[param_name] = context.variables[param_name]
            elif param_name in context.outputs:
                step_inputs[param_name] = context.outputs[param_name]
            elif 'default' in param:
                step_inputs[param_name] = param['default']
        
        return step_inputs


# CLI-Interface
if __name__ == "__main__":
    orchestrator = Orchestrator()
    
    if len(sys.argv) > 2:
        command = sys.argv[1]
        
        if command == "skill":
            skill_name = sys.argv[2]
            inputs = {}
            if len(sys.argv) > 3:
                inputs = json.loads(sys.argv[3])
            
            result = orchestrator.execute_skill(skill_name, inputs)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif command == "agent":
            agent_name = sys.argv[2]
            inputs = {}
            if len(sys.argv) > 3:
                inputs = json.loads(sys.argv[3])
            
            context = orchestrator.execute_agent(agent_name, inputs)
            print(f"Status: {context.status}")
            print(f"Outputs: {json.dumps(context.outputs, indent=2, ensure_ascii=False)}")
        
        elif command == "task":
            task = " ".join(sys.argv[2:])
            context = orchestrator.execute_task(task)
            print(f"Status: {context.status}")
            print(f"Outputs: {json.dumps(context.outputs, indent=2, ensure_ascii=False)}")
    else:
        print("Verwendung:")
        print("  orchestrator.py skill <skill_name> [inputs_json]")
        print("  orchestrator.py agent <agent_name> [inputs_json]")
        print("  orchestrator.py task <task_description>")
