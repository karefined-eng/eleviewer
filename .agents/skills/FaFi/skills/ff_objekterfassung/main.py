#!/usr/bin/env python3
"""
FassadenFix Objekterfassung - Digitaler Workflow
Erfasst Objektdaten für Fassadenprojekte und generiert ein PDF-Protokoll.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict, field
from fpdf import FPDF

# FassadenFix Branding Farben
FF_GREEN = (119, 188, 31)  # #77bc1f
FF_GRAY = (78, 87, 88)     # #4e5758


@dataclass
class Projekt:
    """Projektdaten"""
    anschrift: str = ""
    art_immobilie: str = ""
    putzart: str = ""
    datum: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))


@dataclass
class Zustand:
    """Zustandsdokumentation"""
    vorhandene_schaeden: str = ""
    notizen: str = ""


@dataclass
class Masse:
    """Gemessene Werte"""
    gemessene_werte: str = ""
    gesamtflaeche_qm: float = 0.0
    zu_reinigende_flaeche_qm: float = 0.0


@dataclass
class Checkliste:
    """Checkliste für Objektaufnahme"""
    rundgang_360_grad: bool = False
    gruenverschnitt_notwendig: bool = False
    strassensperrung_notwendig: str = ""


@dataclass
class Objektdaten:
    """Vollständige Objektdaten"""
    projekt: Projekt = field(default_factory=Projekt)
    zustand: Zustand = field(default_factory=Zustand)
    masse: Masse = field(default_factory=Masse)
    checkliste: Checkliste = field(default_factory=Checkliste)
    durchgefuehrt_durch: str = ""
    fotos: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, path: Optional[Path] = None) -> str:
        data = self.to_dict()
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        if path:
            path.write_text(json_str, encoding="utf-8")
        return json_str


class ObjekterfassungsPDF(FPDF):
    """PDF-Generator für Objektdatenblatt im FassadenFix Design"""

    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # Logo-Bereich (Platzhalter)
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(*FF_GREEN)
        self.cell(0, 10, "FASSADENFIX", align="L")
        self.ln(8)
        
        # Untertitel
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 8, "OBJEKTAUFNAHME", align="L")
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 10, f"FassadenFix | Seite {self.page_no()}", align="C")

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*FF_GREEN)
        self.cell(0, 10, title, ln=True)
        self.set_draw_color(*FF_GREEN)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def field(self, label: str, value: str):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*FF_GRAY)
        self.cell(60, 8, f"{label}:", align="L")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 8, str(value), ln=True)

    def checkbox(self, label: str, checked: bool):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*FF_GRAY)
        marker = "[X]" if checked else "[ ]"
        self.cell(0, 8, f"{marker} {label}", ln=True)

    def multiline_field(self, label: str, value: str):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 8, f"{label}:", ln=True)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, str(value))
        self.ln(3)


def generate_pdf(daten: Objektdaten, output_path: Path) -> Path:
    """Generiert ein PDF-Dokument aus den Objektdaten."""
    pdf = ObjekterfassungsPDF()

    # Datum
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*FF_GRAY)
    pdf.cell(0, 8, f"Datum: {daten.projekt.datum}", align="R", ln=True)
    pdf.ln(5)

    # Projektdaten
    pdf.section_title("Projektdaten")
    pdf.field("Anschrift", daten.projekt.anschrift)
    pdf.field("Art der Immobilie", daten.projekt.art_immobilie)
    pdf.field("Putzart", daten.projekt.putzart)
    pdf.ln(5)

    # Zustand
    pdf.section_title("Zustand & Besonderheiten")
    pdf.multiline_field("Vorhandene Schäden", daten.zustand.vorhandene_schaeden or "Keine")
    pdf.multiline_field("Notizen", daten.zustand.notizen or "-")
    pdf.ln(5)

    # Masse
    pdf.section_title("Gemessene Werte")
    pdf.multiline_field("Messwerte", daten.masse.gemessene_werte)
    pdf.field("Gesamtfläche (m²)", f"{daten.masse.gesamtflaeche_qm:.2f}")
    pdf.field("Zu reinigende Fläche (m²)", f"{daten.masse.zu_reinigende_flaeche_qm:.2f}")
    pdf.ln(5)

    # Checkliste
    pdf.section_title("Checkliste")
    pdf.checkbox("360 Grad Rundgang erstellt", daten.checkliste.rundgang_360_grad)
    pdf.checkbox("Grünverschnitt notwendig", daten.checkliste.gruenverschnitt_notwendig)
    if daten.checkliste.strassensperrung_notwendig:
        pdf.field("Straßensperrung notwendig", daten.checkliste.strassensperrung_notwendig)
    pdf.ln(5)

    # Durchgeführt durch
    pdf.section_title("Abschluss")
    pdf.field("Objektaufnahme durchgeführt durch", daten.durchgefuehrt_durch)

    # Speichern
    pdf.output(str(output_path))
    return output_path


def interactive_erfassung() -> Objektdaten:
    """Interaktive Erfassung der Objektdaten über die Kommandozeile."""
    print("\n" + "=" * 60)
    print("  FASSADENFIX OBJEKTERFASSUNG")
    print("=" * 60)

    daten = Objektdaten()

    # Projektdaten
    print("\n--- PROJEKTDATEN ---")
    daten.projekt.anschrift = input("Anschrift: ").strip()
    daten.projekt.art_immobilie = input("Art der Immobilie (z.B. Mehrfamilienhaus): ").strip()
    daten.projekt.putzart = input("Putzart (z.B. Silikatputz): ").strip()

    # Zustand
    print("\n--- ZUSTAND ---")
    daten.zustand.vorhandene_schaeden = input("Vorhandene Schäden (oder Enter für keine): ").strip()
    daten.zustand.notizen = input("Notizen/Besonderheiten: ").strip()

    # Masse
    print("\n--- GEMESSENE WERTE ---")
    daten.masse.gemessene_werte = input("Gemessene Werte (z.B. Nord: 10x15m): ").strip()
    try:
        daten.masse.gesamtflaeche_qm = float(input("Gesamtfläche in m²: ") or 0)
        daten.masse.zu_reinigende_flaeche_qm = float(input("Zu reinigende Fläche in m²: ") or 0)
    except ValueError:
        print("  (Ungültige Eingabe, setze auf 0)")

    # Checkliste
    print("\n--- CHECKLISTE ---")
    daten.checkliste.rundgang_360_grad = input("360° Rundgang erstellt? (j/n): ").lower() == "j"
    daten.checkliste.gruenverschnitt_notwendig = input("Grünverschnitt notwendig? (j/n): ").lower() == "j"
    daten.checkliste.strassensperrung_notwendig = input("Straßensperrung notwendig? (Beschreibung oder Enter): ").strip()

    # Abschluss
    print("\n--- ABSCHLUSS ---")
    daten.durchgefuehrt_durch = input("Durchgeführt durch: ").strip()

    return daten


def main():
    """Hauptfunktion für die interaktive Objekterfassung."""
    daten = interactive_erfassung()

    # JSON speichern
    json_path = Path(f"objekterfassung_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    daten.to_json(json_path)
    print(f"\n✓ JSON gespeichert: {json_path}")

    # PDF generieren
    pdf_path = Path(f"objekterfassung_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    generate_pdf(daten, pdf_path)
    print(f"✓ PDF generiert: {pdf_path}")

    print("\n" + "=" * 60)
    print("  OBJEKTERFASSUNG ABGESCHLOSSEN")
    print("=" * 60)


if __name__ == "__main__":
    main()
