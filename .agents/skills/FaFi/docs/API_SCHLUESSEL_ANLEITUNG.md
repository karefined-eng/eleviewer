# API-Schlüssel Konfiguration

Diese Anleitung erklärt, wie Sie die API-Schlüssel für die verschiedenen Plattformen konfigurieren.

## Übersicht der benötigten Schlüssel

| Plattform | Umgebungsvariable | Wo erhalten? |
|-----------|-------------------|--------------|
| OpenAI/ChatGPT | `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) |
| Anthropic/Claude | `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/settings/keys) |
| Perplexity | `PERPLEXITY_API_KEY` | [perplexity.ai/settings](https://www.perplexity.ai/settings/api) |
| Google AI/Gemini | `GOOGLE_AI_API_KEY` | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| HubSpot | `HUBSPOT_ACCESS_TOKEN` | [developers.hubspot.com](https://developers.hubspot.com/docs/api/private-apps) |
| Abacus AI | `ABACUS_API_KEY` | [abacus.ai](https://abacus.ai/app/profile) |
| Microsoft 365 | `MICROSOFT_CLIENT_ID`, `MICROSOFT_CLIENT_SECRET`, `MICROSOFT_TENANT_ID` | [portal.azure.com](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade) |

## Methode 1: Umgebungsvariablen direkt setzen

### Linux/macOS (Terminal)
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export PERPLEXITY_API_KEY="pplx-..."
export GOOGLE_AI_API_KEY="AIza..."
export HUBSPOT_ACCESS_TOKEN="pat-..."
export ABACUS_API_KEY="..."
```

### Windows (PowerShell)
```powershell
$env:OPENAI_API_KEY="sk-..."
$env:ANTHROPIC_API_KEY="sk-ant-..."
$env:PERPLEXITY_API_KEY="pplx-..."
```

## Methode 2: .env-Datei verwenden

Erstellen Sie eine `.env`-Datei im Hauptverzeichnis des Skill & Agent Hub:

```bash
# /home/ubuntu/skill-agent-hub/.env

# OpenAI / ChatGPT Codex
OPENAI_API_KEY=sk-...

# Anthropic / Claude
ANTHROPIC_API_KEY=sk-ant-...

# Perplexity AI
PERPLEXITY_API_KEY=pplx-...

# Google AI / Gemini
GOOGLE_AI_API_KEY=AIza...

# HubSpot
HUBSPOT_ACCESS_TOKEN=pat-...

# Abacus AI
ABACUS_API_KEY=...

# Microsoft 365 (Azure AD App Registration)
MICROSOFT_CLIENT_ID=...
MICROSOFT_CLIENT_SECRET=...
MICROSOFT_TENANT_ID=...

# Server-Konfiguration
HUB_HOST=0.0.0.0
HUB_PORT=5000
```

## Methode 3: In Manus verwenden

Wenn Sie den Hub innerhalb von Manus nutzen, können Sie die Schlüssel über die Manus-Secrets-Verwaltung hinzufügen:

1. Öffnen Sie die Manus-Einstellungen
2. Navigieren Sie zu "Secrets"
3. Fügen Sie die benötigten API-Schlüssel hinzu

## Welche Schlüssel sind erforderlich?

**Mindestens einer** der folgenden LLM-Schlüssel wird benötigt:
- `OPENAI_API_KEY` (für ChatGPT Codex, DALL-E)
- `ANTHROPIC_API_KEY` (für Claude)
- `GOOGLE_AI_API_KEY` (für Gemini)

**Optional** (für erweiterte Funktionen):
- `PERPLEXITY_API_KEY` (für Echtzeit-Websuche)
- `HUBSPOT_ACCESS_TOKEN` (für CRM-Integration)
- `ABACUS_API_KEY` (für Deep Agent)
- Microsoft 365 Credentials (für Office-Integration)

## Server mit Schlüsseln starten

Nach der Konfiguration starten Sie den Server:

```bash
cd /home/ubuntu/skill-agent-hub
python3 adapters/api_server.py
```

Der Server lädt automatisch die `.env`-Datei und zeigt an, welche Plattformen verfügbar sind.

## Schlüssel testen

Prüfen Sie, ob die Schlüssel korrekt konfiguriert sind:

```bash
# Server-Status prüfen
curl http://localhost:5000/api/v1/health

# Verfügbare Skills auflisten
curl "http://localhost:5000/api/v1/registry/list?type=skill"
```
