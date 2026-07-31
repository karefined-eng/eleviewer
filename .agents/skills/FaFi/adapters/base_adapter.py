"""
Base Adapter
============
Abstrakte Basisklasse für alle Plattform-Adapter.
Definiert die gemeinsame Schnittstelle für die Integration mit verschiedenen KI-Tools.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from registry.registry import SkillAgentRegistry
from orchestrator.orchestrator import Orchestrator
from orchestrator.discovery import DiscoveryService


class BaseAdapter(ABC):
    """
    Abstrakte Basisklasse für Plattform-Adapter.
    Jeder Adapter ermöglicht die Integration des Skill-Hubs mit einer spezifischen KI-Plattform.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialisiert den Adapter.
        
        Args:
            config: Plattform-spezifische Konfiguration
        """
        self.config = config or {}
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.registry = SkillAgentRegistry(
            db_path=os.path.join(self.base_path, 'registry', 'registry.db'),
            base_path=self.base_path
        )
        self.orchestrator = Orchestrator(self.registry, self.base_path)
        self.discovery = DiscoveryService(self.registry)
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Name der Plattform."""
        pass
    
    @abstractmethod
    def format_skill_definition(self, skill: Dict) -> str:
        """
        Formatiert eine Skill-Definition für die spezifische Plattform.
        
        Args:
            skill: Skill-Dictionary aus der Registry
            
        Returns:
            Plattform-spezifisches Format (z.B. Tool-Definition, Function-Schema)
        """
        pass
    
    @abstractmethod
    def format_agent_definition(self, agent: Dict) -> str:
        """
        Formatiert eine Agent-Definition für die spezifische Plattform.
        
        Args:
            agent: Agent-Dictionary aus der Registry
            
        Returns:
            Plattform-spezifisches Format
        """
        pass
    
    def get_all_skills(self) -> List[Dict]:
        """Gibt alle verfügbaren Skills zurück."""
        return self.registry.list_all('skill')
    
    def get_all_agents(self) -> List[Dict]:
        """Gibt alle verfügbaren Agents zurück."""
        return self.registry.list_all('agent')
    
    def search_skills(self, query: str) -> List[Dict]:
        """Sucht nach Skills basierend auf einer Beschreibung."""
        results = self.discovery.discover(query, entity_type='skill')
        return [r.entity for r in results]
    
    def search_agents(self, query: str) -> List[Dict]:
        """Sucht nach Agents basierend auf einer Beschreibung."""
        results = self.discovery.discover(query, entity_type='agent')
        return [r.entity for r in results]
    
    def execute_skill(self, skill_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Führt einen Skill aus."""
        return self.orchestrator.execute_skill(skill_name, inputs)
    
    def execute_agent(self, agent_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Führt einen Agent aus und gibt die Ergebnisse zurück."""
        context = self.orchestrator.execute_agent(agent_name, inputs)
        return {
            'status': context.status,
            'outputs': context.outputs,
            'execution_log': context.execution_log
        }
    
    def get_catalog_for_platform(self) -> str:
        """
        Generiert einen vollständigen Katalog aller Skills und Agents
        im Format der spezifischen Plattform.
        
        Returns:
            Formatierter Katalog-String
        """
        skills = self.get_all_skills()
        agents = self.get_all_agents()
        
        formatted_skills = [self.format_skill_definition(s) for s in skills]
        formatted_agents = [self.format_agent_definition(a) for a in agents]
        
        return self._build_catalog(formatted_skills, formatted_agents)
    
    @abstractmethod
    def _build_catalog(self, skills: List[str], agents: List[str]) -> str:
        """Baut den plattform-spezifischen Katalog zusammen."""
        pass
    
    def generate_system_prompt_extension(self) -> str:
        """
        Generiert eine Erweiterung für den System-Prompt,
        die alle verfügbaren Skills und Agents beschreibt.
        """
        catalog = self.get_catalog_for_platform()
        
        return f"""
## Verfügbare Skills und Agents aus dem Skill-Hub

Die folgenden Skills und Agents stehen zur Verfügung und können bei Bedarf aufgerufen werden:

{catalog}

### Verwendung

Um einen Skill oder Agent zu nutzen, verwende die entsprechende Funktion/Tool-Definition.
Bei Unsicherheit, welcher Skill passend ist, beschreibe die Aufgabe und nutze die Discovery-Funktion.
"""
    
    def refresh_registry(self):
        """Aktualisiert die Registry durch erneutes Scannen."""
        return self.registry.scan_and_register()
