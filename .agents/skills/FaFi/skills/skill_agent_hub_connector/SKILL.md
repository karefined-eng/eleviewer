---
name: skill-agent-hub-connector
description: "Verbindet KI-Tools mit dem zentralen Skill & Agent Hub. Verwenden für: Registrierung neuer Skills, Discovery passender Fähigkeiten, Ausführung von Skills/Agents, bidirektionale Plattform-Integration. Unterstützt Antigravity, Claude, Manus, ChatGPT Codex, Microsoft 365, Gemini, Perplexity, Abacus AI, HubSpot."
---

# Skill & Agent Hub Connector

Dieser Skill ermöglicht die Interaktion mit dem zentralen Multi-Agent-Orchestrierungssystem.

## Voraussetzungen

- Skill & Agent Hub Server läuft auf `http://localhost:5000`
- Python 3.8+ mit `requests` Bibliothek

## Workflow

### 1. Server-Status prüfen

```bash
python3 /home/ubuntu/skills/skill-agent-hub-connector/scripts/hub_client.py health
```

### 2. Skills auflisten

```bash
# Alle Skills
python3 /home/ubuntu/skills/skill-agent-hub-connector/scripts/hub_client.py list skills

# Alle Agents
python3 /home/ubuntu/skills/skill-agent-hub-connector/scripts/hub_client.py list agents
```

### 3. Skills entdecken (Discovery)

```bash
# Nach Fähigkeiten suchen
python3 /home/ubuntu/skills/skill-agent-hub-connector/scripts/hub_client.py discover "text summarization"

# Nach Tags suchen
python3 /home/ubuntu/skills/skill-agent-hub-connector/scripts/hub_client.py discover --tags "web,scraping"
```

### 4. Skill ausführen

```bash
python3 /home/ubuntu/skills/skill-agent-hub-connector/scripts/hub_client.py execute skill <skill_name> '{"param": "value"}'
```

### 5. Agent ausführen

```bash
python3 /home/ubuntu/skills/skill-agent-hub-connector/scripts/hub_client.py execute agent <agent_name> '{"task": "description"}'
```

### 6. Plattform-Katalog abrufen

```bash
# Verfügbare Plattformen: chatgpt_codex, claude, manus, antigravity, microsoft365, gemini, perplexity, abacus, hubspot
python3 /home/ubuntu/skills/skill-agent-hub-connector/scripts/hub_client.py catalog <platform>
```

### 7. Bidirektionale Skills importieren

```bash
# Verfügbare Skills einer Plattform anzeigen
python3 /home/ubuntu/skills/skill-agent-hub-connector/scripts/hub_client.py bidirectional <platform>
```

## Unterstützte Plattformen

| Plattform | Export | Import | Katalog-Endpunkt |
|-----------|--------|--------|------------------|
| ChatGPT Codex | ✓ | ✓ | `/api/v1/catalog/chatgpt_codex` |
| Claude | ✓ | ✓ | `/api/v1/catalog/claude` |
| Manus | ✓ | ✓ | `/api/v1/catalog/manus` |
| Antigravity | ✓ | ✓ | `/api/v1/catalog/antigravity` |
| Microsoft 365 | ✓ | ✓ | `/api/v1/platforms/microsoft365/copilot-manifest` |
| Gemini | ✓ | ✓ | `/api/v1/platforms/gemini/tools-config` |
| Perplexity | ✓ | ✓ | `/api/v1/bidirectional/available-skills/perplexity` |
| Abacus AI | ✓ | ✓ | `/api/v1/platforms/abacus/deep-agent-config` |
| HubSpot | ✓ | ✓ | `/api/v1/bidirectional/available-skills/hubspot` |
