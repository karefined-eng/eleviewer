---
name: skill-creator-enhanced
description: "Creates and validates Skills with integrated naming and description optimization. Use for: creating skills with automatic best-practice checks, skill revision, frontmatter optimization, improving skill triggering."
---

# Enhanced Skill Creator

Dieser Skill ersetzt den Standard-skill-creator mit einem erweiterten Workflow, der die Namens- und Beschreibungsoptimierung automatisch integriert.

## Wann verwenden

- **Statt skill-creator** für neue Skills mit automatischer Optimierung
- Bei Überarbeitung bestehender Skills
- Wenn Skills nicht korrekt ausgelöst werden

## Erweiterter Workflow

Der Workflow entspricht dem skill-creator, aber mit integrierten Optimierungsschritten:

1. **Verstehen** - Beispiele sammeln (wie skill-creator)
2. **Planen** - Ressourcen identifizieren (wie skill-creator)
3. **Initialisieren** - `init_skill_enhanced.py` statt `init_skill.py`
4. **Bearbeiten** - SKILL.md mit optimiertem Frontmatter
5. **Validieren** - `quick_validate_enhanced.py` mit Beschreibungs-Score
6. **Liefern** - SKILL.md an Benutzer senden

## Step 3: Initialisieren (erweitert)

Statt `init_skill.py` verwende das erweiterte Script:

```bash
# Standard (mit interaktiver Beschreibung)
python /home/ubuntu/skills/skill-creator-enhanced/scripts/init_skill_enhanced.py <skill-name>

# Mit Beschreibung
python /home/ubuntu/skills/skill-creator-enhanced/scripts/init_skill_enhanced.py <skill-name> \
  --description "Analysiert CSV-Dateien. Verwenden für: Datenanalyse, Validierung."

# Interaktiver Modus mit Wizard
python /home/ubuntu/skills/skill-creator-enhanced/scripts/init_skill_enhanced.py <skill-name> --interactive
```

Das Script:
- Validiert den Namen automatisch (Kebab-Case, max 64 Zeichen)
- Schlägt korrigierten Namen vor bei Fehlern
- Analysiert die Beschreibung und zeigt Score
- Gibt Verbesserungsvorschläge für bessere Auslösung

## Step 5: Validieren (erweitert)

Statt `quick_validate.py` verwende das erweiterte Script:

```bash
python /home/ubuntu/skills/skill-creator-enhanced/scripts/quick_validate_enhanced.py <skill-name>
```

Zusätzliche Prüfungen:
- **Name-Score**: Kebab-Case-Konformität
- **Description-Score**: 0-100 basierend auf Was/Wann/Anwendungsfälle
- **Verbesserungsvorschläge**: Konkrete Tipps für bessere Auslösung

## Auto-Improve: Automatische Beschreibungsoptimierung

Bei Score < 100 kann die Beschreibung automatisch verbessert werden:

```bash
# Vorschau der Verbesserung
python /home/ubuntu/skills/skill-creator-enhanced/scripts/auto_improve_description.py <skill-name>

# Verbesserung anwenden
python /home/ubuntu/skills/skill-creator-enhanced/scripts/auto_improve_description.py <skill-name> --apply

# Mit Sprachauswahl (de/en)
python /home/ubuntu/skills/skill-creator-enhanced/scripts/auto_improve_description.py <skill-name> --language de --apply
```

Das Script:
- Analysiert die aktuelle Beschreibung
- Erkennt fehlende Komponenten (Was/Wann/Use Cases)
- Generiert automatisch passende Ergänzungen
- Unterstützt Deutsch und Englisch

## Beschreibungs-Checkliste

Eine gute Beschreibung enthält:

| Komponente | Gewichtung | Beispiel |
|------------|------------|----------|
| **Was** (Aktion) | 30% | "Analysiert...", "Erstellt...", "Validiert..." |
| **Wann** (Trigger) | 30% | "Verwenden für:", "Use for:", "Anwenden bei:" |
| **Anwendungsfälle** | 20% | "Datenanalyse, Validierung, Visualisierung" |
| **Länge** (10-50 Wörter) | 20% | Prägnant aber vollständig |

**Ziel-Score: ≥60/100** für zuverlässige Skill-Auslösung.

## Beispiel: Vollständiger Workflow

```bash
# 1. Skill initialisieren mit optimierter Beschreibung
python /home/ubuntu/skills/skill-creator-enhanced/scripts/init_skill_enhanced.py csv-analyzer \
  --description "Analysiert CSV-Dateien in sequentiellem Workflow. Verwenden für: CSV-Datenanalyse, statistische Auswertungen, Datenvisualisierung."

# 2. SKILL.md Body bearbeiten (manuell)

# 3. Validieren mit erweitertem Script
python /home/ubuntu/skills/skill-creator-enhanced/scripts/quick_validate_enhanced.py csv-analyzer

# 4. Bei Score <60: Beschreibung verbessern und erneut validieren
```

## Migration von skill-creator

Für bestehende Skills mit schlechter Auslösung:

```bash
# Bestehenden Skill analysieren
python /home/ubuntu/skills/skill-creator-enhanced/scripts/quick_validate_enhanced.py <skill-name>

# Frontmatter manuell verbessern basierend auf Vorschlägen
# Erneut validieren bis Score ≥60
```
