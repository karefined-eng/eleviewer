#!/usr/bin/env python3
"""
FassadenFix Objektdokumentation
Erstellt Vorher-Nachher-Dokumentationen und Abnahmeprotokolle.
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


@dataclass
class Wasseruhr:
    """Wasseruhr-Zaehlerstand"""
    bezeichnung: str = ""
    zaehlerstand: str = ""


@dataclass
class Checkliste:
    """Checkliste fuer Dokumentation"""
    fotodokumentation: bool = False
    vorhandene_schaeden: bool = False
    schaeden_beschreibung: str = ""
    laeufer_abfaerbungen: bool = False
    laeufer_beschreibung: str = ""
    gefahrenhinweis_bestaetigt: bool = False
    wasseruhren: List[Wasseruhr] = field(default_factory=list)


@dataclass
class Unterschrift:
    """Digitale Unterschrift"""
    name: str = ""
    datum: str = ""
    signatur: str = ""  # Base64 oder Pfad


@dataclass
class Dokumentation:
    """Vollstaendige Dokumentation"""
    typ: str = "vorher"  # "vorher" oder "nachher"
    projektnummer: str = ""
    anschrift: str = ""
    datum: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    checkliste: Checkliste = field(default_factory=Checkliste)
    fotos: List[str] = field(default_factory=list)
    unterschrift_kunde: Unterschrift = field(default_factory=Unterschrift)
    unterschrift_mitarbeiter: Unterschrift = field(default_factory=Unterschrift)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, path: Optional[Path] = None) -> str:
        data = self.to_dict()
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        if path:
            path.write_text(json_str, encoding="utf-8")
        return json_str


class DokumentationsPDF(FPDF):
    """PDF-Generator fuer Objektdokumentation im FassadenFix Design"""

    def __init__(self, typ: str = "vorher"):
        super().__init__()
        self.typ = typ
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # Logo-Bereich
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(*FF_GREEN)
        self.cell(0, 10, "FASSADENFIX", align="L")
        self.ln(12)
        
        # Titel
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*FF_GRAY)
        titel_suffix = "(vor der Reinigung)" if self.typ == "vorher" else "(nach der Reinigung)"
        self.cell(100, 8, "", align="L")
        self.set_text_color(*FF_GREEN)
        self.cell(45, 8, "OBJEKT", align="R")
        self.set_text_color(*FF_GRAY)
        self.cell(45, 8, "DOKUMENTATION", align="L")
        self.ln(6)
        self.set_font("Helvetica", "", 11)
        self.cell(0, 6, titel_suffix, align="R")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 10, "FassadenFix | Professionelle Fassadenreinigung", align="C")

    def projektdaten(self, anschrift: str, datum: str):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 6, f"FassadenFix | {anschrift}", ln=True)
        self.ln(15)
        
        # Datum rechts
        self.set_font("Helvetica", "B", 10)
        self.cell(150, 6, "", align="L")
        self.cell(40, 6, "DATUM", align="L")
        self.ln(5)
        self.cell(150, 6, "", align="L")
        self.set_font("Helvetica", "", 10)
        self.cell(40, 6, datum, align="L")
        self.ln(10)

    def checkbox_item(self, label: str, beschreibung: str, checked: bool, zusatz: str = ""):
        # Checkbox
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*FF_GRAY)
        
        # Checkbox zeichnen
        x = self.get_x()
        y = self.get_y()
        self.rect(x, y, 5, 5)
        if checked:
            self.set_font("Helvetica", "B", 8)
            self.set_xy(x + 1, y)
            self.cell(5, 5, "X", align="L")
        
        # Label
        self.set_xy(x + 8, y)
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 5, label, ln=True)
        
        # Beschreibung
        self.set_x(x + 8)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, beschreibung, ln=True)
        
        # Zusatzfeld
        if zusatz:
            self.set_x(x + 8)
            self.set_draw_color(*FF_GRAY)
            self.rect(self.get_x(), self.get_y() + 2, 180, 15)
            self.set_xy(x + 10, self.get_y() + 4)
            self.set_font("Helvetica", "", 9)
            self.set_text_color(*FF_GRAY)
            self.multi_cell(175, 5, zusatz)
            self.ln(5)
        
        self.ln(8)

    def wasseruhren_tabelle(self, wasseruhren: List[Wasseruhr]):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*FF_GRAY)
        
        # Checkbox
        x = self.get_x()
        y = self.get_y()
        self.rect(x, y, 5, 5)
        
        self.set_xy(x + 8, y)
        self.cell(60, 5, "Wasseruhren", ln=False)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 100, 100)
        self.ln(5)
        self.set_x(x + 8)
        self.cell(0, 5, "Wurden vor Beginn eines Auftrages die Zaehlerstaende gemessen?", ln=True)
        self.ln(5)
        
        # Tabelle
        self.set_x(x + 8)
        col_width = 45
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*FF_GRAY)
        
        for i in range(4):
            self.cell(col_width, 6, "Wasseruhr", border=0)
            self.cell(col_width, 6, "Zaehlerstand", border=0)
        self.ln(6)
        
        self.set_font("Helvetica", "", 9)
        for i in range(4):
            if i < len(wasseruhren):
                self.set_x(x + 8 + i * col_width * 2)
                self.cell(col_width, 6, wasseruhren[i].bezeichnung, border=1)
                self.cell(col_width, 6, wasseruhren[i].zaehlerstand, border=1)
            else:
                self.set_x(x + 8 + i * col_width * 2)
                self.cell(col_width, 6, "", border=1)
                self.cell(col_width, 6, "", border=1)
            if i < 3:
                self.ln(6)
        self.ln(15)

    def unterschriften_block(self, kunde: Unterschrift, mitarbeiter: Unterschrift):
        self.ln(10)
        
        # Hinweistext
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 5, "Ich bestaetige die Richtigkeit der oben gemachten Angaben und habe die Hinweise zur Kenntnis genommen.", ln=True)
        self.ln(10)
        
        # Unterschriftslinien
        self.set_draw_color(*FF_GREEN)
        self.set_line_width(0.5)
        
        x = self.get_x()
        y = self.get_y()
        
        # Kunde
        self.line(x, y + 15, x + 80, y + 15)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*FF_GREEN)
        self.set_xy(x, y + 17)
        self.cell(80, 5, "Unterschrift Kunde", align="C")
        if kunde.name:
            self.set_xy(x, y + 5)
            self.set_text_color(*FF_GRAY)
            self.cell(80, 5, kunde.name, align="C")
        
        # Mitarbeiter
        self.line(x + 100, y + 15, x + 180, y + 15)
        self.set_text_color(*FF_GREEN)
        self.set_xy(x + 100, y + 17)
        self.cell(80, 5, "Unterschrift Mitarbeiter", align="C")
        if mitarbeiter.name:
            self.set_xy(x + 100, y + 5)
            self.set_text_color(*FF_GRAY)
            self.cell(80, 5, mitarbeiter.name, align="C")


def generate_dokumentation_pdf(dok: Dokumentation, output_path: Path) -> Path:
    """Generiert ein PDF-Dokument fuer die Objektdokumentation."""
    pdf = DokumentationsPDF(typ=dok.typ)
    
    # Projektdaten
    pdf.projektdaten(dok.anschrift, dok.datum)
    
    # Checkliste
    pdf.checkbox_item(
        "Fotodokumentation",
        "Wurden vor Beginn eines Auftrages Bilder gemacht?",
        dok.checkliste.fotodokumentation
    )
    
    pdf.checkbox_item(
        "Vorhandene Schaeden",
        "Putzschaeden / Farbschaeden / sonstige Schaeden",
        dok.checkliste.vorhandene_schaeden,
        dok.checkliste.schaeden_beschreibung
    )
    
    pdf.checkbox_item(
        "Laeufer, Abfaerbungen, Schattierungen?",
        "an/unter/von Fensterbanken, Dachsparren, Dachrinnen, Anbauteilen (Lampen, Gelaender etc.)",
        dok.checkliste.laeufer_abfaerbungen,
        dok.checkliste.laeufer_beschreibung
    )
    
    pdf.checkbox_item(
        "Gefahrenhinweis",
        "Reinigungsloesungen koennen im Allgemeinen aetzend sein und somit Haut- & Atemwegsreizungen verursachen bzw. Kleidung beschaedigen. Der Kunde sollte sich daher waehrend der Reinigung nicht ungeschuetzt in unmittelbarer Naehe aufhalten.",
        dok.checkliste.gefahrenhinweis_bestaetigt
    )
    
    # Wasseruhren
    pdf.wasseruhren_tabelle(dok.checkliste.wasseruhren)
    
    # Unterschriften
    pdf.unterschriften_block(dok.unterschrift_kunde, dok.unterschrift_mitarbeiter)
    
    # Speichern
    pdf.output(str(output_path))
    return output_path


def interactive_dokumentation() -> Dokumentation:
    """Interaktive Erfassung der Dokumentationsdaten."""
    print("\n" + "=" * 60)
    print("  FASSADENFIX OBJEKTDOKUMENTATION")
    print("=" * 60)

    dok = Dokumentation()

    # Typ
    print("\nDokumentationstyp:")
    print("  1) Vorher (vor der Reinigung)")
    print("  2) Nachher (nach der Reinigung)")
    typ_wahl = input("Auswahl (1/2): ").strip()
    dok.typ = "nachher" if typ_wahl == "2" else "vorher"

    # Projektdaten
    print("\n--- PROJEKTDATEN ---")
    dok.projektnummer = input("Projektnummer: ").strip()
    dok.anschrift = input("Anschrift: ").strip()

    # Checkliste
    print("\n--- CHECKLISTE ---")
    dok.checkliste.fotodokumentation = input("Fotodokumentation erstellt? (j/n): ").lower() == "j"
    dok.checkliste.vorhandene_schaeden = input("Vorhandene Schaeden? (j/n): ").lower() == "j"
    if dok.checkliste.vorhandene_schaeden:
        dok.checkliste.schaeden_beschreibung = input("  Beschreibung: ").strip()
    
    dok.checkliste.laeufer_abfaerbungen = input("Laeufer/Abfaerbungen? (j/n): ").lower() == "j"
    if dok.checkliste.laeufer_abfaerbungen:
        dok.checkliste.laeufer_beschreibung = input("  Beschreibung: ").strip()
    
    dok.checkliste.gefahrenhinweis_bestaetigt = input("Gefahrenhinweis bestaetigt? (j/n): ").lower() == "j"

    # Wasseruhren
    print("\n--- WASSERUHREN ---")
    anzahl = input("Anzahl Wasseruhren (0-4): ").strip()
    try:
        anzahl = int(anzahl)
    except ValueError:
        anzahl = 0
    
    for i in range(min(anzahl, 4)):
        print(f"  Wasseruhr {i+1}:")
        bez = input("    Bezeichnung: ").strip()
        stand = input("    Zaehlerstand: ").strip()
        dok.checkliste.wasseruhren.append(Wasseruhr(bezeichnung=bez, zaehlerstand=stand))

    # Unterschriften
    print("\n--- UNTERSCHRIFTEN ---")
    dok.unterschrift_kunde.name = input("Name Kunde: ").strip()
    dok.unterschrift_mitarbeiter.name = input("Name Mitarbeiter: ").strip()

    return dok


def main():
    """Hauptfunktion fuer die interaktive Dokumentation."""
    dok = interactive_dokumentation()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # JSON speichern
    json_path = Path(f"dokumentation_{dok.typ}_{timestamp}.json")
    dok.to_json(json_path)
    print(f"\nJSON gespeichert: {json_path}")

    # PDF generieren
    pdf_path = Path(f"dokumentation_{dok.typ}_{timestamp}.pdf")
    generate_dokumentation_pdf(dok, pdf_path)
    print(f"PDF generiert: {pdf_path}")

    print("\n" + "=" * 60)
    print("  DOKUMENTATION ABGESCHLOSSEN")
    print("=" * 60)


if __name__ == "__main__":
    main()
