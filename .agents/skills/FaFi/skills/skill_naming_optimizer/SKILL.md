---
name: skill-naming-optimizer
description: "Validiert und optimiert Skill-Namen und Beschreibungen nach Best Practices. Verwenden bei Skill-Erstellung, Skill-Überarbeitung, Frontmatter-Optimierung, Verbesserung der Skill-Auslösung."
---

# Skill Naming Optimizer

Dieser Skill optimiert `name` und `description` im YAML-Frontmatter von Skills. Er ergänzt den skill-creator und sollte bei Step 4 (Edit the Skill) angewendet werden.

## Wann verwenden

- Bei Erstellung eines neuen Skills (nach `init_skill.py`)
- Bei Überarbeitung bestehender Skills
- Wenn ein Skill nicht korrekt ausgelöst wird

## Name-Optimierung

### Regeln (strikt)

| Regel | Gültig | Ungültig |
|-------|--------|----------|
| Kebab-Case | `csv-analyzer` | `csvAnalyzer`, `CSV_Analyzer` |
| Nur a-z, 0-9, Bindestriche | `api-v2-client` | `api_client`, `API-Client` |
| Max. 64 Zeichen | `data-processor` | (zu lang) |
| Muss Verzeichnisnamen entsprechen | `/skills/my-skill/` → `name: my-skill` | |

### Validierung

```bash
python /home/ubuntu/skills/skill-naming-optimizer/scripts/validate_name.py "skill-name"
```

## Description-Optimierung

Die `description` ist der **primäre Auslösemechanismus**. Manus entscheidet anhand der Beschreibung, ob ein Skill verwendet wird – der Body wird erst danach geladen.

### Struktur (empfohlen)

```
[Was der Skill tut]. [Wann verwenden]: [Anwendungsfall 1], [Anwendungsfall 2], [Anwendungsfall 3].
```

### Checkliste

1. **Was** - Beschreibt die Hauptfunktion klar?
2. **Wann** - Sind konkrete Anwendungsfälle genannt?
3. **Länge** - Unter 100 Wörter (immer im Kontext)?
4. **Trigger-Wörter** - Enthält Begriffe, die Benutzer verwenden würden?

### Beispiele

**Gut:**
```yaml
description: Analysiert CSV-Dateien in einem sequentiellen Workflow. Verwenden für: CSV-Datenanalyse, statistische Auswertungen, Datenvisualisierung.
```

**Besser:**
```yaml
description: Document creation and editing with tracked changes. Use for: creating .docx files, modifying content, working with tracked changes, redlining documents.
```

**Schlecht:**
```yaml
description: Ein Skill für CSV-Dateien.
```
*(Zu vage, keine Anwendungsfälle, wird nicht zuverlässig ausgelöst)*

### Optimierungsscript

Analysiere und optimiere eine bestehende Beschreibung:

```bash
python /home/ubuntu/skills/skill-naming-optimizer/scripts/optimize_description.py "/path/to/SKILL.md"
```

## Integration mit skill-creator

Bei Verwendung des skill-creator diesen Skill in **Step 4** (Edit the Skill) anwenden:

1. Nach Erstellung des Frontmatters → `validate_name.py` ausführen
2. Nach Schreiben der Beschreibung → Checkliste prüfen
3. Optional: `optimize_description.py` für Verbesserungsvorschläge

## Schnellreferenz

```yaml
---
name: kebab-case-max-64-zeichen
description: [Hauptfunktion]. [Wann verwenden]: [Anwendungsfall 1], [Anwendungsfall 2], [Anwendungsfall 3].
---
```
