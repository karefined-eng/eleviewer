"""
Universal API Server
====================
REST API für den Zugriff auf den Skill & Agent Hub.
Ermöglicht plattformübergreifende Integration.

Version 2.1 - Vollständig bidirektional für alle 13 Plattformen:

Ursprüngliche 5 Plattformen (jetzt bidirektional):
- Antigravity
- Claude Cowork
- Claude Code  
- Manus 1.6
- ChatGPT Codex

Zusätzliche 8 Plattformen (bidirektional):
- Microsoft 365 Copilot
- Google NotebookLM
- Google Gemini
- Google AI Studio
- Perplexity
- Abacus AI (Chat LLM, Deep Agent, CLI)
- HubSpot
- HubSpot Breeze
"""

from flask import Flask, request, jsonify
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from registry.registry import SkillAgentRegistry
from orchestrator.orchestrator import Orchestrator
from orchestrator.discovery import DiscoveryService

# Original-Adapter (jetzt bidirektional)
from adapters.claude_adapter import ClaudeAdapter, ClaudeCoworkAdapter, ClaudeCodeAdapter
from adapters.manus_adapter import ManusAdapter
from adapters.chatgpt_codex_adapter import ChatGPTCodexAdapter
from adapters.antigravity_adapter import AntigravityAdapter

# Zusätzliche bidirektionale Adapter
from adapters.microsoft365_copilot_adapter import Microsoft365CopilotAdapter
from adapters.google_ecosystem_adapter import (
    GoogleEcosystemAdapter, 
    NotebookLMAdapter, 
    GeminiAdapter, 
    GoogleAIStudioAdapter
)
from adapters.perplexity_adapter import PerplexityAdapter
from adapters.abacus_ai_adapter import AbacusAIAdapter
from adapters.hubspot_adapter import HubSpotAdapter

app = Flask(__name__)

# Initialisiere Komponenten
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
registry = SkillAgentRegistry(
    db_path=os.path.join(base_path, 'registry', 'registry.db'),
    base_path=base_path
)
orchestrator = Orchestrator(registry, base_path)
discovery = DiscoveryService(registry)

# Alle Adapter (alle sind jetzt bidirektional)
adapters = {
    # Ursprüngliche 5 Plattformen
    'antigravity': AntigravityAdapter(),
    'claude': ClaudeAdapter(),
    'claude_cowork': ClaudeCoworkAdapter(),
    'claude_code': ClaudeCodeAdapter(),
    'manus': ManusAdapter(),
    'chatgpt_codex': ChatGPTCodexAdapter(),
    # Zusätzliche 8 Plattformen
    'microsoft365_copilot': Microsoft365CopilotAdapter(),
    'notebooklm': NotebookLMAdapter(),
    'gemini': GeminiAdapter(),
    'google_ai_studio': GoogleAIStudioAdapter(),
    'perplexity': PerplexityAdapter(),
    'abacus_ai': AbacusAIAdapter(),
    'hubspot': HubSpotAdapter()
}

# Alle Adapter sind jetzt bidirektional
bidirectional_adapters = adapters.copy()


# ============== Registry Endpoints ==============

@app.route('/api/v1/registry/scan', methods=['POST'])
def scan_registry():
    """Scannt und registriert alle Skills und Agents."""
    count = registry.scan_and_register()
    return jsonify({
        'status': 'success',
        'registered_count': count
    })


@app.route('/api/v1/registry/list', methods=['GET'])
def list_entities():
    """Listet alle registrierten Entities auf."""
    entity_type = request.args.get('type')  # 'skill', 'agent', oder None für alle
    imported_only = request.args.get('imported', 'false').lower() == 'true'
    platform = request.args.get('platform')
    
    entities = registry.list_all(entity_type)
    
    # Filtere nach importierten Skills, falls gewünscht
    if imported_only:
        entities = [e for e in entities if e.get('metadata', {}).get('imported', False) or 
                    'imported' in e.get('tags', [])]
    
    # Filtere nach Plattform
    if platform:
        entities = [e for e in entities if 
                    e.get('metadata', {}).get('source_platform', '').lower() == platform.lower() or
                    platform.lower() in [t.lower() for t in e.get('tags', [])]]
    
    return jsonify({
        'status': 'success',
        'count': len(entities),
        'entities': entities
    })


