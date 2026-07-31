# Plattform-Integration

Diese Anleitung erklärt, wie Sie den Skill & Agent Hub mit verschiedenen KI-Plattformen verbinden.

## Übersicht

Der Hub generiert automatisch plattformspezifische Kataloge, die direkt in die jeweiligen Tools importiert werden können.

| Plattform | Katalog-Endpunkt | Format |
|-----------|------------------|--------|
| ChatGPT Codex | `/api/v1/catalog/chatgpt_codex` | OpenAI Function Calling |
| Claude | `/api/v1/catalog/claude` | Anthropic Tool Format |
| Manus | `/api/v1/catalog/manus` | Manus Function Calling |
| Antigravity | `/api/v1/catalog/antigravity` | Action/Workflow Format |
| Microsoft 365 | `/api/v1/platforms/microsoft365/copilot-manifest` | Copilot Plugin Manifest |
| Gemini | `/api/v1/platforms/gemini/tools-config` | Google AI Tools Config |
| Abacus AI | `/api/v1/platforms/abacus/deep-agent-config` | Deep Agent Config |

---

## 1. ChatGPT / OpenAI Codex

### GPT Actions (Custom GPTs)

1. Erstellen Sie einen neuen Custom GPT
2. Gehen Sie zu "Configure" → "Actions"
3. Importieren Sie das OpenAPI-Schema:
   ```
   http://localhost:5000/api/v1/openapi-schema
   ```
4. Oder fügen Sie die Tools manuell hinzu:
   ```bash
   curl http://localhost:5000/api/v1/catalog/chatgpt_codex
   ```

### Assistants API

```python
import openai

# Katalog abrufen
import requests
catalog = requests.get("http://localhost:5000/api/v1/catalog/chatgpt_codex").json()

# Assistant erstellen
assistant = openai.beta.assistants.create(
    name="Skill Hub Assistant",
    instructions="Du hast Zugriff auf den Skill & Agent Hub.",
    tools=catalog["catalog"]["tools"],
    model="gpt-4o"
)
```

---

## 2. Claude (Anthropic)

### Claude Desktop / Cowork

1. Öffnen Sie die Claude-Einstellungen
2. Navigieren Sie zu "Tools" oder "MCP Servers"
3. Fügen Sie den Hub als MCP-Server hinzu:
   ```json
   {
     "mcpServers": {
       "skill-hub": {
         "command": "python3",
         "args": ["/path/to/skill-agent-hub/adapters/api_server.py", "--mcp"]
       }
     }
   }
   ```

### Claude API

```python
import anthropic

# Katalog abrufen
import requests
catalog = requests.get("http://localhost:5000/api/v1/catalog/claude").json()

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=catalog["catalog"]["tools"],
    messages=[{"role": "user", "content": "Fasse diesen Text zusammen..."}]
)
```

---

## 3. Manus

### Als Skill importieren

Der `skill-agent-hub-connector` ist bereits als Manus-Skill verfügbar:

```
/home/ubuntu/skills/skill-agent-hub-connector/SKILL.md
```

### Verwendung in Manus

```bash
# Server-Status prüfen
python3 /home/ubuntu/skills/skill-agent-hub-connector/scripts/hub_client.py health

# Skills auflisten
python3 /home/ubuntu/skills/skill-agent-hub-connector/scripts/hub_client.py list skills

# Skill ausführen
python3 /home/ubuntu/skills/skill-agent-hub-connector/scripts/hub_client.py execute skill text_summarizer '{"text": "...", "max_length": 100}'
```

---

## 4. Antigravity

### Workflow-Integration

1. Exportieren Sie den Antigravity-Katalog:
   ```bash
   curl http://localhost:5000/api/v1/catalog/antigravity > antigravity_actions.json
   ```

2. Importieren Sie die Actions in Antigravity:
   - Öffnen Sie Antigravity
   - Gehen Sie zu "Actions" → "Import"
   - Laden Sie `antigravity_actions.json`

---

## 5. Microsoft 365 Copilot

### Plugin-Manifest

1. Rufen Sie das Manifest ab:
   ```bash
   curl http://localhost:5000/api/v1/platforms/microsoft365/copilot-manifest > manifest.json
   ```

2. Passen Sie die URLs an Ihre Produktionsumgebung an

3. Registrieren Sie das Plugin im Microsoft Partner Center

### Graph API Integration

Der Hub kann über die importierten Microsoft 365 Skills auf Outlook, OneDrive, Teams etc. zugreifen (erfordert Azure AD App Registration).

---

## 6. Google Gemini

### Gemini API

```python
import google.generativeai as genai

# Katalog abrufen
import requests
config = requests.get("http://localhost:5000/api/v1/platforms/gemini/tools-config").json()

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    tools=config["tools"]
)
```

### Google AI Studio

1. Öffnen Sie [AI Studio](https://aistudio.google.com)
2. Erstellen Sie einen neuen Prompt
3. Fügen Sie die Tools aus dem Katalog hinzu

---

## 7. Perplexity AI

### Bidirektionale Skills

Perplexity bietet folgende Skills für den Import:

```bash
curl http://localhost:5000/api/v1/bidirectional/available-skills/perplexity
```

Verfügbare Skills:
- `perplexity_web_search` - Echtzeit-Websuche
- `perplexity_academic_search` - Akademische Recherche
- `perplexity_news_search` - Nachrichtensuche
- `perplexity_deep_research` - Tiefgehende Recherche

---

## 8. Abacus AI

### Deep Agent Integration

```bash
curl http://localhost:5000/api/v1/platforms/abacus/deep-agent-config
```

### Chat LLM

Der Hub kann als Tool-Provider für Abacus Chat LLM konfiguriert werden.

---

## 9. HubSpot

### CRM-Integration

Der Hub nutzt den HubSpot MCP-Server für bidirektionale Integration:

```bash
# Verfügbare HubSpot-Skills anzeigen
curl http://localhost:5000/api/v1/bidirectional/available-skills/hubspot
```

Verfügbare Operationen:
- Kontakte erstellen/lesen/aktualisieren
- Unternehmen verwalten
- Deals und Pipelines
- Tickets und Support

---

## Bidirektionale Integration testen

```bash
# Alle verfügbaren bidirektionalen Skills einer Plattform
python3 /home/ubuntu/skills/skill-agent-hub-connector/scripts/hub_client.py bidirectional perplexity

# Skill von einer Plattform importieren
curl -X POST http://localhost:5000/api/v1/bidirectional/import-skill \
  -H "Content-Type: application/json" \
  -d '{"platform": "perplexity", "skill_name": "perplexity_web_search"}'
```
