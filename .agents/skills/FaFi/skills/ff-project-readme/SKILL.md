---
name: ff-project-readme
description: "Generiert und validiert README.md-Dateien nach FassadenFix Corporate Design mit CI-konformen Farben, Logos und Tonalität. Verwenden für: Projektdokumentation, Repository-README, Skill-Dokumentation, Software-Anleitungen, Open-Source-Projekte, interne Dokumentation."
default_enabled: true
priority: 75
scope: global
platforms:
  - claude
  - manus
  - chatgpt_codex
  - gemini
  - antigravity
required_skills:
  - fassadenfix-branding
  - fassadenfix-identity
optional_skills:
  - fassadenfix-assets
  - fassadenfix-copywriting
---

# FassadenFix Project README Skill

## Übersicht

Dieser Skill erstellt professionelle, markenkonformen README.md-Dateien für FassadenFix-Projekte. Er kombiniert die Dokumentationsstruktur des ursprünglichen `project-readme` Skills mit den FassadenFix CI-Richtlinien.

**Status:** STANDARD-SKILL (Opt-Out-Prinzip)
**Priorität:** Mittel (75)
**Geltungsbereich:** Global - alle Projektdokumentationen

---

## ⚠️ VERPFLICHTENDE CI-REGELN

> **WICHTIG:** Alle README-Dateien für FassadenFix-Projekte müssen den CI-Richtlinien entsprechen.

### Verpflichtende Farben (für HTML/Badge-Elemente)

| Farbe | Pantone | HEX | Verwendung |
|-------|---------|-----|------------|
| **FassadenFix Grün** | **368 C** | `#77bc1f` | Badges, Akzente, Links |
| **Dunkelgrau** | **445 C** | `#4e5758` | Text, Sekundärelemente |

### Verpflichtende Logo-Verwendung

> Pfad: `/home/ubuntu/skills/fassadenfix-assets/templates/logos/`

| Kontext | Logo-Datei |
|---------|------------|
| **README Header** | `standard/FassadenFix_Logo_bunt_transparent_300px.png` |
| **GitHub Badge** | `varianten/FassadenFix_Logo_96x96.jpg` |

### Verpflichtende Tonalität

Alle Texte folgen der FassadenFix Markensprache aus `fassadenfix-identity`:
- **Persönlich & nahbar** - Direkte Ansprache
- **Selbstbewusst & werteorientiert** - Qualität betonen
- **Partnerschaftlich** - Zusammenarbeit hervorheben
- **Ehrlich & transparent** - Klare Kommunikation

---

## Workflow

README-Erstellung erfolgt in diesen Schritten:

1. **Projektanalyse** - Struktur und Zweck verstehen
2. **Template-Auswahl** - Passende Vorlage wählen
3. **Content-Erstellung** - Inhalte nach CI-Richtlinien
4. **Qualitätsprüfung** - Markenkonformität sicherstellen

---

## Template-Auswahl

Wähle das passende Template basierend auf dem Projekttyp:

| Projekttyp | Template | Referenz |
|------------|----------|----------|
| **Skill/Agent** | Skill-README | `templates/skill-readme.md` |
| **Webanwendung** | Web-README | `templates/web-readme.md` |
| **Internes Tool** | Tool-README | `templates/tool-readme.md` |
| **API/Service** | API-README | `templates/api-readme.md` |
| **Allgemein** | Standard-README | `templates/standard-readme.md` |

---

## README-Struktur (Standard)

Jede README folgt dieser Grundstruktur:

### 1. Header-Bereich

```markdown
<div align="center">
  <img src="[Logo-Pfad]" alt="FassadenFix Logo" width="300">
  
  # [Projektname]
  
  **[Kurzbeschreibung - max. 2 Sätze]**
  
  [![FassadenFix](https://img.shields.io/badge/FassadenFix-Projekt-77bc1f?style=flat-square)](https://fassadenfix.de)
  [![Status](https://img.shields.io/badge/Status-Aktiv-77bc1f?style=flat-square)]()
</div>
```

### 2. Einleitung

> Kurze, prägnante Zusammenfassung nach FassadenFix Tonalität.

**Beispiel:**
> "Dieses Projekt unterstützt Sie bei [Zweck]. Wie bei allen FassadenFix-Lösungen steht Qualität und Transparenz im Vordergrund."

### 3. Funktionen

Liste der Hauptfunktionen mit FassadenFix-Bezug:

```markdown
## Funktionen

| Funktion | Beschreibung |
|----------|--------------|
| **[Feature 1]** | [Beschreibung] |
| **[Feature 2]** | [Beschreibung] |
```

### 4. Installation

Schrittweise Anleitung mit klaren Anweisungen:

