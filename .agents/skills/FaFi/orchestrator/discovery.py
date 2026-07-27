"""
Discovery Service
=================
Intelligente Suche nach passenden Skills und Agents basierend auf
natürlichsprachlichen Anforderungen und semantischer Ähnlichkeit.
"""

import json
import os
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# Füge Registry zum Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from registry.registry import SkillAgentRegistry


@dataclass
class DiscoveryResult:
    """Ergebnis einer Discovery-Suche."""
    entity: Dict
    relevance_score: float
    match_reasons: List[str] = field(default_factory=list)


class DiscoveryService:
    """
    Service zur intelligenten Suche nach Skills und Agents.
    Kombiniert Keyword-Matching mit semantischer Analyse.
    """
    
    # Mapping von natürlichsprachlichen Begriffen zu Capabilities
    CAPABILITY_SYNONYMS = {
        # Text-Verarbeitung
        'zusammenfassen': ['text_summary', 'summarize', 'nlp'],
        'übersetzen': ['translate', 'translation', 'language'],
        'schreiben': ['text_generation', 'write', 'content'],
        'analysieren': ['analysis', 'analyze', 'nlp'],
        
        # Daten
        'daten': ['data', 'database', 'storage'],
        'speichern': ['save', 'store', 'persistence'],
        'lesen': ['read', 'fetch', 'retrieve'],
        'suchen': ['search', 'find', 'query'],
        
        # Kommunikation
        'email': ['email', 'mail', 'messaging'],
        'nachricht': ['message', 'notification', 'communication'],
        'senden': ['send', 'transmit', 'deliver'],
        
        # Dateien
        'datei': ['file', 'document', 'io'],
        'pdf': ['pdf', 'document', 'export'],
        'bild': ['image', 'picture', 'visual'],
        
        # Web
        'web': ['web', 'http', 'api'],
        'scraping': ['scrape', 'crawl', 'extract'],
        'api': ['api', 'rest', 'integration'],
        
        # Code
        'code': ['code', 'programming', 'development'],
        'ausführen': ['execute', 'run', 'shell'],
        'python': ['python', 'scripting'],
    }
    
    # Mapping von Input/Output-Anforderungen
    TYPE_KEYWORDS = {
        'text': ['text', 'string', 'inhalt', 'content'],
        'number': ['zahl', 'nummer', 'anzahl', 'count'],
        'file': ['datei', 'file', 'dokument', 'document'],
        'array': ['liste', 'list', 'mehrere', 'multiple'],
        'object': ['objekt', 'daten', 'struktur'],
        'boolean': ['ja/nein', 'wahr/falsch', 'flag'],
    }
    
    def __init__(self, registry: SkillAgentRegistry = None):
        """
        Initialisiert den Discovery Service.
        
        Args:
            registry: Bestehende Registry-Instanz oder None für neue
        """
        self.registry = registry or SkillAgentRegistry()
    
    def discover(self, 
                 task_description: str,
                 required_inputs: List[str] = None,
                 required_outputs: List[str] = None,
                 entity_type: str = None,
                 limit: int = 10) -> List[DiscoveryResult]:
        """
        Findet passende Skills/Agents für eine Aufgabenbeschreibung.
        
        Args:
            task_description: Natürlichsprachliche Beschreibung der Aufgabe
            required_inputs: Liste von benötigten Input-Typen
            required_outputs: Liste von benötigten Output-Typen
            entity_type: 'skill' oder 'agent' oder None für beide
            limit: Maximale Anzahl Ergebnisse
            
        Returns:
            Liste von DiscoveryResults, sortiert nach Relevanz
        """
        # Extrahiere Keywords und Capabilities aus der Beschreibung
        keywords = self._extract_keywords(task_description.lower())
        inferred_capabilities = self._infer_capabilities(task_description.lower())
        inferred_types = self._infer_types(task_description.lower())
        
        # Kombiniere mit expliziten Anforderungen
        if required_inputs:
            inferred_types['inputs'].update(required_inputs)
        if required_outputs:
            inferred_types['outputs'].update(required_outputs)
        
        # Hole alle Entities aus der Registry
        all_entities = self.registry.list_all(entity_type)
        
        # Bewerte jede Entity
        results = []
        for entity in all_entities:
            score, reasons = self._calculate_relevance(
                entity, keywords, inferred_capabilities, inferred_types
            )
            if score > 0:
                results.append(DiscoveryResult(
                    entity=entity,
                    relevance_score=score,
                    match_reasons=reasons
                ))
        
        # Sortiere nach Relevanz und limitiere
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]
    
    def find_chain(self, 
                   input_type: str, 
                   output_type: str,
                   max_depth: int = 3) -> List[List[Dict]]:
        """
        Findet Ketten von Skills, die einen Input-Typ in einen Output-Typ transformieren.
        
        Args:
            input_type: Verfügbarer Input-Typ
            output_type: Gewünschter Output-Typ
            max_depth: Maximale Kettenlänge
            
        Returns:
            Liste von möglichen Skill-Ketten
        """
        chains = []
        self._find_chain_recursive(input_type, output_type, [], chains, max_depth)
        return chains
    
    def _find_chain_recursive(self, 
                               current_type: str,
                               target_type: str,
                               current_chain: List[Dict],
                               all_chains: List[List[Dict]],
                               remaining_depth: int):
        """Rekursive Hilfsfunktion für Kettensuche."""
        if remaining_depth <= 0:
            return
        
        # Finde Skills, die den aktuellen Typ als Input akzeptieren
        candidates = self.registry.search(input_types=[current_type], entity_type='skill')
        
        for candidate in candidates:
            if candidate in current_chain:
                continue  # Vermeide Zyklen
            
            new_chain = current_chain + [candidate]
            
            # Prüfe Output-Typen
            output_types = [p['type'] for p in candidate['interface']['outputs']]
            
            if target_type in output_types:
                all_chains.append(new_chain)
            else:
                # Rekursiv weitersuchen
                for out_type in output_types:
                    self._find_chain_recursive(
                        out_type, target_type, new_chain, all_chains, remaining_depth - 1
                    )
    
    def suggest_composition(self, task_description: str) -> Dict:
        """
        Schlägt eine Komposition von Skills für eine komplexe Aufgabe vor.
        
        Args:
            task_description: Beschreibung der Aufgabe
            
        Returns:
            Vorgeschlagene Komposition mit Skills und Verbindungen
        """
        # Zerlege Aufgabe in Teilschritte (vereinfachte Heuristik)
        steps = self._decompose_task(task_description)
        
        composition = {
            'task': task_description,
            'steps': [],
            'connections': []
        }
        
        previous_outputs = set()
        
        for i, step in enumerate(steps):
            # Finde passende Skills für diesen Schritt
            results = self.discover(step, limit=3)
            
            if results:
                best_match = results[0]
                step_info = {
                    'step_number': i + 1,
                    'description': step,
                    'suggested_skill': best_match.entity['name'],
                    'confidence': best_match.relevance_score,
                    'alternatives': [r.entity['name'] for r in results[1:]]
                }
                composition['steps'].append(step_info)
                
                # Verbindungen zu vorherigen Schritten
                skill_inputs = {p['type'] for p in best_match.entity['interface']['inputs']}
                matching_outputs = skill_inputs & previous_outputs
                
                if matching_outputs and i > 0:
                    composition['connections'].append({
                        'from_step': i,
                        'to_step': i + 1,
                        'data_types': list(matching_outputs)
                    })
                
                # Aktualisiere verfügbare Outputs
                for p in best_match.entity['interface']['outputs']:
                    previous_outputs.add(p['type'])
        
        return composition
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrahiert relevante Keywords aus dem Text."""
        # Einfache Tokenisierung und Filterung
        stopwords = {'der', 'die', 'das', 'ein', 'eine', 'und', 'oder', 'für', 
                     'mit', 'von', 'zu', 'in', 'auf', 'an', 'ist', 'sind', 'wird',
                     'werden', 'soll', 'sollen', 'kann', 'können', 'muss', 'müssen',
                     'ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr', 'the', 'a', 'an',
                     'and', 'or', 'for', 'with', 'to', 'in', 'on', 'is', 'are'}
        
        words = text.replace(',', ' ').replace('.', ' ').replace('?', ' ').split()
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        return keywords
    
    def _infer_capabilities(self, text: str) -> List[str]:
        """Inferiert benötigte Capabilities aus dem Text."""
        capabilities = set()
        
        for keyword, caps in self.CAPABILITY_SYNONYMS.items():
            if keyword in text:
                capabilities.update(caps)
        
        return list(capabilities)
    
    def _infer_types(self, text: str) -> Dict[str, set]:
        """Inferiert benötigte Input/Output-Typen aus dem Text."""
        types = {'inputs': set(), 'outputs': set()}
        
        for type_name, keywords in self.TYPE_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    # Vereinfachte Heuristik: füge zu beiden hinzu
                    types['inputs'].add(type_name)
                    types['outputs'].add(type_name)
                    break
        
        return types
    
    def _calculate_relevance(self,
                             entity: Dict,
                             keywords: List[str],
                             capabilities: List[str],
                             required_types: Dict[str, set]) -> Tuple[float, List[str]]:
        """
        Berechnet Relevanz-Score für eine Entity.
        
        Returns:
            Tuple von (Score, Liste von Match-Gründen)
        """
        score = 0.0
        reasons = []
        
        # Keyword-Matching in Name und Beschreibung
        entity_text = f"{entity['name']} {entity.get('description', '')}".lower()
        keyword_matches = sum(1 for kw in keywords if kw in entity_text)
        if keyword_matches > 0:
            score += keyword_matches * 0.2
            reasons.append(f"Keyword-Match: {keyword_matches} Treffer")
        
        # Tag-Matching
        entity_tags = set(entity.get('tags', []))
        tag_matches = len(entity_tags & set(keywords))
        if tag_matches > 0:
            score += tag_matches * 0.3
            reasons.append(f"Tag-Match: {tag_matches} Tags")
        
        # Capability-Matching
        entity_caps = set(entity.get('capabilities', []))
        cap_matches = len(entity_caps & set(capabilities))
        if cap_matches > 0:
            score += cap_matches * 0.4
            reasons.append(f"Capability-Match: {cap_matches} Fähigkeiten")
        
        # Interface-Matching
        interface = entity.get('interface', {})
        input_types = {p['type'] for p in interface.get('inputs', [])}
        output_types = {p['type'] for p in interface.get('outputs', [])}
        
        input_matches = len(input_types & required_types.get('inputs', set()))
        output_matches = len(output_types & required_types.get('outputs', set()))
        
        if input_matches > 0:
            score += input_matches * 0.15
            reasons.append(f"Input-Match: {input_matches} Typen")
        
        if output_matches > 0:
            score += output_matches * 0.15
            reasons.append(f"Output-Match: {output_matches} Typen")
        
        return score, reasons
    
    def _decompose_task(self, task_description: str) -> List[str]:
        """
        Zerlegt eine komplexe Aufgabe in Teilschritte.
        Vereinfachte Implementierung - kann durch LLM ersetzt werden.
        """
        # Suche nach Aufzählungen oder Schritten
        steps = []
        
        # Trenne bei "dann", "danach", "anschließend", etc.
        separators = ['dann', 'danach', 'anschließend', 'und dann', 'schließlich',
                      'then', 'after that', 'finally', 'next']
        
        current = task_description
        for sep in separators:
            if sep in current.lower():
                parts = current.lower().split(sep)
                steps.extend([p.strip() for p in parts if p.strip()])
                current = ""
                break
        
        if not steps:
            # Keine expliziten Schritte gefunden, behandle als einzelne Aufgabe
            steps = [task_description]
        
        return steps


# CLI-Interface
if __name__ == "__main__":
    discovery = DiscoveryService()
    
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
        print(f"Suche nach Skills für: {task}\n")
        
        results = discovery.discover(task)
        
        if results:
            print("Gefundene Skills/Agents:")
            print("-" * 50)
            for r in results:
                print(f"\n{r.entity['name']} (Score: {r.relevance_score:.2f})")
                print(f"  Typ: {r.entity['type']}")
                print(f"  Beschreibung: {r.entity.get('description', 'N/A')}")
                print(f"  Gründe: {', '.join(r.match_reasons)}")
        else:
            print("Keine passenden Skills/Agents gefunden.")
    else:
        print("Verwendung: discovery.py <Aufgabenbeschreibung>")
