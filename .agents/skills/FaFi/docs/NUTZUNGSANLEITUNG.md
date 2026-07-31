# Skill & Agent Hub - Nutzungsanleitung (Version 2.1)

Diese Anleitung beschreibt, wie Sie das Multi-Agent-Orchestrierungssystem einrichten, nutzen und erweitern können.

## 1. Installation und Setup

Folgen Sie den Schritten in der `README.md`-Datei, um das System zu klonen, Abhängigkeiten zu installieren und den API-Server zu starten.

## 2. API-Schlüssel konfigurieren

Das System verwendet Umgebungsvariablen, um auf die APIs der verschiedenen Plattformen zuzugreifen. Erstellen Sie eine `.env`-Datei im Hauptverzeichnis oder setzen Sie die Variablen in Ihrer Shell:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-...
export PERPLEXITY_API_KEY="pplx-..."
export GOOGLE_AI_API_KEY="...
# ... und so weiter für alle benötigten Dienste
```

## 3. Integration in Ihre KI-Plattform

Der Hub generiert für jede Plattform spezifische Konfigurationen, um die Integration so einfach wie möglich zu machen.

### OpenAI / ChatGPT (GPTs)

1.  **OpenAPI Schema**: Holen Sie das für GPT Actions generierte OpenAPI-Schema.
    ```bash
    curl http://localhost:5000/api/v1/openapi-schema
    ```
2.  **GPT erstellen**: Erstellen oder bearbeiten Sie ein GPT und fügen Sie eine neue "Action" hinzu. Importieren Sie das OpenAPI-Schema.
3.  **Anweisungen**: Fügen Sie die generierten Anweisungen zum System-Prompt Ihres GPTs hinzu.
    ```bash
    curl http://localhost:5000/api/v1/instructions/chatgpt_codex
    ```

### Claude (Cowork & Code)

1.  **Tool-Katalog**: Holen Sie den Katalog im Anthropic Tool-Format.
    ```bash
    curl http://localhost:5000/api/v1/catalog/claude
    ```
2.  **System-Prompt**: Fügen Sie den Tool-Katalog in den System-Prompt Ihres Claude-Modells ein.
3.  **Slash-Commands (Claude Code)**: Für eine IDE-Integration können Sie die generierten Slash-Commands nutzen.
    ```bash
    curl http://localhost:5000/api/v1/platforms/claude_code/slash-commands
    ```

### Manus 1.6

1.  **Function Calling**: Holen Sie den Katalog im Manus Function-Calling-Format.
    ```bash
    curl http://localhost:5000/api/v1/catalog/manus
    ```
2.  **System-Prompt**: Integrieren Sie die Funktionen in den System-Prompt Ihres Manus-Agenten.

### Microsoft 365 Copilot

1.  **Plugin-Manifest**: Holen Sie das vollständige Plugin-Manifest.
    ```bash
    curl http://localhost:5000/api/v1/platforms/microsoft365/copilot-manifest
    ```
2.  **Plugin installieren**: Laden Sie das Manifest in Ihrer Microsoft 365-Entwicklungsumgebung hoch, um das Plugin zu installieren.

### Google Gemini & AI Studio

1.  **Tools-Konfiguration**: Holen Sie die Konfiguration im Gemini-Format.
    ```bash
    curl http://localhost:5000/api/v1/platforms/gemini/tools-config
    ```
2.  **API-Aufruf**: Übergeben Sie diese Konfiguration an die `tools`-Eigenschaft bei Ihrem Gemini-API-Aufruf.

## 4. Skills und Agents nutzen

Alle Interaktionen mit dem Hub laufen über die REST-API.

### Einen Skill ausführen

Führen Sie einen beliebigen Skill (nativ oder importiert) über seinen Namen aus.

**Beispiel: `manus_shell_execute` (importiert)**
```bash
curl -X POST http://localhost:5000/api/v1/execute/skill/manus_shell_execute \
-H "Content-Type: application/json" \
-d '{
  "command": "ls -la ~"
}'
```

### Einen Agent ausführen

Starten Sie einen Agenten, um eine komplexere Aufgabe zu erledigen.

**Beispiel: `research_agent`**
```bash
curl -X POST http://localhost:5000/api/v1/execute/agent/research_agent \
-H "Content-Type: application/json" \
-d '{
  "topic": "Die Zukunft der KI-Agenten",
  "questions": [
    "Welche Architekturen sind am vielversprechendsten?",
    "Was sind die größten Herausforderungen?"
  ]
}'
```

### Skills dynamisch entdecken

Nutzen Sie den Discovery-Endpunkt, um zur Laufzeit den besten Skill für eine Aufgabe zu finden.

```bash
curl -X POST http://localhost:5000/api/v1/discover \
-H "Content-Type: application/json" \
-d '{
  "query": "Fasse mir diesen langen Text zusammen",
  "type": "skill",
  "limit": 1
}'
```

## 5. Eigene Skills und Agents erstellen

Die Erweiterung des Hubs ist einfach und erfordert keine Code-Änderungen am Kernsystem.

### Einen neuen nativen Skill erstellen

1.  **Verzeichnis erstellen**: Erstellen Sie ein neues Verzeichnis unter `/skills/native/ihr_skill_name`.
2.  **`manifest.json` erstellen**: Definieren Sie die Metadaten, Inputs und Outputs Ihres Skills.
3.  **`main.py` implementieren**: Schreiben Sie die Python-Logik für Ihren Skill.
4.  **Registry aktualisieren**: Starten Sie den API-Server neu oder rufen Sie den `scan`-Endpunkt auf.
    ```bash
    curl -X POST http://localhost:5000/api/v1/registry/scan
    ```

### Einen neuen importierten Skill hinzufügen

Der Prozess ist ähnlich, aber die Implementierung ruft eine externe API auf.

1.  **Verzeichnis erstellen**: `/skills/imported/neue_plattform/neuer_skill`.
2.  **`manifest.json` erstellen**: Setzen Sie `implementation.type` auf `remote` und `metadata.imported` auf `true`.
3.  **`main.py` implementieren**: Implementieren Sie den API-Aufruf an die externe Plattform. Nutzen Sie `os.environ.get()` für API-Schlüssel.
4.  **Registry aktualisieren**.

## 6. Vollständige API-Referenz (v2.1)

- `GET /api/v1/info`: Allgemeine Informationen über den Hub.
- `GET /api/v1/health`: Health-Check.

**Registry:**
- `POST /api/v1/registry/scan`: Scannt und registriert alle Entities.
- `GET /api/v1/registry/list`: Listet alle Entities (filterbar nach `type`, `imported`, `platform`).
- `GET /api/v1/registry/get/<name>`: Holt eine spezifische Entity.
- `GET /api/v1/registry/imported`: Listet alle importierten Skills (filterbar nach `platform`).

**Discovery:**
- `POST /api/v1/discover`: Findet passende Skills/Agents für eine Aufgabe.
- `POST /api/v1/suggest-composition`: Schlägt eine Skill-Komposition vor.

**Execution:**
- `POST /api/v1/execute/skill/<name>`: Führt einen Skill aus.
- `POST /api/v1/execute/agent/<name>`: Führt einen Agent aus.
- `POST /api/v1/execute/task`: Führt eine Aufgabe mit dynamischer Skill-Auswahl aus.

**Adapter & Kataloge:**
- `GET /api/v1/catalog/<platform>`: Generiert den Katalog für eine Plattform.
- `GET /api/v1/instructions/<platform>`: Generiert Integrationsanweisungen.
- `GET /api/v1/openapi-schema`: Generiert das OpenAPI-Schema für GPTs.

**Bidirektionale Endpunkte:**
- `GET /api/v1/bidirectional/available-skills/<platform>`: Zeigt importierbare Skills einer Plattform.
- `POST /api/v1/bidirectional/import-skill`: (Für zukünftige Automatisierung) Importiert einen Skill.
- `POST /api/v1/bidirectional/export-to/<platform>`: (Für zukünftige Automatisierung) Exportiert Skills.

**Plattform-spezifische Endpunkte:**
- `GET /api/v1/platforms/microsoft365/copilot-manifest`
- `GET /api/v1/platforms/gemini/tools-config`
- `GET /api/v1/platforms/abacus/deep-agent-config`
- `GET /api/v1/platforms/antigravity/manifest`
- `GET /api/v1/platforms/claude/mcp-config`
- `GET /api/v1/platforms/claude_code/slash-commands`
- ... und weitere.
