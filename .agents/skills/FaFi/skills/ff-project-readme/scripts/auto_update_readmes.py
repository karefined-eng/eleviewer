#!/usr/bin/env python3
"""
FassadenFix README Auto-Updater

Automatisiert die Aktualisierung von README-Dateien in FassadenFix-Projekten.
Wird täglich ausgeführt, um CI-Konformität sicherzustellen.

Verwendung:
    python auto_update_readmes.py [--repo-path <pfad>] [--dry-run] [--force]
    
Beispiele:
    python auto_update_readmes.py --repo-path /home/ubuntu/FaFi
    python auto_update_readmes.py --dry-run  # Vorschau ohne Änderungen
    python auto_update_readmes.py --force    # Alle READMEs neu generieren
"""

import argparse
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Pfade
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
VALIDATE_SCRIPT = SCRIPT_DIR / "validate_readme.py"

# FassadenFix CI-Konstanten
FF_GREEN = "#77bc1f"
FF_GRAY = "#4e5758"
FF_LOGO_PATH = "/home/ubuntu/skills/fassadenfix-assets/templates/logos/"

# Projekt-Typen basierend auf Verzeichnisstruktur
PROJECT_TYPE_INDICATORS = {
    "skill": ["SKILL.md", "manifest.json"],
    "web": ["package.json", "index.html", "vite.config.ts"],
    "api": ["api_server.py", "openapi.yaml", "swagger.json"],
    "tool": ["main.py", "cli.py", "__main__.py"]
}


