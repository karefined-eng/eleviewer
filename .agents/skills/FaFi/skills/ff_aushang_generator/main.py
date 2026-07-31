#!/usr/bin/env python3
"""
FassadenFix Aushang-Generator
Generiert standortspezifische Mieterinformationen und Aushänge.
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
FF_WHITE = (255, 255, 255)

# Vordefinierte Textbausteine
TEXTBAUSTEINE = {
    "intro_standard": """Sehr geehrte Mieterinnen und Mieter,

in Kuerze werden an Ihrem WohnGebaeude professionelle Fassadenreinigungsarbeiten durchgefuehrt. 
Diese Massnahme dient der Werterhaltung und Verschoenerung Ihrer Wohnanlage.""",

    "intro_algen": """Sehr geehrte Mieterinnen und Mieter,

an Ihrem Wohngebaeude werden professionelle Fassadenreinigungsarbeiten zur Entfernung von 
Algen- und Pilzbefall durchgefuehrt. Diese Massnahme verbessert nicht nur das Erscheinungsbild, 
sondern schuetzt auch die Bausubstanz langfristig.""",

    "zeitraum": """Die Arbeiten werden voraussichtlich im Zeitraum vom {start_datum} bis {end_datum} durchgefuehrt.""",

    "hinweise_standard": """Bitte beachten Sie waehrend der Arbeiten folgende Hinweise:
- Halten Sie Fenster und Tueren geschlossen
- Parken Sie nicht unmittelbar vor dem Gebaeude
- Entfernen Sie empfindliche Gegenstaende von Balkonen und Terrassen""",

    "hinweise_hubbuehne": """Bitte beachten Sie waehrend der Arbeiten folgende Hinweise:
- Halten Sie Fenster und Tueren geschlossen
- Der Einsatz von Hubarbeitsbuehnen kann zu kurzzeitigen Einschraenkungen fuehren
- Parken Sie nicht im gekennzeichneten Arbeitsbereich
- Entfernen Sie empfindliche Gegenstaende von Balkonen und Terrassen""",

    "abschluss": """Wir bitten um Ihr Verstaendnis und bedanken uns fuer Ihre Kooperation.

Bei Fragen wenden Sie sich bitte an:
{ansprechpartner}
Tel.: {telefon}
E-Mail: {email}""",

    "abschluss_kurz": """Wir bitten um Ihr Verstaendnis und bedanken uns fuer Ihre Kooperation.