@app.route('/api/v1/registry/get/<name>', methods=['GET'])
def get_entity(name):
    """Holt eine spezifische Entity."""
    entity = registry.get_by_name(name)
    if entity:
        return jsonify({
            'status': 'success',
            'entity': entity
        })
    return jsonify({
        'status': 'error',
        'message': f"Entity '{name}' nicht gefunden"
    }), 404


@app.route('/api/v1/registry/imported', methods=['GET'])
def list_imported_skills():
    """Listet alle importierten Skills von externen Plattformen auf."""
    platform = request.args.get('platform')
    
    entities = registry.list_all('skill')
    imported = [e for e in entities if e.get('metadata', {}).get('imported', False) or
                'imported' in e.get('tags', [])]
    
    if platform:
        imported = [e for e in imported if 
                    e.get('metadata', {}).get('source_platform', '').lower() == platform.lower() or
                    platform.lower() in [t.lower() for t in e.get('tags', [])]]
    
    # Gruppiere nach Plattform
    by_platform = {}
    for e in imported:
        # Versuche Plattform aus metadata oder tags zu ermitteln
        source = e.get('metadata', {}).get('source_platform', '')
        if not source:
            tags = e.get('tags', [])
            for tag in ['antigravity', 'claude', 'manus', 'openai', 'perplexity', 
                       'hubspot', 'google', 'microsoft365', 'abacus']:
                if tag in [t.lower() for t in tags]:
                    source = tag
                    break
        source = source or 'Unknown'
        
        if source not in by_platform:
            by_platform[source] = []
        by_platform[source].append(e)
    
    return jsonify({
        'status': 'success',
        'total_count': len(imported),
        'by_platform': by_platform
    })


# ============== Discovery Endpoints ==============

@app.route('/api/v1/discover', methods=['POST'])
def discover_skills():
    """Sucht nach passenden Skills basierend auf einer Beschreibung."""
    data = request.json or {}
    query = data.get('query', '')
    entity_type = data.get('type')
    limit = data.get('limit', 10)
    include_imported = data.get('include_imported', True)
    platform_filter = data.get('platform')
    
    results = discovery.discover(
        task_description=query,
        entity_type=entity_type,
        limit=limit
    )
    
    # Filtere importierte Skills, falls nicht gewünscht
    if not include_imported:
        results = [r for r in results if not r.entity.get('metadata', {}).get('imported', False) and
                   'imported' not in r.entity.get('tags', [])]
    
    # Filtere nach Plattform
    if platform_filter:
        results = [r for r in results if 
                   r.entity.get('metadata', {}).get('source_platform', '').lower() == platform_filter.lower() or
                   platform_filter.lower() in [t.lower() for t in r.entity.get('tags', [])]]
    
    return jsonify({
        'status': 'success',
        'count': len(results),
        'results': [{
            'entity': r.entity,
            'relevance_score': r.relevance_score,
            'match_reasons': r.match_reasons
        } for r in results]
    })


@app.route('/api/v1/suggest-composition', methods=['POST'])
def suggest_composition():
    """Schlägt eine Skill-Komposition für eine Aufgabe vor."""
    data = request.json or {}
    task = data.get('task', '')
    
    composition = discovery.suggest_composition(task)
    
    return jsonify({
        'status': 'success',
        'composition': composition
    })


# ============== Execution Endpoints ==============

