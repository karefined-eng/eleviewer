#!/usr/bin/env python3
"""
FassadenFix README Validator

Prüft README-Dateien auf Einhaltung der FassadenFix CI-Richtlinien.

Verwendung:
    python validate_readme.py <readme-pfad>
    python validate_readme.py /path/to/README.md
"""

import sys
import re
from pathlib import Path


# FassadenFix CI-Konstanten
FF_GREEN = "#77bc1f"
FF_GRAY = "#4e5758"
FF_LOGO_PATTERNS = [
    "FassadenFix_Logo",
    "fassadenfix-assets/templates/logos"
]
FF_BADGE_COLOR = "77bc1f"


def validate_readme(readme_path: str) -> dict:
    """Validiert eine README-Datei gegen FassadenFix CI-Richtlinien."""
    
    results = {
        "valid": True,
        "score": 100,
        "checks": [],
        "warnings": [],
        "errors": []
    }
    
    path = Path(readme_path)
    
    if not path.exists():
        results["valid"] = False
        results["errors"].append(f"Datei nicht gefunden: {readme_path}")
        results["score"] = 0
        return results
    
    content = path.read_text(encoding="utf-8")
    
    # Check 1: Logo-Verwendung
    logo_found = any(pattern in content for pattern in FF_LOGO_PATTERNS)
    if logo_found:
        results["checks"].append("✅ FassadenFix Logo gefunden")
    else:
        results["warnings"].append("⚠️ Kein FassadenFix Logo gefunden")
        results["score"] -= 10
    
    # Check 2: CI-Farben in Badges
    if FF_BADGE_COLOR in content.lower():
        results["checks"].append("✅ CI-konforme Badge-Farbe (#77bc1f) verwendet")
    else:
        results["warnings"].append("⚠️ CI-konforme Badge-Farbe nicht gefunden")
        results["score"] -= 5
    
    # Check 3: Pflichtabschnitte
    required_sections = ["## Übersicht", "## Installation", "## Verwendung"]
    alt_sections = ["## Overview", "## Installation", "## Usage"]
    
    for section, alt in zip(required_sections, alt_sections):
        if section.lower() in content.lower() or alt.lower() in content.lower():
            results["checks"].append(f"✅ Abschnitt '{section}' vorhanden")
        else:
            results["warnings"].append(f"⚠️ Abschnitt '{section}' fehlt")
            results["score"] -= 10
    
    # Check 4: Kontaktinformationen
    if "fassadenfix.de" in content.lower():
        results["checks"].append("✅ FassadenFix Kontaktinformationen vorhanden")
    else:
        results["warnings"].append("⚠️ FassadenFix Kontaktinformationen fehlen")
        results["score"] -= 5
    
    # Check 5: Footer/Branding
    footer_patterns = ["Erstellt mit", "FassadenFix", "💚"]
    footer_found = sum(1 for p in footer_patterns if p in content)
    if footer_found >= 2:
        results["checks"].append("✅ FassadenFix Footer/Branding vorhanden")
    else:
        results["warnings"].append("⚠️ FassadenFix Footer/Branding unvollständig")
        results["score"] -= 5
    
    # Check 6: Markdown-Qualität
    # Überschriften-Hierarchie
    h1_count = len(re.findall(r'^# ', content, re.MULTILINE))
    if h1_count == 1:
        results["checks"].append("✅ Korrekte H1-Überschrift (genau eine)")
    elif h1_count == 0:
        results["warnings"].append("⚠️ Keine H1-Überschrift gefunden")
        results["score"] -= 5
    else:
        results["warnings"].append(f"⚠️ Mehrere H1-Überschriften ({h1_count})")
        results["score"] -= 5
    
    # Check 7: Code-Blöcke
    code_blocks = len(re.findall(r'```', content))
    if code_blocks >= 2:
        results["checks"].append("✅ Code-Beispiele vorhanden")
    else:
        results["warnings"].append("⚠️ Wenige/keine Code-Beispiele")
        results["score"] -= 5
    
    # Check 8: Tabellen
    tables = len(re.findall(r'\|.*\|', content))
    if tables >= 3:
        results["checks"].append("✅ Tabellen für Übersichtlichkeit verwendet")
    else:
        results["warnings"].append("⚠️ Wenige Tabellen - FassadenFix bevorzugt tabellarische Darstellung")
        results["score"] -= 5
    
    # Gesamtbewertung
    results["score"] = max(0, results["score"])
    results["valid"] = results["score"] >= 60 and len(results["errors"]) == 0
    
    return results


def print_results(results: dict, readme_path: str):
    """Gibt die Validierungsergebnisse aus."""
    
    print("\n" + "=" * 60)
    print("FassadenFix README Validator")
    print("=" * 60)
    print(f"\nDatei: {readme_path}")
    print(f"Score: {results['score']}/100")
    print(f"Status: {'✅ GÜLTIG' if results['valid'] else '❌ UNGÜLTIG'}")
    
    if results["checks"]:
        print("\n--- Bestandene Prüfungen ---")
        for check in results["checks"]:
            print(f"  {check}")
    
    if results["warnings"]:
        print("\n--- Warnungen ---")
        for warning in results["warnings"]:
            print(f"  {warning}")
    
    if results["errors"]:
        print("\n--- Fehler ---")
        for error in results["errors"]:
            print(f"  {error}")
    
    print("\n" + "-" * 60)
    
    if results["score"] >= 80:
        print("🎉 Ausgezeichnet! Die README entspricht den FassadenFix CI-Richtlinien.")
    elif results["score"] >= 60:
        print("👍 Gut! Die README ist akzeptabel, aber es gibt Verbesserungspotenzial.")
    else:
        print("⚠️ Die README erfüllt nicht die FassadenFix CI-Mindestanforderungen.")
        print("   Bitte beheben Sie die oben genannten Probleme.")
    
    print("=" * 60 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Verwendung: python validate_readme.py <readme-pfad>")
        print("Beispiel:   python validate_readme.py ./README.md")
        sys.exit(1)
    
    readme_path = sys.argv[1]
    results = validate_readme(readme_path)
    print_results(results, readme_path)
    
    # Exit-Code basierend auf Validierung
    sys.exit(0 if results["valid"] else 1)


if __name__ == "__main__":
    main()
