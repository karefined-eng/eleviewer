#!/usr/bin/env python3
"""
FassadenFix Branding Skill - Wettkampf-Testdurchlauf
=====================================================
Vollständiger Test unter "Wettkampfbedingungen" mit allen Szenarien.
"""

import sys
import os
import json
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skills', 'fassadenfix_branding'))

from skills.fassadenfix_branding.main import (
    execute, check_opt_out, is_default_enabled, get_priority, get_scope,
    get_color, get_font_import, COLORS, TYPOGRAPHY, SPACING, BORDER_RADIUS, SHADOWS
)

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        self.start_time = time.time()
    
    def add_result(self, name, passed, details=""):
        self.tests.append({
            "name": name,
            "passed": passed,
            "details": details
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        elapsed = time.time() - self.start_time
        total = self.passed + self.failed
        
        print("\n" + "=" * 70)
        print("🏆 WETTKAMPF-ERGEBNISSE")
        print("=" * 70)
        
        for test in self.tests:
            status = "✅ PASS" if test["passed"] else "❌ FAIL"
            print(f"{status} | {test['name']}")
            if test["details"] and not test["passed"]:
                print(f"       └─ {test['details']}")
        
        print("\n" + "-" * 70)
        print(f"📊 Gesamt: {self.passed}/{total} Tests bestanden ({self.passed/total*100:.1f}%)")
        print(f"⏱️  Zeit: {elapsed:.2f} Sekunden")
        
        if self.failed == 0:
            print("\n🎉 ALLE TESTS BESTANDEN - WETTKAMPF GEWONNEN!")
        else:
            print(f"\n⚠️  {self.failed} Test(s) fehlgeschlagen")
        
        return self.failed == 0


def run_competition_tests():
    """Führt alle Wettkampf-Tests durch."""
    
    results = TestResults()
    
    print("=" * 70)
    print("🏁 FASSADENFIX BRANDING SKILL - WETTKAMPF-DURCHLAUF")
    print("=" * 70)
    print()
    
    # =========================================================================
    # KATEGORIE 1: Skill-Metadaten und Konfiguration
    # =========================================================================
    print("📋 KATEGORIE 1: Skill-Metadaten und Konfiguration")
    print("-" * 50)
    
    # Test 1.1: Standard-Aktivierung
    test_name = "1.1 Standard-Aktivierung (default_enabled)"
    try:
        enabled = is_default_enabled()
        results.add_result(test_name, enabled == True, f"Erwartet: True, Erhalten: {enabled}")
    except Exception as e:
        results.add_result(test_name, False, str(e))
    
    # Test 1.2: Priorität
    test_name = "1.2 Höchste Priorität (100)"
    try:
        priority = get_priority()
        results.add_result(test_name, priority == 100, f"Erwartet: 100, Erhalten: {priority}")
    except Exception as e:
        results.add_result(test_name, False, str(e))
    
    # Test 1.3: Globaler Geltungsbereich
    test_name = "1.3 Globaler Geltungsbereich"
    try:
        scope = get_scope()
        results.add_result(test_name, scope == "global", f"Erwartet: global, Erhalten: {scope}")
    except Exception as e:
        results.add_result(test_name, False, str(e))
    
    print()
    
    # =========================================================================
    # KATEGORIE 2: Farbpalette
    # =========================================================================
    print("🎨 KATEGORIE 2: Farbpalette")
    print("-" * 50)
    
    # Test 2.1: Primärfarbe
    test_name = "2.1 Primärfarbe (FassadenFix Grün)"
    expected_color = "#77bc1f"
    actual_color = get_color("primary")
    results.add_result(test_name, actual_color == expected_color, 
                      f"Erwartet: {expected_color}, Erhalten: {actual_color}")
    
    # Test 2.2: Sekundärfarbe
    test_name = "2.2 Sekundärfarbe (Dunkelgrau)"
    expected_color = "#4e5758"
    actual_color = get_color("secondary")
    results.add_result(test_name, actual_color == expected_color,
                      f"Erwartet: {expected_color}, Erhalten: {actual_color}")
    
    # Test 2.3: Alle Farben vorhanden
    test_name = "2.3 Vollständige Farbpalette (≥10 Farben)"
    color_count = len(COLORS)
    results.add_result(test_name, color_count >= 10,
                      f"Erwartet: ≥10, Erhalten: {color_count}")
    
    # Test 2.4: Farbvarianten
    test_name = "2.4 Farbvarianten (dark/light)"
    has_variants = "primary_dark" in COLORS and "primary_light" in COLORS
    results.add_result(test_name, has_variants,
                      f"primary_dark: {'✓' if 'primary_dark' in COLORS else '✗'}, primary_light: {'✓' if 'primary_light' in COLORS else '✗'}")
    
    print()
    
    # =========================================================================
    # KATEGORIE 3: Typografie
    # =========================================================================
    print("📝 KATEGORIE 3: Typografie")
    print("-" * 50)
    
    # Test 3.1: Schriftfamilie
    test_name = "3.1 Schriftfamilie (Raleway)"
    font_family = TYPOGRAPHY.get("font_family", "")
    results.add_result(test_name, "Raleway" in font_family,
                      f"Erhalten: {font_family}")
    
    # Test 3.2: Font-Import
    test_name = "3.2 Google Fonts Import-Link"
    font_import = get_font_import()
    results.add_result(test_name, "fonts.googleapis.com" in font_import and "Raleway" in font_import,
                      f"Import vorhanden: {'✓' if 'fonts.googleapis.com' in font_import else '✗'}")
    
    # Test 3.3: Font-Gewichte
    test_name = "3.3 Font-Gewichte (regular, medium, bold)"
    weights = TYPOGRAPHY.get("weights", {})
    has_weights = all(w in weights for w in ["regular", "medium", "bold"])
    results.add_result(test_name, has_weights,
                      f"Gewichte: {list(weights.keys())}")
    
    # Test 3.4: Font-Größen
    test_name = "3.4 Font-Größen (xs bis 5xl)"
    sizes = TYPOGRAPHY.get("sizes", {})
    has_sizes = len(sizes) >= 7
    results.add_result(test_name, has_sizes,
                      f"Größen: {len(sizes)}")
    
    print()
    
    # =========================================================================
    # KATEGORIE 4: Design-System-Token
    # =========================================================================
    print("📐 KATEGORIE 4: Design-System-Token")
    print("-" * 50)
    
    # Test 4.1: Spacing
    test_name = "4.1 Spacing-System (xs bis 3xl)"
    has_spacing = len(SPACING) >= 7
    results.add_result(test_name, has_spacing,
                      f"Spacing-Stufen: {len(SPACING)}")
    
    # Test 4.2: Border-Radius
    test_name = "4.2 Border-Radius (sm bis full)"
    has_radius = len(BORDER_RADIUS) >= 4
    results.add_result(test_name, has_radius,
                      f"Radius-Stufen: {len(BORDER_RADIUS)}")
    
    # Test 4.3: Shadows
    test_name = "4.3 Schatten (sm bis xl)"
    has_shadows = len(SHADOWS) >= 4
    results.add_result(test_name, has_shadows,
                      f"Schatten-Stufen: {len(SHADOWS)}")
    
    print()
    
    # =========================================================================
    # KATEGORIE 5: Ausgabeformate
    # =========================================================================
    print("📦 KATEGORIE 5: Ausgabeformate")
    print("-" * 50)
    
    # Test 5.1: CSS-Generierung
    test_name = "5.1 CSS-Generierung"
    try:
        result = execute(output_format="css")
        css_valid = (
            result["branding_applied"] == True and
            len(result["styles"]) > 1000 and
            "--ff-green" in result["styles"] and
            ":root" in result["styles"]
        )
        results.add_result(test_name, css_valid,
                          f"Länge: {len(result['styles'])} Zeichen, Variablen: {'✓' if '--ff-green' in result['styles'] else '✗'}")
    except Exception as e:
        results.add_result(test_name, False, str(e))
    
    # Test 5.2: Tailwind-Generierung
    test_name = "5.2 Tailwind-Konfiguration"
    try:
        result = execute(output_format="tailwind")
        tailwind_valid = (
            result["branding_applied"] == True and
            "module.exports" in result["styles"] and
            "ff-green" in result["styles"]
        )
        results.add_result(test_name, tailwind_valid,
                          f"Länge: {len(result['styles'])} Zeichen")
    except Exception as e:
        results.add_result(test_name, False, str(e))
    
    # Test 5.3: SCSS-Generierung
    test_name = "5.3 SCSS-Variablen"
    try:
        result = execute(output_format="scss")
        scss_valid = (
            result["branding_applied"] == True and
            "$ff-green" in result["styles"]
        )
        results.add_result(test_name, scss_valid,
                          f"Länge: {len(result['styles'])} Zeichen")
    except Exception as e:
        results.add_result(test_name, False, str(e))
    
    # Test 5.4: JSON-Generierung
    test_name = "5.4 JSON-Export"
    try:
        result = execute(output_format="json")
        json_data = json.loads(result["styles"])
        json_valid = (
            result["branding_applied"] == True and
            "colors" in json_data and
            "typography" in json_data
        )
        results.add_result(test_name, json_valid,
                          f"Keys: {list(json_data.keys())}")
    except Exception as e:
        results.add_result(test_name, False, str(e))
    
    print()
    
    # =========================================================================
    # KATEGORIE 6: Opt-Out-Mechanismus
    # =========================================================================
    print("🚫 KATEGORIE 6: Opt-Out-Mechanismus")
    print("-" * 50)
    
    opt_out_cases = [
        ("6.1 Opt-Out: --no-branding", "--no-branding", True),
        ("6.2 Opt-Out: ohne FassadenFix Branding", "Erstelle ohne FassadenFix Branding", True),
        ("6.3 Opt-Out: abweichendes Design", "abweichendes Design verwenden", True),
        ("6.4 Opt-Out: custom branding", "use custom branding", True),
        ("6.5 Kein Opt-Out: normale Anfrage", "Erstelle eine Webanwendung", False),
        ("6.6 Kein Opt-Out: mit Branding", "Erstelle mit FassadenFix Design", False),
    ]
    
    for test_name, context, expected_opt_out in opt_out_cases:
        actual_opt_out = check_opt_out(context)
        results.add_result(test_name, actual_opt_out == expected_opt_out,
                          f"Erwartet: {expected_opt_out}, Erhalten: {actual_opt_out}")
    
    # Test 6.7: Opt-Out via execute
    test_name = "6.7 Opt-Out via execute()"
    try:
        result = execute(context="ohne FassadenFix Branding")
        opt_out_works = result["branding_applied"] == False
        results.add_result(test_name, opt_out_works,
                          f"branding_applied: {result['branding_applied']}")
    except Exception as e:
        results.add_result(test_name, False, str(e))
    
    # Test 6.8: Opt-Out via Parameter
    test_name = "6.8 Opt-Out via apply_branding=False"
    try:
        result = execute(apply_branding=False)
        opt_out_works = result["branding_applied"] == False
        results.add_result(test_name, opt_out_works,
                          f"branding_applied: {result['branding_applied']}")
    except Exception as e:
        results.add_result(test_name, False, str(e))
    
    print()
    
    # =========================================================================
    # KATEGORIE 7: Integration und Vollständigkeit
    # =========================================================================
    print("🔗 KATEGORIE 7: Integration und Vollständigkeit")
    print("-" * 50)
    
    # Test 7.1: Vollständige Rückgabe
    test_name = "7.1 Vollständige Rückgabe-Struktur"
    try:
        result = execute()
        required_keys = ["styles", "colors", "typography", "branding_applied", "font_import", "message"]
        has_all_keys = all(k in result for k in required_keys)
        results.add_result(test_name, has_all_keys,
                          f"Keys: {list(result.keys())}")
    except Exception as e:
        results.add_result(test_name, False, str(e))
    
    # Test 7.2: Konsistente Farbwerte
    test_name = "7.2 Konsistente Farbwerte (HEX-Format)"
    all_hex = all(c.startswith("#") and len(c) == 7 for c in COLORS.values())
    results.add_result(test_name, all_hex,
                      f"Alle HEX: {'✓' if all_hex else '✗'}")
    
    # Test 7.3: CSS-Variablen-Konsistenz
    test_name = "7.3 CSS-Variablen-Konsistenz"
    try:
        result = execute(output_format="css")
        css = result["styles"]
        has_ff_vars = "--ff-green" in css and "--ff-gray" in css
        has_color_vars = "--color-primary" in css and "--color-secondary" in css
        results.add_result(test_name, has_ff_vars and has_color_vars,
                          f"FF-Vars: {'✓' if has_ff_vars else '✗'}, Color-Vars: {'✓' if has_color_vars else '✗'}")
    except Exception as e:
        results.add_result(test_name, False, str(e))
    
    # Test 7.4: UI-Komponenten im CSS
    test_name = "7.4 UI-Komponenten (Buttons, Cards, Nav)"
    try:
        result = execute(output_format="css")
        css = result["styles"]
        has_components = (
            ".btn-primary" in css and
            ".btn-secondary" in css and
            ".card" in css and
            ".nav" in css
        )
        results.add_result(test_name, has_components,
                          f"Komponenten vorhanden: {'✓' if has_components else '✗'}")
    except Exception as e:
        results.add_result(test_name, False, str(e))
    
    print()
    
    # =========================================================================
    # KATEGORIE 8: Performance und Robustheit
    # =========================================================================
    print("⚡ KATEGORIE 8: Performance und Robustheit")
    print("-" * 50)
    
    # Test 8.1: Schnelle Ausführung
    test_name = "8.1 Schnelle Ausführung (<100ms)"
    start = time.time()
    for _ in range(10):
        execute(output_format="css")
    elapsed = (time.time() - start) / 10 * 1000
    results.add_result(test_name, elapsed < 100,
                      f"Durchschnitt: {elapsed:.2f}ms")
    
    # Test 8.2: Fehlertoleranz bei leerem Kontext
    test_name = "8.2 Fehlertoleranz (leerer Kontext)"
    try:
        result = execute(context="")
        results.add_result(test_name, result["branding_applied"] == True,
                          "Leerer Kontext wird als Opt-In behandelt")
    except Exception as e:
        results.add_result(test_name, False, str(e))
    
    # Test 8.3: Fehlertoleranz bei None-Werten
    test_name = "8.3 Fehlertoleranz (None-Werte)"
    try:
        result = execute(components=None)
        results.add_result(test_name, result["branding_applied"] == True,
                          "None-Werte werden toleriert")
    except Exception as e:
        results.add_result(test_name, False, str(e))
    
    # Test 8.4: Unbekanntes Format-Fallback
    test_name = "8.4 Fallback bei unbekanntem Format"
    try:
        result = execute(output_format="unknown")
        # Sollte auf CSS zurückfallen
        results.add_result(test_name, ":root" in result["styles"],
                          "Fallback zu CSS funktioniert")
    except Exception as e:
        results.add_result(test_name, False, str(e))
    
    print()
    
    # =========================================================================
    # ABSCHLUSS
    # =========================================================================
    return results.print_summary()


if __name__ == "__main__":
    success = run_competition_tests()
    sys.exit(0 if success else 1)