Mit freundlichen Gruessen
Ihr FassadenFix-Team"""
}


@dataclass
class Projektdaten:
    """Projektdaten fuer den Aushang"""
    ort: str = ""
    strasse: str = ""
    hausnummer: str = ""
    plz: str = ""
    start_datum: str = ""
    end_datum: str = ""
    ansprechpartner: str = ""
    telefon: str = ""
    email: str = ""


@dataclass
class AushangKonfiguration:
    """Konfiguration fuer den Aushang"""
    titel: str = "Mieterinformation"
    intro_baustein: str = "intro_standard"
    hinweise_baustein: str = "hinweise_standard"
    abschluss_baustein: str = "abschluss_kurz"
    zusatztext: str = ""
    qr_code_pfad: Optional[str] = None


@dataclass
class Aushang:
    """Vollständiger Aushang"""
    projekt: Projektdaten = field(default_factory=Projektdaten)
    konfiguration: AushangKonfiguration = field(default_factory=AushangKonfiguration)
    erstellungsdatum: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, path: Optional[Path] = None) -> str:
        data = self.to_dict()
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        if path:
            path.write_text(json_str, encoding="utf-8")
        return json_str


class AushangPDF(FPDF):
    """PDF-Generator fuer Mieteraushange im FassadenFix Design"""

    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # Logo-Bereich
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(*FF_GREEN)
        self.cell(0, 12, "FASSADENFIX", align="L")
        self.ln(10)
        
        # Trennlinie
        self.set_draw_color(*FF_GREEN)
        self.set_line_width(1)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 10, "FassadenFix | Professionelle Fassadenreinigung | www.fassadenfix.de", align="C")

    def titel(self, text: str):
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 15, text, ln=True, align="C")
        self.ln(5)

    def standort(self, ort: str, strasse: str, hausnummer: str):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*FF_GREEN)
        self.cell(0, 10, f"{strasse} {hausnummer}", ln=True, align="C")
        self.set_font("Helvetica", "", 12)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 8, ort, ln=True, align="C")
        self.ln(10)

    def textblock(self, text: str):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(*FF_GRAY)
        self.multi_cell(0, 7, text)
        self.ln(5)

    def zeitraum_box(self, start: str, ende: str):
        # Hintergrund
        self.set_fill_color(*FF_GREEN)
        self.set_text_color(*FF_WHITE)
        self.set_font("Helvetica", "B", 12)
        
        y = self.get_y()
        self.rect(10, y, 190, 20, "F")
        self.set_xy(10, y + 5)
        self.cell(190, 10, f"Zeitraum: {start} bis {ende}", align="C")
        self.ln(25)
        self.set_text_color(*FF_GRAY)

    def hinweis_liste(self, text: str):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(*FF_GRAY)
        
        lines = text.strip().split("\n")
        for line in lines:
            if line.strip().startswith("•"):
                self.set_x(15)
            self.multi_cell(0, 6, line.strip())
        self.ln(5)

    def kontakt_box(self, name: str, telefon: str, email: str):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 8, "Ihr Ansprechpartner:", ln=True)
        
        self.set_font("Helvetica", "", 11)
        self.cell(0, 6, f"  {name}", ln=True)
        if telefon:
            self.cell(0, 6, f"  Tel.: {telefon}", ln=True)
        if email:
            self.cell(0, 6, f"  E-Mail: {email}", ln=True)
        self.ln(5)


def generate_aushang_pdf(aushang: Aushang, output_path: Path) -> Path:
    """Generiert ein PDF-Dokument fuer den Aushang."""
    pdf = AushangPDF()
    
    # Titel
    pdf.titel(aushang.konfiguration.titel)
    
    # Standort
    pdf.standort(
        aushang.projekt.ort,
        aushang.projekt.strasse,
        aushang.projekt.hausnummer
    )
    
    # Intro-Text
    intro = TEXTBAUSTEINE.get(aushang.konfiguration.intro_baustein, "")
    pdf.textblock(intro)
    
    # Zeitraum
    if aushang.projekt.start_datum and aushang.projekt.end_datum:
        pdf.zeitraum_box(aushang.projekt.start_datum, aushang.projekt.end_datum)
    
    # Hinweise
    hinweise = TEXTBAUSTEINE.get(aushang.konfiguration.hinweise_baustein, "")
    pdf.hinweis_liste(hinweise)
    
    # Zusatztext
    if aushang.konfiguration.zusatztext:
        pdf.textblock(aushang.konfiguration.zusatztext)
    
    # Abschluss
    abschluss = TEXTBAUSTEINE.get(aushang.konfiguration.abschluss_baustein, "")
    if "{ansprechpartner}" in abschluss:
        abschluss = abschluss.format(
            ansprechpartner=aushang.projekt.ansprechpartner,
            telefon=aushang.projekt.telefon,
            email=aushang.projekt.email
        )
    pdf.textblock(abschluss)
    
    # Speichern
    pdf.output(str(output_path))
    return output_path


def interactive_aushang() -> Aushang:
    """Interaktive Erfassung der Aushangdaten über die Kommandozeile."""
    print("\n" + "=" * 60)
    print("  FASSADENFIX AUSHANG-GENERATOR")
    print("=" * 60)

    aushang = Aushang()

    # Projektdaten
    print("\n--- STANDORT ---")
    aushang.projekt.ort = input("Ort (z.B. 12345 Musterstadt): ").strip()
    aushang.projekt.strasse = input("Straße: ").strip()
    aushang.projekt.hausnummer = input("Hausnummer: ").strip()

    # Zeitraum
    print("\n--- ZEITRAUM ---")
    aushang.projekt.start_datum = input("Startdatum (z.B. 15.02.2026): ").strip()
    aushang.projekt.end_datum = input("Enddatum (z.B. 20.02.2026): ").strip()

    # Textbausteine
    print("\n--- TEXTBAUSTEINE ---")
    print("Intro-Varianten:")
    print("  1) Standard")
    print("  2) Algen/Pilzbefall")
    intro_wahl = input("Auswahl (1/2): ").strip()
    aushang.konfiguration.intro_baustein = "intro_algen" if intro_wahl == "2" else "intro_standard"

    print("\nHinweise-Varianten:")
    print("  1) Standard")
    print("  2) Mit Hubarbeitsbühne")
    hinweise_wahl = input("Auswahl (1/2): ").strip()
    aushang.konfiguration.hinweise_baustein = "hinweise_hubbuehne" if hinweise_wahl == "2" else "hinweise_standard"

    # Ansprechpartner
    print("\n--- ANSPRECHPARTNER (optional) ---")
    aushang.projekt.ansprechpartner = input("Name: ").strip()
    if aushang.projekt.ansprechpartner:
        aushang.projekt.telefon = input("Telefon: ").strip()
        aushang.projekt.email = input("E-Mail: ").strip()
        aushang.konfiguration.abschluss_baustein = "abschluss"
    else:
        aushang.konfiguration.abschluss_baustein = "abschluss_kurz"

    # Zusatztext
    print("\n--- ZUSATZTEXT (optional) ---")
    aushang.konfiguration.zusatztext = input("Zusaetzlicher Text (Enter fuer keinen): ").strip()

    return aushang


def main():
    """Hauptfunktion fuer den interaktiven Aushang-Generator."""
    aushang = interactive_aushang()

    # Dateiname generieren
    safe_ort = aushang.projekt.ort.replace(" ", "_").replace(",", "")[:20]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # JSON speichern
    json_path = Path(f"aushang_{safe_ort}_{timestamp}.json")
    aushang.to_json(json_path)
    print(f"\n✓ JSON gespeichert: {json_path}")

    # PDF generieren
    pdf_path = Path(f"aushang_{safe_ort}_{timestamp}.pdf")
    generate_aushang_pdf(aushang, pdf_path)
    print(f"✓ PDF generiert: {pdf_path}")

    print("\n" + "=" * 60)
    print("  AUSHANG ERSTELLT")
    print("=" * 60)


if __name__ == "__main__":
    main()