class ReadmeUpdater:
    """Verwaltet die automatische Aktualisierung von README-Dateien."""
    
    def __init__(self, repo_path: str, dry_run: bool = False, force: bool = False):
        self.repo_path = Path(repo_path)
        self.dry_run = dry_run
        self.force = force
        self.updated_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.log_entries = []
    
    def log(self, message: str, level: str = "INFO"):
        """Protokolliert eine Nachricht."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] {message}"
        self.log_entries.append(entry)
        print(entry)
    
    def detect_project_type(self, project_path: Path) -> str:
        """Erkennt den Projekttyp basierend auf vorhandenen Dateien."""
        for project_type, indicators in PROJECT_TYPE_INDICATORS.items():
            for indicator in indicators:
                if (project_path / indicator).exists():
                    return project_type
        return "standard"
    
    def validate_readme(self, readme_path: Path) -> Dict:
        """Validiert eine README-Datei gegen CI-Richtlinien."""
        try:
            result = subprocess.run(
                ["python3", str(VALIDATE_SCRIPT), str(readme_path)],
                capture_output=True,
                text=True
            )
            # Parse Score aus Output
            score = 0
            for line in result.stdout.split('\n'):
                if 'Score:' in line:
                    try:
                        score = int(line.split(':')[1].split('/')[0].strip())
                    except:
                        pass
            return {
                "valid": result.returncode == 0,
                "score": score,
                "output": result.stdout
            }
        except Exception as e:
            return {"valid": False, "score": 0, "error": str(e)}
    
    def needs_update(self, readme_path: Path) -> bool:
        """Prüft, ob eine README aktualisiert werden muss."""
        if self.force:
            return True
        
        if not readme_path.exists():
            return True
        
        validation = self.validate_readme(readme_path)
        
        # Aktualisieren wenn Score unter 70
        if validation.get("score", 0) < 70:
            return True
        
        # Prüfen auf fehlende CI-Elemente
        content = readme_path.read_text(encoding="utf-8")
        
        ci_checks = [
            FF_GREEN in content.lower(),
            "fassadenfix" in content.lower(),
            "77bc1f" in content
        ]
        
        if not all(ci_checks):
            return True
        
        return False
    
    def update_readme(self, project_path: Path, project_name: str) -> bool:
        """Aktualisiert eine README-Datei mit FassadenFix-Branding."""
        readme_path = project_path / "README.md"
        project_type = self.detect_project_type(project_path)
        
        self.log(f"Verarbeite: {project_name} (Typ: {project_type})")
        
        if not self.needs_update(readme_path):
            self.log(f"  → Übersprungen (bereits CI-konform)", "SKIP")
            self.skipped_count += 1
            return False
        
        if self.dry_run:
            self.log(f"  → Würde aktualisiert werden (Dry-Run)", "DRY")
            return True
        
        try:
            # Für Skills mit SKILL.md: Smart Generator verwenden
            if project_type == "skill" and (project_path / "SKILL.md").exists():
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        "smart_readme_generator",
                        SCRIPT_DIR / "smart_readme_generator.py"
                    )
                    smart_gen = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(smart_gen)
                    new_content = smart_gen.generate_smart_readme(project_path)
                    readme_path.write_text(new_content, encoding="utf-8")
                    self.log(f"  → Smart-Aktualisiert ✓", "UPDATE")
                    self.updated_count += 1
                    return True
                except Exception as e:
                    self.log(f"  → Smart-Generator Fehler: {e}, verwende Template", "WARN")
            
            # Template laden (Fallback oder für Nicht-Skills)
            template_file = TEMPLATES_DIR / f"{project_type}-readme.md"
            if not template_file.exists():
                template_file = TEMPLATES_DIR / "standard-readme.md"
            
            template = template_file.read_text(encoding="utf-8")
            
            # Bestehende README lesen (falls vorhanden)
            existing_content = ""
            if readme_path.exists():
                existing_content = readme_path.read_text(encoding="utf-8")
            
            # Intelligentes Merging: Behalte benutzerdefinierte Inhalte
            new_content = self._merge_readme(template, existing_content, project_name, project_type)
            
            # README schreiben
            readme_path.write_text(new_content, encoding="utf-8")
            
            self.log(f"  → Aktualisiert ✓", "UPDATE")
            self.updated_count += 1
            return True
            
        except Exception as e:
            self.log(f"  → Fehler: {e}", "ERROR")
            self.error_count += 1
            return False
    
    def _merge_readme(self, template: str, existing: str, project_name: str, project_type: str) -> str:
        """Merged Template mit bestehendem Inhalt."""
        # Platzhalter ersetzen
        result = template
        
        # Projekt-spezifische Ersetzungen
        replacements = {
            "[PROJEKTNAME]": project_name,
            "[SKILL-NAME]": project_name,
            "[WEBAPP-NAME]": project_name,
            "[API-NAME]": project_name,
            "[TOOL-NAME]": project_name,
            "[projektname]": project_name.lower().replace(" ", "-").replace("_", "-"),
            "[skill-name]": project_name.lower().replace(" ", "-").replace("_", "-"),
            "YYYY-MM-DD": datetime.now().strftime("%Y-%m-%d"),
        }
        
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        
        # Wenn bestehender Inhalt vorhanden, versuche wichtige Abschnitte zu erhalten
        if existing:
            # Extrahiere benutzerdefinierte Beschreibungen
            import re
            
            # Übersicht/Description aus bestehendem README
            overview_match = re.search(r'## Übersicht\n\n(.+?)(?=\n##|\n---|\Z)', existing, re.DOTALL)
            if overview_match:
                custom_overview = overview_match.group(1).strip()
                if custom_overview and "[" not in custom_overview[:50]:
                    result = re.sub(
                        r'## Übersicht\n\n\[.+?\]',
                        f'## Übersicht\n\n{custom_overview}',
                        result,
                        flags=re.DOTALL
                    )
        
        return result
    
    def find_projects(self) -> List[Dict]:
        """Findet alle Projekte im Repository."""
        projects = []
        
        # Hauptprojekt
        if (self.repo_path / "README.md").exists() or any(
            (self.repo_path / f).exists() for f in ["package.json", "requirements.txt", "setup.py"]
        ):
            projects.append({
                "name": self.repo_path.name,
                "path": self.repo_path,
                "type": "main"
            })
        
        # Skills-Verzeichnis
        skills_dir = self.repo_path / "skills"
        if skills_dir.exists():
            for skill_path in skills_dir.iterdir():
                if skill_path.is_dir() and not skill_path.name.startswith('.'):
                    projects.append({
                        "name": skill_path.name,
                        "path": skill_path,
                        "type": "skill"
                    })
        
        # Agents-Verzeichnis
        agents_dir = self.repo_path / "agents"
        if agents_dir.exists():
            for agent_path in agents_dir.iterdir():
                if agent_path.is_dir() and not agent_path.name.startswith('.'):
                    projects.append({
                        "name": agent_path.name,
                        "path": agent_path,
                        "type": "agent"
                    })
        
        # Weitere Unterverzeichnisse mit README
        for subdir in self.repo_path.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                if subdir.name not in ['skills', 'agents', 'docs', 'tests', '__pycache__', 'node_modules']:
                    if (subdir / "README.md").exists():
                        projects.append({
                            "name": subdir.name,
                            "path": subdir,
                            "type": "subproject"
                        })
        
        return projects
    
    def run(self) -> Dict:
        """Führt die Aktualisierung aller Projekte durch."""
        self.log(f"=== FassadenFix README Auto-Updater ===")
        self.log(f"Repository: {self.repo_path}")
        self.log(f"Modus: {'Dry-Run' if self.dry_run else 'Live'}")
        self.log(f"Force: {self.force}")
        self.log("")
        
        projects = self.find_projects()
        self.log(f"Gefundene Projekte: {len(projects)}")
        self.log("")
        
        for project in projects:
            self.update_readme(project["path"], project["name"])
        
        self.log("")
        self.log("=== Zusammenfassung ===")
        self.log(f"Aktualisiert: {self.updated_count}")
        self.log(f"Übersprungen: {self.skipped_count}")
        self.log(f"Fehler: {self.error_count}")
        
        return {
            "updated": self.updated_count,
            "skipped": self.skipped_count,
            "errors": self.error_count,
            "total": len(projects),
            "log": self.log_entries
        }


def main():
    parser = argparse.ArgumentParser(
        description="FassadenFix README Auto-Updater",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--repo-path", "-r",
        default="/home/ubuntu/FaFi",
        help="Pfad zum Repository (Standard: /home/ubuntu/FaFi)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Vorschau ohne Änderungen"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Alle READMEs neu generieren"
    )
    parser.add_argument(
        "--output-log", "-o",
        help="Pfad für Log-Datei"
    )
    
    args = parser.parse_args()
    
    updater = ReadmeUpdater(
        repo_path=args.repo_path,
        dry_run=args.dry_run,
        force=args.force
    )
    
    result = updater.run()
    
    # Log speichern wenn gewünscht
    if args.output_log:
        log_path = Path(args.output_log)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text('\n'.join(result['log']), encoding='utf-8')
        print(f"\nLog gespeichert: {args.output_log}")
    
    # Exit-Code basierend auf Ergebnis
    sys.exit(0 if result['errors'] == 0 else 1)


if __name__ == "__main__":
    main()
