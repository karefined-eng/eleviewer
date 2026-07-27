#!/usr/bin/env python3
"""
FassadenFix Smart README Generator

Generiert intelligente README-Dateien basierend auf SKILL.md-Inhalten.
Extrahiert automatisch Informationen aus vorhandenen Skill-Definitionen.

Verwendung:
    python smart_readme_generator.py <skill-pfad>
    python smart_readme_generator.py /home/ubuntu/FaFi/skills/fassadenfix_branding
"""

import sys
import re
import yaml
from pathlib import Path
from datetime import datetime


def extract_skill_info(skill_path: Path) -> dict:
    """Extrahiert Informationen aus SKILL.md."""
    skill_md = skill_path / "SKILL.md"
    
    if not skill_md.exists():
        return {"name": skill_path.name, "description": "", "content": ""}
    
    content = skill_md.read_text(encoding="utf-8")
    
    # Frontmatter extrahieren
    frontmatter = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
            except:
                pass
            body = parts[2].strip()
        else:
            body = content
    else:
        body = content
    
    # Überschriften und Abschnitte extrahieren
    sections = {}
    current_section = "intro"
    current_content = []
    
    for line in body.split('\n'):
        if line.startswith('## '):
            if current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line[3:].strip().lower()
            current_content = []
        else:
            current_content.append(line)
    
    if current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return {
        "name": frontmatter.get("name", skill_path.name),
        "description": frontmatter.get("description", ""),
        "priority": frontmatter.get("priority", ""),
        "scope": frontmatter.get("scope", ""),
        "platforms": frontmatter.get("platforms", []),
        "required_skills": frontmatter.get("required_skills", []),
        "optional_skills": frontmatter.get("optional_skills", []),
        "default_enabled": frontmatter.get("default_enabled", False),
        "sections": sections,
        "body": body
    }


def generate_smart_readme(skill_path: Path) -> str:
    """Generiert eine intelligente README basierend auf SKILL.md."""
    info = extract_skill_info(skill_path)
    
    # Formatierter Name
    display_name = info["name"].replace("_", " ").replace("-", " ").title()
    kebab_name = info["name"].replace("_", "-").lower()
    
    # Status bestimmen
    status = "STANDARD-SKILL" if info.get("default_enabled") else "OPTIONALER SKILL"
    
    # Priorität formatieren
    priority = info.get("priority", "")
    priority_label = "Hoch" if priority and int(priority) >= 80 else "Mittel" if priority and int(priority) >= 50 else "Niedrig"
    
    # Beschreibung extrahieren oder generieren
    description = info.get("description", "")
    if not description:
        description = f"Skill für {display_name} Funktionalität."
    
    # Übersicht aus Body extrahieren
    overview = info.get("sections", {}).get("übersicht", "")
    if not overview:
        overview = description
    
    # Funktionen aus Body extrahieren
    functions_section = info.get("sections", {}).get("funktionen", "")
    
    # Workflow aus Body extrahieren
    workflow_section = info.get("sections", {}).get("workflow", "")
    
    # README generieren
    readme = f'''<div align="center">
  <img src="/home/ubuntu/skills/fassadenfix-assets/templates/logos/standard/FassadenFix_Logo_bunt_transparent_300px.png" alt="FassadenFix Logo" width="300">
  
  # {display_name}
  
  **{description.split(". ")[0]}**
  
  [![FassadenFix](https://img.shields.io/badge/FassadenFix-Skill-77bc1f?style=flat-square)](https://fassadenfix.de)
  [![Status](https://img.shields.io/badge/Status-Aktiv-77bc1f?style=flat-square)]()
  [![Priorität](https://img.shields.io/badge/Priorität-{priority or "N/A"}-4e5758?style=flat-square)]()
</div>

---

## Übersicht

{overview}

**Status:** {status}
**Priorität:** {priority_label} ({priority or "N/A"})
**Geltungsbereich:** {info.get("scope", "Global").capitalize()}

---

## Zusammenspiel mit anderen Skills

| Skill | Beziehung | Funktion |
|-------|-----------|----------|
'''
    
    # Required Skills
    for skill in info.get("required_skills", []):
        readme += f'| **{skill}** | Pflicht | Erforderliche Abhängigkeit |\n'
    
    # Optional Skills
    for skill in info.get("optional_skills", []):
        readme += f'| **{skill}** | Optional | Optionale Erweiterung |\n'
    
    if not info.get("required_skills") and not info.get("optional_skills"):
        readme += '| **fassadenfix-branding** | Empfohlen | CI-Richtlinien |\n'
    
    readme += '''
---

## Plattformen

Dieser Skill ist verfügbar auf:

'''
    
    platforms = info.get("platforms", ["manus"])
    for platform in platforms:
        readme += f'- **{platform.replace("_", " ").title()}**\n'
    
    readme += f'''
---

## Verwendung

### Automatische Aktivierung

Der Skill wird automatisch aktiviert bei relevanten Anfragen.

### Explizite Aktivierung

```
/{kebab_name}
"Mit {display_name} erstellen"
```

---

## Deaktivierung (Opt-Out)

```
--no-{kebab_name}
--skip-{kebab_name}
"ohne {display_name}"
```

---

## Quelle

Dieser Skill ist Teil des **FassadenFix Skill & Agent Hub** Ökosystems.

---

<div align="center">
  <sub>Erstellt mit 💚 von FassadenFix</sub>
  <br>
  <sub>Letzte Aktualisierung: {datetime.now().strftime("%Y-%m-%d")}</sub>
</div>
'''
    
    return readme


def main():
    if len(sys.argv) < 2:
        print("Verwendung: python smart_readme_generator.py <skill-pfad>")
        sys.exit(1)
    
    skill_path = Path(sys.argv[1])
    
    if not skill_path.exists():
        print(f"Fehler: Pfad nicht gefunden: {skill_path}")
        sys.exit(1)
    
    readme = generate_smart_readme(skill_path)
    
    # README schreiben
    readme_path = skill_path / "README.md"
    readme_path.write_text(readme, encoding="utf-8")
    
    print(f"✅ README generiert: {readme_path}")


if __name__ == "__main__":
    main()