```markdown
## Installation

### Voraussetzungen

- [Voraussetzung 1]
- [Voraussetzung 2]

### Schnellstart

\`\`\`bash
# Schritt 1: [Beschreibung]
[Befehl]

# Schritt 2: [Beschreibung]
[Befehl]
\`\`\`
```

### 5. Verwendung

Codebeispiele und Anwendungsfälle:

```markdown
## Verwendung

### Grundlegende Verwendung

\`\`\`[sprache]
[Codebeispiel]
\`\`\`

### Erweiterte Optionen

[Weitere Beispiele nach Bedarf]
```

### 6. Konfiguration (optional)

```markdown
## Konfiguration

| Parameter | Beschreibung | Standard |
|-----------|--------------|----------|
| `[param]` | [Beschreibung] | `[wert]` |
```

### 7. Beitrag (für Open-Source)

```markdown
## Beitrag

Wir freuen uns über Beiträge! Bitte beachten Sie:

1. Fork des Repositories erstellen
2. Feature-Branch anlegen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'feat: Add AmazingFeature'`)
4. Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request erstellen
```

### 8. Lizenz

```markdown
## Lizenz

Dieses Projekt ist unter der [Lizenztyp] lizenziert. Siehe [LICENSE](LICENSE) für Details.
```

### 9. Kontakt

```markdown
## Kontakt

**FassadenFix GmbH**
- Website: [www.fassadenfix.de](https://www.fassadenfix.de)
- E-Mail: [kontakt@fassadenfix.de](mailto:kontakt@fassadenfix.de)

---

<div align="center">
  <sub>Erstellt mit 💚 von FassadenFix</sub>
</div>
```

---

## Badge-Vorlagen

### FassadenFix Badges (CI-konform)

```markdown
<!-- Projekt-Badge -->
[![FassadenFix](https://img.shields.io/badge/FassadenFix-Projekt-77bc1f?style=flat-square)](https://fassadenfix.de)

<!-- Status-Badges -->
[![Status](https://img.shields.io/badge/Status-Aktiv-77bc1f?style=flat-square)]()
[![Status](https://img.shields.io/badge/Status-In_Entwicklung-4e5758?style=flat-square)]()
[![Status](https://img.shields.io/badge/Status-Archiviert-4e5758?style=flat-square)]()

<!-- Versions-Badge -->
[![Version](https://img.shields.io/badge/Version-1.0.0-77bc1f?style=flat-square)]()

<!-- CI-Badge -->
[![CI](https://img.shields.io/badge/CI-konform-77bc1f?style=flat-square)]()
```

---

## Qualitätsprüfung

### Checkliste vor Veröffentlichung

| Prüfpunkt | Erfüllt |
|-----------|---------|
| Logo korrekt eingebunden (aus `fassadenfix-assets`) | ☐ |
| Farben CI-konform (#77bc1f, #4e5758) | ☐ |
| Tonalität entspricht `fassadenfix-identity` | ☐ |
| Alle Abschnitte vollständig | ☐ |
| Code-Beispiele getestet | ☐ |
| Links funktionieren | ☐ |

### Validierung

```bash
# README-Struktur prüfen
python /home/ubuntu/skills/ff-project-readme/scripts/validate_readme.py [README-Pfad]
```

---

## Anwendungsbeispiele

### Skill-Dokumentation erstellen

```
Erstelle eine README für den neuen FassadenFix-Skill
→ Template: templates/skill-readme.md
→ Logo: FassadenFix_Logo_bunt_transparent_300px.png
→ Tonalität: fassadenfix-identity
```

### Webanwendung dokumentieren

```
Erstelle eine README für die FassadenFix-Webapp
→ Template: templates/web-readme.md
→ Badges: FassadenFix-Projekt, Status, Version
→ Installation: npm/pnpm Befehle
```

### API-Dokumentation

```
Erstelle eine README für die FassadenFix-API
→ Template: templates/api-readme.md
→ Endpunkte: Tabellen-Format
→ Authentifizierung: Klar dokumentiert
```

---

## Zusammenspiel mit anderen Skills

| Skill | Integration |
|-------|-------------|
| **fassadenfix-branding** | Farben, Typografie, UI-Elemente |
| **fassadenfix-identity** | Tonalität, Kernbotschaften |
| **fassadenfix-assets** | Logo-Dateien, Icons |
| **fassadenfix-copywriting** | Textbausteine, Claims |

---

## Deaktivierung (Opt-Out)

```
--no-readme-branding
--skip-ff-project-readme
"ohne FassadenFix README-Stil"
"neutrale README"
```

---

## Quelle

Dieser Skill basiert auf dem ursprünglichen `project-readme` Skill und wurde erweitert um die **FassadenFix Corporate Design Richtlinien** aus den Skills `fassadenfix-branding`, `fassadenfix-identity` und `fassadenfix-assets`.
