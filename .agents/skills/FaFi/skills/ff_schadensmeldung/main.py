#!/usr/bin/env python3
"""
FassadenFix Schadensmeldung
Ermoeglicht schnelle und strukturierte digitale Schadensmeldungen.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, asdict, field
from fpdf import FPDF

# FassadenFix Branding Farben
FF_GREEN = (119, 188, 31)  # #77bc1f
FF_GRAY = (78, 87, 88)     # #4e5758
FF_RED = (220, 50, 50)     # Warnung
FF_WHITE = (255, 255, 255)

# Vordefinierte Schadensarten
SCHADENSARTEN = [
    "Algen-/Pilzbefall (Neubefall)",
    "Putzschaeden",
    "Farbschaeden",
    "Risse",
    "Abplatzungen",
    "Sonstige Schaeden"
]

# Dringlichkeitsstufen
DRINGLICHKEIT = ["Niedrig", "Mittel", "Hoch", "Kritisch"]


@dataclass
class Kontakt:
    """Kontaktdaten des Meldenden"""
    name: str = ""
    telefon: str = ""
    email: str = ""
    rolle: str = ""  # Kunde, Mieter, Mitarbeiter


@dataclass
class Schadensmeldung:
    """Vollstaendige Schadensmeldung"""
    meldungsnummer: str = ""
    datum: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    projektnummer: str = ""
    objektadresse: str = ""
    schadensart: str = ""
    beschreibung: str = ""
    dringlichkeit: str = "Mittel"
    fotos: List[str] = field(default_factory=list)
    standort_koordinaten: str = ""
    melder: Kontakt = field(default_factory=Kontakt)
    status: str = "Neu"  # Neu, In Bearbeitung, Abgeschlossen

    def __post_init__(self):
        if not self.meldungsnummer:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            self.meldungsnummer = f"SCH-{timestamp}"

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, path: Optional[Path] = None) -> str:
        data = self.to_dict()
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        if path:
            path.write_text(json_str, encoding="utf-8")
        return json_str


class SchadensmeldungPDF(FPDF):
    """PDF-Generator fuer Schadensmeldung im FassadenFix Design"""

    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # Logo-Bereich
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(*FF_GREEN)
        self.cell(0, 10, "FASSADENFIX", align="L")
        self.ln(8)
        
        # Untertitel
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 8, "SCHADENSMELDUNG", align="L")
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 10, "FassadenFix | Schadensmeldung | Vertraulich", align="C")

    def meldungskopf(self, meldung: 'Schadensmeldung'):
        # Meldungsnummer und Datum
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*FF_GRAY)
        self.cell(100, 6, f"Meldungsnummer: {meldung.meldungsnummer}", align="L")
        self.cell(0, 6, f"Datum: {meldung.datum}", align="R")
        self.ln(8)
        
        # Dringlichkeit mit Farbcodierung
        self.cell(100, 6, f"Projektnummer: {meldung.projektnummer}", align="L")
        
        # Dringlichkeits-Badge
        dring_farben = {
            "Niedrig": (100, 180, 100),
            "Mittel": (255, 200, 0),
            "Hoch": (255, 140, 0),
            "Kritisch": (220, 50, 50)
        }
        farbe = dring_farben.get(meldung.dringlichkeit, FF_GRAY)
        self.set_fill_color(*farbe)
        self.set_text_color(*FF_WHITE)
        self.cell(40, 6, f" {meldung.dringlichkeit} ", align="C", fill=True)
        self.ln(15)
        self.set_text_color(*FF_GRAY)

    def section(self, titel: str):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*FF_GREEN)
        self.cell(0, 8, titel, ln=True)
        self.set_draw_color(*FF_GREEN)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def feld(self, label: str, wert: str):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*FF_GRAY)
        self.cell(50, 6, f"{label}:", align="L")
        self.set_font("Helvetica", "", 9)
        self.cell(0, 6, wert, ln=True)

    def textblock(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*FF_GRAY)
        self.multi_cell(0, 6, text)
        self.ln(5)


def generate_schadensmeldung_pdf(meldung: Schadensmeldung, output_path: Path) -> Path:
    """Generiert ein PDF-Dokument fuer die Schadensmeldung."""
    pdf = SchadensmeldungPDF()
    
    # Kopfbereich
    pdf.meldungskopf(meldung)
    
    # Objektdaten
    pdf.section("Objektdaten")
    pdf.feld("Adresse", meldung.objektadresse)
    if meldung.standort_koordinaten:
        pdf.feld("Koordinaten", meldung.standort_koordinaten)
    pdf.ln(5)
    
    # Schadensbeschreibung
    pdf.section("Schadensbeschreibung")
    pdf.feld("Schadensart", meldung.schadensart)
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, "Beschreibung:", ln=True)
    pdf.textblock(meldung.beschreibung)
    
    # Fotos
    if meldung.fotos:
        pdf.section("Fotodokumentation")
        pdf.set_font("Helvetica", "", 9)
        for i, foto in enumerate(meldung.fotos, 1):
            pdf.cell(0, 6, f"  Foto {i}: {foto}", ln=True)
        pdf.ln(5)
    
    # Melder
    pdf.section("Meldende Person")
    pdf.feld("Name", meldung.melder.name)
    pdf.feld("Rolle", meldung.melder.rolle)
    if meldung.melder.telefon:
        pdf.feld("Telefon", meldung.melder.telefon)
    if meldung.melder.email:
        pdf.feld("E-Mail", meldung.melder.email)
    
    # Status
    pdf.ln(10)
    pdf.section("Status")
    pdf.feld("Aktueller Status", meldung.status)
    
    # Speichern
    pdf.output(str(output_path))
    return output_path


def interactive_schadensmeldung() -> Schadensmeldung:
    """Interaktive Erfassung einer Schadensmeldung."""
    print("\n" + "=" * 60)
    print("  FASSADENFIX SCHADENSMELDUNG")
    print("=" * 60)

    meldung = Schadensmeldung()

    # Objektdaten
    print("\n--- OBJEKTDATEN ---")
    meldung.projektnummer = input("Projektnummer (falls bekannt): ").strip()
    meldung.objektadresse = input("Objektadresse: ").strip()

    # Schaden
    print("\n--- SCHADENSBESCHREIBUNG ---")
    print("Schadensarten:")
    for i, art in enumerate(SCHADENSARTEN, 1):
        print(f"  {i}) {art}")
    art_wahl = input("Auswahl (1-6): ").strip()
    try:
        meldung.schadensart = SCHADENSARTEN[int(art_wahl) - 1]
    except (ValueError, IndexError):
        meldung.schadensart = "Sonstige Schaeden"
    
    meldung.beschreibung = input("Beschreibung des Schadens: ").strip()

    # Dringlichkeit
    print("\nDringlichkeit:")
    for i, d in enumerate(DRINGLICHKEIT, 1):
        print(f"  {i}) {d}")
    dring_wahl = input("Auswahl (1-4): ").strip()
    try:
        meldung.dringlichkeit = DRINGLICHKEIT[int(dring_wahl) - 1]
    except (ValueError, IndexError):
        meldung.dringlichkeit = "Mittel"

    # Melder
    print("\n--- KONTAKTDATEN ---")
    meldung.melder.name = input("Ihr Name: ").strip()
    meldung.melder.rolle = input("Ihre Rolle (Kunde/Mieter/Mitarbeiter): ").strip()
    meldung.melder.telefon = input("Telefon: ").strip()
    meldung.melder.email = input("E-Mail: ").strip()

    return meldung


def main():
    """Hauptfunktion fuer die interaktive Schadensmeldung."""
    meldung = interactive_schadensmeldung()

    # JSON speichern
    json_path = Path(f"schadensmeldung_{meldung.meldungsnummer}.json")
    meldung.to_json(json_path)
    print(f"\nJSON gespeichert: {json_path}")

    # PDF generieren
    pdf_path = Path(f"schadensmeldung_{meldung.meldungsnummer}.pdf")
    generate_schadensmeldung_pdf(meldung, pdf_path)
    print(f"PDF generiert: {pdf_path}")

    print("\n" + "=" * 60)
    print(f"  MELDUNG {meldung.meldungsnummer} ERFASST")
    print("=" * 60)


if __name__ == "__main__":
    main()
