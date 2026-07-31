#!/usr/bin/env python3
"""
FassadenFix HR-Einstellung
Digitaler Personalfragebogen fuer neue Mitarbeiter.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, asdict, field
from fpdf import FPDF

# FassadenFix Branding Farben
FF_GREEN = (119, 188, 31)
FF_GRAY = (78, 87, 88)
FF_WHITE = (255, 255, 255)

# Ausbildungsoptionen
AUSBILDUNG_OPTIONEN = [
    "Volks-/Hauptschule/mittlere Reife",
    "Abitur",
    "Fachschule/Fachhochschule",
    "Universitaetsabschluss"
]

# Steuerklassen
STEUERKLASSEN = ["I", "II", "III", "IV", "V", "VI"]


@dataclass
class Bankverbindung:
    """Bankdaten des Mitarbeiters"""
    iban: str = ""
    bic: str = ""
    bankname: str = ""


@dataclass
class Beschaeftigung:
    """Beschaeftigungsdaten"""
    eintrittsdatum: str = ""
    steuerklasse: str = "I"
    kinderfreibetraege: int = 0
    kirchensteuer: bool = False
    kirche: str = ""
    taetigkeit: str = ""
    ausbildung: str = ""
    berufsausbildung: bool = False
    urlaubsanspruch: int = 30
    woechentliche_arbeitszeit: float = 40.0


@dataclass
class Sozialversicherung:
    """Sozialversicherungsdaten"""
    krankenkasse: str = ""
    rv_nummer: str = ""
    kinder: bool = False


@dataclass
class Entlohnung:
    """Entlohnungsdaten"""
    bezeichnung: str = ""
    gueltig_ab: str = ""
    betrag: float = 0.0
    gleitzone: bool = False
    steuer_id: str = ""


@dataclass
class Personalfragebogen:
    """Vollstaendiger Personalfragebogen"""
    # Persoenliche Angaben
    familienname: str = ""
    vorname: str = ""
    strasse: str = ""
    plz_ort: str = ""
    geburtsdatum: str = ""
    geschlecht: str = ""
    staatsangehoerigkeit: str = "deutsch"
    familienstand: str = ""
    verheiratet: bool = False
    schwerbehindert: bool = False
    
    # Weitere Daten
    bank: Bankverbindung = field(default_factory=Bankverbindung)
    beschaeftigung: Beschaeftigung = field(default_factory=Beschaeftigung)
    sozialversicherung: Sozialversicherung = field(default_factory=Sozialversicherung)
    entlohnung: Entlohnung = field(default_factory=Entlohnung)
    
    # Dokumente
    dokumente: List[str] = field(default_factory=list)
    
    # Meta
    erstellt_am: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, path: Optional[Path] = None) -> str:
        data = self.to_dict()
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        if path:
            path.write_text(json_str, encoding="utf-8")
        return json_str

    def validate_iban(self) -> bool:
        """Einfache IBAN-Validierung"""
        iban = self.bank.iban.replace(" ", "").upper()
        if len(iban) < 15 or len(iban) > 34:
            return False
        if not iban[:2].isalpha():
            return False
        return True

    def validate_steuer_id(self) -> bool:
        """Validierung der Steuer-ID (11 Ziffern)"""
        steuer_id = self.entlohnung.steuer_id.replace(" ", "")
        return len(steuer_id) == 11 and steuer_id.isdigit()


class PersonalfragebogenPDF(FPDF):
    """PDF-Generator fuer Personalfragebogen im FassadenFix Design"""

    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 10, "Personalfragebogen (allgemein)", align="L")
        self.ln(8)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*FF_GREEN)
        self.cell(0, 8, "FASSADENFIX", align="L")
        self.ln(5)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*FF_GRAY)
        self.multi_cell(0, 4, "Bitte beachten Sie, dass wir Ihre Daten speichern, verarbeiten und bei Notwendigkeit an Behoerden weiter melden. Die Grundsaetze der DS-GVO werden eingehalten.")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 10, f"FassadenFix | Personalfragebogen | Stand: {datetime.now().strftime('%m/%Y')}", align="C")

    def section(self, titel: str):
        self.ln(5)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 8, titel, ln=True)
        self.set_draw_color(*FF_GRAY)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def feld_zeile(self, felder: list):
        """Mehrere Felder in einer Zeile"""
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*FF_GRAY)
        breite = 190 // len(felder)
        for label, wert in felder:
            self.set_font("Helvetica", "", 8)
            self.cell(breite, 4, label, align="L")
        self.ln(4)
        for label, wert in felder:
            self.set_font("Helvetica", "", 10)
            self.set_draw_color(*FF_GRAY)
            x = self.get_x()
            y = self.get_y()
            self.rect(x, y, breite - 2, 7)
            self.cell(breite - 2, 7, str(wert) if wert else "", align="L")
            self.set_x(x + breite)
        self.ln(10)

    def checkbox_feld(self, label: str, checked: bool):
        x = self.get_x()
        y = self.get_y()
        self.rect(x, y, 4, 4)
        if checked:
            self.set_font("Helvetica", "B", 8)
            self.set_xy(x + 0.5, y - 0.5)
            self.cell(4, 4, "X")
        self.set_xy(x + 6, y)
        self.set_font("Helvetica", "", 9)
        self.cell(30, 4, label)


def generate_personalfragebogen_pdf(pf: Personalfragebogen, output_path: Path) -> Path:
    """Generiert ein PDF-Dokument fuer den Personalfragebogen."""
    pdf = PersonalfragebogenPDF()
    
    # Persoenliche Angaben
    pdf.section("Persoenliche Angaben:")
    pdf.feld_zeile([("Familienname", pf.familienname), ("Vorname", pf.vorname)])
    pdf.feld_zeile([("Strasse und Hausnummer", pf.strasse), ("PLZ, Ort", pf.plz_ort)])
    pdf.feld_zeile([("Geburtsdatum", pf.geburtsdatum), ("Geschlecht", pf.geschlecht)])
    pdf.feld_zeile([("RV-Versicherungsnummer", pf.sozialversicherung.rv_nummer), ("Familienstand", pf.familienstand)])
    pdf.feld_zeile([("Staatsangehoerigkeit", pf.staatsangehoerigkeit), ("Schwerbehindert", "Ja" if pf.schwerbehindert else "Nein")])
    pdf.feld_zeile([("IBAN", pf.bank.iban), ("BIC / Bankbezeichnung", f"{pf.bank.bic} / {pf.bank.bankname}")])
    
    # Beschaeftigung
    pdf.section("Beschaeftigung:")
    pdf.feld_zeile([
        ("Eintrittsdatum", pf.beschaeftigung.eintrittsdatum),
        ("Lohnsteuerklasse", pf.beschaeftigung.steuerklasse),
        ("Kinderfreibetraege", str(pf.beschaeftigung.kinderfreibetraege))
    ])
    pdf.feld_zeile([
        ("Kirchensteuer", "Ja" if pf.beschaeftigung.kirchensteuer else "Nein"),
        ("Ausgeuebte Taetigkeit", pf.beschaeftigung.taetigkeit)
    ])
    pdf.feld_zeile([
        ("Ausbildung", pf.beschaeftigung.ausbildung),
        ("Berufsausbildung", "mit" if pf.beschaeftigung.berufsausbildung else "ohne")
    ])
    pdf.feld_zeile([
        ("Urlaubsanspruch", f"{pf.beschaeftigung.urlaubsanspruch} Tage"),
        ("Woechentliche Arbeitszeit", f"{pf.beschaeftigung.woechentliche_arbeitszeit} Std.")
    ])
    
    # Sozialversicherung
    pdf.section("Sozialversicherung:")
    pdf.feld_zeile([
        ("Krankenkasse (genaue Angabe)", pf.sozialversicherung.krankenkasse),
        ("Kinder", "Ja" if pf.sozialversicherung.kinder else "Nein")
    ])
    
    # Entlohnung
    pdf.section("Entlohnung:")
    pdf.feld_zeile([
        ("Bezeichnung", pf.entlohnung.bezeichnung),
        ("Gueltig ab", pf.entlohnung.gueltig_ab),
        ("Hoehe", f"{pf.entlohnung.betrag:.2f} EUR")
    ])
    pdf.feld_zeile([
        ("Gleitzone", "Ja" if pf.entlohnung.gleitzone else "Nein"),
        ("Steuerliche Identifikationsnummer", pf.entlohnung.steuer_id)
    ])
    
    # Unterschrift
    pdf.ln(15)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*FF_GRAY)
    pdf.multi_cell(0, 4, "Erklaerung des Arbeitnehmers: Ich versichere, dass die vorstehenden Angaben der Wahrheit entsprechen. Ich verpflichte mich, meinem Arbeitgeber alle Aenderungen, insbesondere in Bezug auf weitere Beschaeftigungen (in Bezug auf Art, Dauer und Entgelt) unverzueglich mitzuteilen.")
    
    pdf.ln(15)
    pdf.set_draw_color(*FF_GRAY)
    pdf.line(20, pdf.get_y(), 80, pdf.get_y())
    pdf.line(120, pdf.get_y(), 180, pdf.get_y())
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(90, 5, "Datum", align="C")
    pdf.cell(90, 5, "Unterschrift", align="C")
    
    # Speichern
    pdf.output(str(output_path))
    return output_path


def interactive_personalfragebogen() -> Personalfragebogen:
    """Interaktive Erfassung des Personalfragebogens."""
    print("\n" + "=" * 60)
    print("  FASSADENFIX PERSONALFRAGEBOGEN")
    print("=" * 60)

    pf = Personalfragebogen()

    # Persoenliche Angaben
    print("\n--- PERSOENLICHE ANGABEN ---")
    pf.familienname = input("Familienname: ").strip()
    pf.vorname = input("Vorname: ").strip()
    pf.strasse = input("Strasse und Hausnummer: ").strip()
    pf.plz_ort = input("PLZ, Ort: ").strip()
    pf.geburtsdatum = input("Geburtsdatum (TT.MM.JJJJ): ").strip()
    pf.geschlecht = input("Geschlecht (m/w/d): ").strip()
    pf.staatsangehoerigkeit = input("Staatsangehoerigkeit [deutsch]: ").strip() or "deutsch"
    pf.familienstand = input("Familienstand: ").strip()
    pf.verheiratet = input("Verheiratet? (j/n): ").lower() == "j"
    pf.schwerbehindert = input("Schwerbehindert? (j/n): ").lower() == "j"

    # Bankverbindung
    print("\n--- BANKVERBINDUNG ---")
    pf.bank.iban = input("IBAN: ").strip()
    pf.bank.bic = input("BIC: ").strip()
    pf.bank.bankname = input("Bankname: ").strip()

    # Beschaeftigung
    print("\n--- BESCHAEFTIGUNG ---")
    pf.beschaeftigung.eintrittsdatum = input("Eintrittsdatum (TT.MM.JJJJ): ").strip()
    print("Steuerklassen: I, II, III, IV, V, VI")
    pf.beschaeftigung.steuerklasse = input("Steuerklasse [I]: ").strip() or "I"
    pf.beschaeftigung.kinderfreibetraege = int(input("Kinderfreibetraege [0]: ").strip() or "0")
    pf.beschaeftigung.kirchensteuer = input("Kirchensteuer? (j/n): ").lower() == "j"
    pf.beschaeftigung.taetigkeit = input("Ausgeuebte Taetigkeit: ").strip()
    
    print("Ausbildung:")
    for i, opt in enumerate(AUSBILDUNG_OPTIONEN, 1):
        print(f"  {i}) {opt}")
    ausb_wahl = input("Auswahl (1-4): ").strip()
    try:
        pf.beschaeftigung.ausbildung = AUSBILDUNG_OPTIONEN[int(ausb_wahl) - 1]
    except (ValueError, IndexError):
        pf.beschaeftigung.ausbildung = AUSBILDUNG_OPTIONEN[0]
    
    pf.beschaeftigung.berufsausbildung = input("Mit Berufsausbildung? (j/n): ").lower() == "j"
    pf.beschaeftigung.urlaubsanspruch = int(input("Urlaubsanspruch (Tage) [30]: ").strip() or "30")
    pf.beschaeftigung.woechentliche_arbeitszeit = float(input("Woechentliche Arbeitszeit (Std.) [40]: ").strip() or "40")

    # Sozialversicherung
    print("\n--- SOZIALVERSICHERUNG ---")
    pf.sozialversicherung.krankenkasse = input("Krankenkasse: ").strip()
    pf.sozialversicherung.rv_nummer = input("RV-Versicherungsnummer: ").strip()
    pf.sozialversicherung.kinder = input("Kinder? (j/n): ").lower() == "j"

    # Entlohnung
    print("\n--- ENTLOHNUNG ---")
    pf.entlohnung.bezeichnung = input("Bezeichnung (z.B. Stundenlohn): ").strip()
    pf.entlohnung.gueltig_ab = input("Gueltig ab (TT.MM.JJJJ): ").strip()
    pf.entlohnung.betrag = float(input("Betrag (EUR): ").strip() or "0")
    pf.entlohnung.gleitzone = input("Gleitzone? (j/n): ").lower() == "j"
    pf.entlohnung.steuer_id = input("Steuerliche Identifikationsnummer: ").strip()

    return pf


def main():
    """Hauptfunktion fuer den interaktiven Personalfragebogen."""
    pf = interactive_personalfragebogen()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{pf.familienname}_{pf.vorname}".replace(" ", "_")[:30]

    # JSON speichern
    json_path = Path(f"personalfragebogen_{safe_name}_{timestamp}.json")
    pf.to_json(json_path)
    print(f"\nJSON gespeichert: {json_path}")

    # PDF generieren
    pdf_path = Path(f"personalfragebogen_{safe_name}_{timestamp}.pdf")
    generate_personalfragebogen_pdf(pf, pdf_path)
    print(f"PDF generiert: {pdf_path}")

    # Validierung
    print("\n--- VALIDIERUNG ---")
    if pf.validate_iban():
        print("IBAN: OK")
    else:
        print("IBAN: WARNUNG - Format pruefen")
    
    if pf.validate_steuer_id():
        print("Steuer-ID: OK")
    else:
        print("Steuer-ID: WARNUNG - 11 Ziffern erforderlich")

    print("\n" + "=" * 60)
    print("  PERSONALFRAGEBOGEN ERSTELLT")
    print("=" * 60)


if __name__ == "__main__":
    main()
