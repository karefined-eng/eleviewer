#!/usr/bin/env python3
"""
FassadenFix README Generator

Generiert README-Dateien basierend auf Templates und Projektinformationen.

Verwendung:
    python generate_readme.py <projekt-name> --type <template-typ> [--output <pfad>]
    
Beispiele:
    python generate_readme.py "MeinProjekt" --type standard
    python generate_readme.py "FaFi-API" --type api --output ./README.md
    python generate_readme.py "Neuer Skill" --type skill
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime


# Pfad zu den Templates
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Verfügbare Template-Typen
TEMPLATE_TYPES = {
    "standard": "standard-readme.md",
    "skill": "skill-readme.md",
    "web": "web-readme.md",
    "api": "api-readme.md",
    "tool": "tool-readme.md"
}


def load_template(template_type: str) -> str:
    """Lädt ein Template basierend auf dem Typ."""
    
    if template_type not in TEMPLATE_TYPES:
        raise ValueError(f"Unbekannter Template-Typ: {template_type}. "
                        f"Verfügbar: {', '.join(TEMPLATE_TYPES.keys())}")
    
    template_path = TEMPLATES_DIR / TEMPLATE_TYPES[template_type]
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template nicht gefunden: {template_path}")
    
    return template_path.read_text(encoding="utf-8")


def replace_placeholders(content: str, project_name: str, **kwargs) -> str:
    """Ersetzt Platzhalter im Template mit Projektinformationen."""
    
    replacements = {
        "[PROJEKTNAME]": project_name,
        "[SKILL-NAME]": project_name,
        "[WEBAPP-NAME]": project_name,
        "[API-NAME]": project_name,
        "[TOOL-NAME]": project_name,
        "[projektname]": project_name.lower().replace(" ", "-"),
        "[skill-name]": project_name.lower().replace(" ", "-"),
        "YYYY-MM-DD": datetime.now().strftime("%Y-%m-%d"),
        "2025-02-02": datetime.now().strftime("%Y-%m-%d"),
    }
    
    # Benutzerdefinierte Ersetzungen hinzufügen
    replacements.update(kwargs)
    
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    
    return content


def generate_readme(project_name: str, template_type: str = "standard", 
                   output_path: str = None, **kwargs) -> str:
    """Generiert eine README-Datei."""
    
    # Template laden
    template = load_template(template_type)
    
    # Platzhalter ersetzen
    readme_content = replace_placeholders(template, project_name, **kwargs)
    
    # Optional: In Datei speichern
    if output_path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(readme_content, encoding="utf-8")
        print(f"✅ README erstellt: {output_path}")
    
    return readme_content


def main():
    parser = argparse.ArgumentParser(
        description="FassadenFix README Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
    python generate_readme.py "MeinProjekt" --type standard
    python generate_readme.py "FaFi-API" --type api --output ./README.md
    python generate_readme.py "Neuer Skill" --type skill
        """
    )
    
    parser.add_argument("project_name", help="Name des Projekts")
    parser.add_argument(
        "--type", "-t",
        choices=TEMPLATE_TYPES.keys(),
        default="standard",
        help="Template-Typ (Standard: standard)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Ausgabepfad für die README-Datei"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Zeigt eine Vorschau ohne zu speichern"
    )
    
    args = parser.parse_args()
    
    try:
        readme = generate_readme(
            project_name=args.project_name,
            template_type=args.type,
            output_path=args.output if not args.preview else None
        )
        
        if args.preview or not args.output:
            print("\n" + "=" * 60)
            print("README Vorschau")
            print("=" * 60 + "\n")
            print(readme[:2000])
            if len(readme) > 2000:
                print("\n... (gekürzt) ...")
            print("\n" + "=" * 60)
            
            if not args.output:
                print("\nHinweis: Verwenden Sie --output <pfad> zum Speichern.")
        
    except (ValueError, FileNotFoundError) as e:
        print(f"❌ Fehler: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