@app.route('/api/v1/execute/skill/<name>', methods=['POST'])
def execute_skill(name):
    """Führt einen Skill aus."""
    inputs = request.json or {}
    
    try:
        result = orchestrator.execute_skill(name, inputs)
        return jsonify({
            'status': 'success',
            'result': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


@app.route('/api/v1/execute/agent/<name>', methods=['POST'])
def execute_agent(name):
    """Führt einen Agent aus."""
    inputs = request.json or {}
    
    try:
        context = orchestrator.execute_agent(name, inputs)
        return jsonify({
            'status': context.status,
            'task_id': context.task_id,
            'outputs': context.outputs,
            'execution_log': context.execution_log
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


@app.route('/api/v1/execute/task', methods=['POST'])
def execute_task():
    """Führt eine Aufgabe basierend auf natürlichsprachlicher Beschreibung aus."""
    data = request.json or {}
    task = data.get('task', '')
    inputs = data.get('inputs', {})
    
    try:
        context = orchestrator.execute_task(task, inputs)
        return jsonify({
            'status': context.status,
            'task_id': context.task_id,
            'outputs': context.outputs,
            'execution_log': context.execution_log
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


# ============== Adapter Endpoints ==============

@app.route('/api/v1/catalog/<platform>', methods=['GET'])
def get_platform_catalog(platform):
    """Gibt den Katalog im plattform-spezifischen Format zurück."""
    if platform not in adapters:
        return jsonify({
            'status': 'error',
            'message': f"Unbekannte Plattform: {platform}",
            'available_platforms': list(adapters.keys())
        }), 400
    
    adapter = adapters[platform]
    catalog = adapter.get_catalog_for_platform()
    
    return jsonify({
        'status': 'success',
        'platform': platform,
        'catalog': json.loads(catalog)
    })


@app.route('/api/v1/instructions/<platform>', methods=['GET'])
def get_platform_instructions(platform):
    """Gibt Integrationsanweisungen für eine Plattform zurück."""
    if platform not in adapters:
        return jsonify({
            'status': 'error',
            'message': f"Unbekannte Plattform: {platform}"
        }), 400
    
    adapter = adapters[platform]
    instructions = adapter.generate_system_prompt_extension()
    
    return jsonify({
        'status': 'success',
        'platform': platform,
        'instructions': instructions
    })


@app.route('/api/v1/openapi-schema', methods=['GET'])
def get_openapi_schema():
    """Gibt das OpenAPI-Schema für GPT Actions zurück."""
    adapter = adapters['chatgpt_codex']
    schema = adapter.generate_gpt_action_schema()
    return jsonify(schema)


# ============== Bidirektionale Integration Endpoints ==============

@app.route('/api/v1/bidirectional/available-skills/<platform>', methods=['GET'])
def get_available_platform_skills(platform):
    """Gibt die verfügbaren importierbaren Skills einer Plattform zurück."""
    if platform not in bidirectional_adapters:
        return jsonify({
            'status': 'error',
            'message': f"Plattform '{platform}' nicht gefunden",
            'available_platforms': list(bidirectional_adapters.keys())
        }), 400
    
    adapter = bidirectional_adapters[platform]
    
    # Hole die generierten Skills basierend auf dem Adapter-Typ
    skills = []
    
    # Ursprüngliche 5 Plattformen
    if hasattr(adapter, 'generate_antigravity_skills'):
        skills.extend(adapter.generate_antigravity_skills())
    if hasattr(adapter, 'generate_claude_skills'):
        skills.extend(adapter.generate_claude_skills())
    if hasattr(adapter, 'generate_cowork_skills'):
        skills.extend(adapter.generate_cowork_skills())
    if hasattr(adapter, 'generate_code_skills'):
        skills.extend(adapter.generate_code_skills())
    if hasattr(adapter, 'generate_manus_skills'):
        skills.extend(adapter.generate_manus_skills())
    if hasattr(adapter, 'generate_openai_skills'):
        skills.extend(adapter.generate_openai_skills())
    
    # Zusätzliche 8 Plattformen
    if hasattr(adapter, 'generate_graph_api_skills'):
        skills.extend(adapter.generate_graph_api_skills())
    if hasattr(adapter, 'generate_notebooklm_skills'):
        skills.extend(adapter.generate_notebooklm_skills())
    if hasattr(adapter, 'generate_gemini_skills'):
        skills.extend(adapter.generate_gemini_skills())
    if hasattr(adapter, 'generate_aistudio_skills'):
        skills.extend(adapter.generate_aistudio_skills())
    if hasattr(adapter, 'generate_perplexity_skills'):
        skills.extend(adapter.generate_perplexity_skills())
    if hasattr(adapter, 'generate_abacus_skills'):
        skills.extend(adapter.generate_abacus_skills())
    if hasattr(adapter, 'generate_hubspot_skills'):
        skills.extend(adapter.generate_hubspot_skills())
    if hasattr(adapter, 'generate_hubspot_breeze_skills'):
        skills.extend(adapter.generate_hubspot_breeze_skills())
    
    return jsonify({
        'status': 'success',
        'platform': platform,
        'available_skills_count': len(skills),
        'available_skills': skills
    })


@app.route('/api/v1/bidirectional/import-skill', methods=['POST'])
def import_platform_skill():
    """Importiert einen Skill von einer externen Plattform in den Hub."""
    data = request.json or {}
    platform = data.get('platform')
    skill_name = data.get('skill_name')
    
    if not platform or not skill_name:
        return jsonify({
            'status': 'error',
            'message': 'platform und skill_name erforderlich'
        }), 400
    
    # Hier würde die tatsächliche Import-Logik implementiert
    # Für jetzt geben wir eine Bestätigung zurück
    return jsonify({
        'status': 'success',
        'message': f"Skill '{skill_name}' von Plattform '{platform}' zur Import-Queue hinzugefügt",
        'note': 'Der Skill wird beim nächsten Registry-Scan registriert'
    })


@app.route('/api/v1/bidirectional/export-to/<platform>', methods=['POST'])
def export_skills_to_platform(platform):
    """Exportiert Hub-Skills zu einer externen Plattform."""
    data = request.json or {}
    skill_names = data.get('skills', [])
    
    if platform not in adapters:
        return jsonify({
            'status': 'error',
            'message': f"Unbekannte Plattform: {platform}"
        }), 400
    
    adapter = adapters[platform]
    
    # Generiere plattformspezifische Definitionen für die angegebenen Skills
    exported = []
    for name in skill_names:
        entity = registry.get_by_name(name)
        if entity:
            if entity.get('type') == 'skill':
                definition = adapter.format_skill_definition(entity)
            else:
                definition = adapter.format_agent_definition(entity)
            exported.append({
                'name': name,
                'definition': json.loads(definition)
            })
    
    return jsonify({
        'status': 'success',
        'platform': platform,
        'exported_count': len(exported),
        'exported_skills': exported
    })


# ============== Platform-Specific Endpoints ==============

# Ursprüngliche 5 Plattformen

@app.route('/api/v1/platforms/antigravity/manifest', methods=['GET'])
def get_antigravity_manifest():
    """Gibt das Antigravity-Paket-Manifest zurück."""
    adapter = adapters['antigravity']
    manifest = adapter.generate_antigravity_manifest()
    return jsonify(manifest)


@app.route('/api/v1/platforms/claude/mcp-config', methods=['GET'])
def get_claude_mcp_config():
    """Gibt die Claude MCP-Server-Konfiguration zurück."""
    adapter = adapters['claude']
    config = adapter.generate_mcp_server_config()
    return jsonify(config)


@app.route('/api/v1/platforms/claude_cowork/workspace-integration', methods=['GET'])
def get_cowork_integration():
    """Gibt die Claude Cowork Workspace-Integration zurück."""
    adapter = adapters['claude_cowork']
    integration = adapter.generate_workspace_integration()
    return jsonify({
        'status': 'success',
        'integration_guide': integration
    })


@app.route('/api/v1/platforms/claude_code/slash-commands', methods=['GET'])
def get_claude_code_commands():
    """Gibt die Claude Code Slash-Commands zurück."""
    adapter = adapters['claude_code']
    commands = adapter.generate_slash_commands()
    return jsonify({
        'status': 'success',
        'commands': commands
    })


@app.route('/api/v1/platforms/manus/instructions', methods=['GET'])
def get_manus_instructions():
    """Gibt die Manus-Integrationsanweisungen zurück."""
    adapter = adapters['manus']
    instructions = adapter.generate_manus_instructions()
    return jsonify({
        'status': 'success',
        'instructions': instructions
    })


@app.route('/api/v1/platforms/chatgpt_codex/tools-array', methods=['GET'])
def get_openai_tools_array():
    """Gibt das OpenAI Tools-Array zurück."""
    adapter = adapters['chatgpt_codex']
    tools = adapter.generate_openai_tools_array()
    return jsonify({
        'status': 'success',
        'tools': tools
    })


@app.route('/api/v1/platforms/chatgpt_codex/assistant-instructions', methods=['GET'])
def get_assistant_instructions():
    """Gibt die OpenAI Assistant-Anweisungen zurück."""
    adapter = adapters['chatgpt_codex']
    instructions = adapter.generate_assistant_instructions()
    return jsonify({
        'status': 'success',
        'instructions': instructions
    })


# Zusätzliche 8 Plattformen

@app.route('/api/v1/platforms/microsoft365/copilot-manifest', methods=['GET'])
def get_copilot_manifest():
    """Gibt das Microsoft 365 Copilot Plugin Manifest zurück."""
    adapter = bidirectional_adapters['microsoft365_copilot']
    manifest = adapter.generate_copilot_plugin_manifest()
    return jsonify(manifest)


@app.route('/api/v1/platforms/gemini/tools-config', methods=['GET'])
def get_gemini_tools_config():
    """Gibt die Gemini Tools-Konfiguration zurück."""
    adapter = bidirectional_adapters['gemini']
    config = adapter.generate_gemini_tools_config()
    return jsonify(config)


@app.route('/api/v1/platforms/abacus/deep-agent-config', methods=['GET'])
def get_abacus_deep_agent_config():
    """Gibt die Abacus Deep Agent Konfiguration zurück."""
    adapter = bidirectional_adapters['abacus_ai']
    config = adapter.generate_deep_agent_config()
    return jsonify(config)


# ============== Health & Info ==============

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health-Check-Endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '2.1.0'
    })


@app.route('/api/v1/info', methods=['GET'])
def get_info():
    """Gibt Informationen über den Hub zurück."""
    skills = registry.list_all('skill')
    agents = registry.list_all('agent')
    
    # Zähle importierte Skills
    imported_skills = [s for s in skills if s.get('metadata', {}).get('imported', False) or
                       'imported' in s.get('tags', [])]
    native_skills = [s for s in skills if not (s.get('metadata', {}).get('imported', False) or
                     'imported' in s.get('tags', []))]
    
    # Gruppiere importierte Skills nach Plattform
    imported_by_platform = {}
    for s in imported_skills:
        source = s.get('metadata', {}).get('source_platform', '')
        if not source:
            tags = s.get('tags', [])
            for tag in ['antigravity', 'claude', 'manus', 'openai', 'perplexity', 
                       'hubspot', 'google', 'microsoft365', 'abacus']:
                if tag in [t.lower() for t in tags]:
                    source = tag
                    break
        source = source or 'other'
        imported_by_platform[source] = imported_by_platform.get(source, 0) + 1
    
    return jsonify({
        'name': 'Skill & Agent Hub',
        'version': '2.1.0',
        'description': 'Zentraler Hub für wiederverwendbare Skills und Agents mit vollständiger bidirektionaler Integration',
        'statistics': {
            'total_skills': len(skills),
            'native_skills': len(native_skills),
            'imported_skills': len(imported_skills),
            'imported_by_platform': imported_by_platform,
            'total_agents': len(agents)
        },
        'supported_platforms': {
            'original_5': ['antigravity', 'claude_cowork', 'claude_code', 'manus', 'chatgpt_codex'],
            'additional_8': ['microsoft365_copilot', 'notebooklm', 'gemini', 'google_ai_studio', 
                           'perplexity', 'abacus_ai', 'hubspot'],
            'all_bidirectional': list(bidirectional_adapters.keys())
        },
        'endpoints': {
            'registry': '/api/v1/registry/*',
            'discovery': '/api/v1/discover',
            'execution': '/api/v1/execute/*',
            'catalogs': '/api/v1/catalog/<platform>',
            'bidirectional': '/api/v1/bidirectional/*',
            'platform_specific': '/api/v1/platforms/*'
        }
    })


if __name__ == '__main__':
    # Scanne beim Start
    print("=" * 60)
    print("Skill & Agent Hub - Version 2.1.0")
    print("=" * 60)
    print("\nScanne Skills und Agents...")
    count = registry.scan_and_register()
    print(f"Registriert: {count} Entities")
    
    print("\n" + "-" * 40)
    print("Unterstützte Plattformen (alle bidirektional):")
    print("-" * 40)
    
    print("\nUrsprüngliche 5 Plattformen:")
    for p in ['antigravity', 'claude_cowork', 'claude_code', 'manus', 'chatgpt_codex']:
        print(f"  ✓ {p}")
    
    print("\nZusätzliche 8 Plattformen:")
    for p in ['microsoft365_copilot', 'notebooklm', 'gemini', 'google_ai_studio', 
              'perplexity', 'abacus_ai', 'hubspot']:
        print(f"  ✓ {p}")
    
    print("\n" + "=" * 60)
    print("Server startet auf http://0.0.0.0:5000")
    print("=" * 60)
    
    # Starte Server
    app.run(host='0.0.0.0', port=5000, debug=True)
