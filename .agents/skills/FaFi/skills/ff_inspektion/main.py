#!/usr/bin/env python3
"""
FassadenFix Jährliche Inspektion - Digitaler Workflow
Führt den Prüfer durch den Inspektionsprozess und generiert ein PDF-Protokoll.
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

# Bewertungsskala Farben (0=grün bis 4=rot)
BEWERTUNG_FARBEN = [
    (119, 188, 31),   # 0 - Grün (neuwertig)
    (180, 210, 50),   # 1 - Hellgrün
    (255, 220, 0),    # 2 - Gelb
    (255, 140, 0),    # 3 - Orange (Nachbesserung nötig)
    (220, 50, 50),    # 4 - Rot (starker Neubefall)
]

# Vordefinierte Optionen
SCHAEDEN_ARTEN = ["Keine", "Löcher", "Risse", "Graffiti", "Abplatzungen", "Sonstige Schäden"]
GEFAHREN_ARTEN = [
    "Keine",
    "Vogelnester",
    "Wachstum von Bäumen, Hecken und Rankpflanzen",
    "Veränderungen im Bereich der StVO",
    "Sonstige Gründe"
]
NACHARBEITEN_BEREICHE = ["Keine", "Eingangsseite", "Rückseite", "Giebel links", "Giebel rechts"]


@dataclass
class Projektdaten:
    """Ursprüngliche Projektdaten"""
    projektnummer: str = ""
    auftraggeber: str = ""
    anschrift: str = ""
    umsetzungsdatum: str = ""


@dataclass
class Inspektionsergebnis:
    """Ergebnis der Inspektion"""
    datum: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    zustand_fassade: int = 0  # 0-4 Skala
    nacharbeiten_notwendig: bool = False
    nacharbeiten_bereiche: List[str] = field(default_factory=list)


@dataclass
class Schaeden:
    """Dokumentierte Schäden"""
    vorhanden: bool = False
    arten: List[str] = field(default_factory=list)
    beschreibung: str = ""


@dataclass
class Gefahren:
    """Weitere zu prüfende Gefahren"""
    vorhanden: bool = False
    arten: List[str] = field(default_factory=list)
    beschreibung: str = ""


@dataclass
class Unterschrift:
    """Digitale Unterschrift"""
    name: str = ""
    funktion: str = ""
    signatur: str = ""  # Base64 oder Pfad


@dataclass
class Inspektionsdaten:
    """Vollständige Inspektionsdaten"""
    projekt: Projektdaten = field(default_factory=Projektdaten)
    inspektion: Inspektionsergebnis = field(default_factory=Inspektionsergebnis)
    schaeden: Schaeden = field(default_factory=Schaeden)
    gefahren: Gefahren = field(default_factory=Gefahren)
    empfehlungen: str = ""
    garantie_erteilt_bis: str = ""
    naechster_inspektionstermin: str = ""
    unterschrift_empfaenger: Unterschrift = field(default_factory=Unterschrift)
    unterschrift_pruefer: Unterschrift = field(default_factory=Unterschrift)
    fotos: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, path: Optional[Path] = None) -> str:
        data = self.to_dict()
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        if path:
            path.write_text(json_str, encoding="utf-8")
        return json_str


class InspektionsPDF(FPDF):
    """PDF-Generator für Inspektionsprotokoll im FassadenFix Design"""

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
        self.cell(0, 8, "JÄHRLICHE INSPEKTION", align="L")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 8, 'Zur Kontrolle der Garantie "5 Jahre algenfrei"', align="R")
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

    def bewertungsskala(self, wert: int):
        """Zeichnet die visuelle Bewertungsskala"""
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*FF_GRAY)
        self.cell(60, 8, "Zustand der Fassade:", align="L")
        
        # Skala zeichnen
        x_start = self.get_x()
        y = self.get_y()
        box_width = 20
        box_height = 8
        
        for i in range(5):
            # Hintergrundfarbe
            self.set_fill_color(*BEWERTUNG_FARBEN[i])
            self.set_draw_color(*FF_GRAY)
            
            # Box zeichnen
            self.rect(x_start + i * box_width, y, box_width, box_height, "FD" if i == wert else "D")
            
            # Zahl
            self.set_xy(x_start + i * box_width, y)
            self.set_text_color(*FF_WHITE if i == wert else FF_GRAY)
            self.set_font("Helvetica", "B" if i == wert else "", 10)
            self.cell(box_width, box_height, str(i), align="C")
        
        self.ln(12)
        
        # Legende
        self.set_text_color(*FF_GRAY)
        self.set_font("Helvetica", "I", 8)
        self.cell(60, 6, "", align="L")
        self.cell(0, 6, "Ab Stufe 3 muss nachgebessert werden!", align="L")
        self.ln(8)

    def checkbox_group(self, label: str, options: List[str], selected: List[str]):
        """Zeichnet eine Gruppe von Checkboxen"""
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 8, f"{label}:", ln=True)
        
        self.set_font("Helvetica", "", 10)
        for option in options:
            marker = "[X]" if option in selected else "[ ]"
            self.cell(0, 6, f"    {marker} {option}", ln=True)
        self.ln(3)

    def multiline_field(self, label: str, value: str):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 8, f"{label}:", ln=True)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, str(value) if value else "-")
        self.ln(3)

    def unterschrift_block(self, label: str, name: str, funktion: str):
        """Zeichnet einen Unterschriftenblock"""
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 8, f"{label}:", ln=True)
        
        self.set_font("Helvetica", "", 10)
        self.cell(30, 6, "Name:", align="L")
        self.cell(60, 6, name, ln=True)
        self.cell(30, 6, "Funktion:", align="L")
        self.cell(60, 6, funktion, ln=True)
        
        # Unterschriftslinie
        self.ln(10)
        self.set_draw_color(*FF_GRAY)
        x = self.get_x()
        y = self.get_y()
        self.line(x, y, x + 80, y)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*FF_GREEN)
        self.cell(80, 5, label, align="C")
        self.ln(10)


def generate_pdf(daten: Inspektionsdaten, output_path: Path) -> Path:
    """Generiert ein PDF-Dokument aus den Inspektionsdaten."""
    pdf = InspektionsPDF()

    # Datum
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*FF_GRAY)
    pdf.cell(0, 8, f"Datum der Inspektion: {daten.inspektion.datum}", align="R", ln=True)
    pdf.ln(5)

    # Projektdaten
    pdf.section_title("Projektdaten")
    pdf.field("Projektnummer", daten.projekt.projektnummer)
    pdf.field("Auftraggeber", daten.projekt.auftraggeber)
    pdf.field("Anschrift", daten.projekt.anschrift)
    pdf.field("Umsetzungsdatum", daten.projekt.umsetzungsdatum)
    pdf.ln(5)

    # Inspektionspunkte
    pdf.section_title("Inspektionspunkte")
    pdf.bewertungsskala(daten.inspektion.zustand_fassade)
    
    # Nacharbeiten
    nacharbeiten_text = "Keine" if not daten.inspektion.nacharbeiten_notwendig else ", ".join(daten.inspektion.nacharbeiten_bereiche)
    pdf.checkbox_group("Nacharbeiten (kostenfrei)", NACHARBEITEN_BEREICHE, 
                       daten.inspektion.nacharbeiten_bereiche if daten.inspektion.nacharbeiten_notwendig else ["Keine"])
    pdf.ln(3)

    # Schäden
    pdf.checkbox_group("Schäden", SCHAEDEN_ARTEN, 
                       daten.schaeden.arten if daten.schaeden.vorhanden else ["Keine"])
    if daten.schaeden.beschreibung:
        pdf.multiline_field("Beschreibung", daten.schaeden.beschreibung)

    # Gefahren
    pdf.checkbox_group("Weitere zu prüfende Gefahren", GEFAHREN_ARTEN,
                       daten.gefahren.arten if daten.gefahren.vorhanden else ["Keine"])
    if daten.gefahren.beschreibung:
        pdf.multiline_field("Beschreibung", daten.gefahren.beschreibung)

    # Empfehlungen
    pdf.section_title("Empfehlungen")
    pdf.multiline_field("Empfohlene Maßnahmen", daten.empfehlungen)
    pdf.ln(3)

    # Termine
    pdf.field("Garantie erteilt bis", daten.garantie_erteilt_bis)
    pdf.field("Nächster Inspektionstermin", daten.naechster_inspektionstermin)
    pdf.ln(5)

    # Unterschriften
    pdf.section_title("Unterschriften")
    
    # Zwei Spalten für Unterschriften
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*FF_GRAY)
    
    col_width = 90
    x_start = pdf.get_x()
    y_start = pdf.get_y()
    
    # Empfänger
    pdf.unterschrift_block("Unterschrift Empfänger", 
                           daten.unterschrift_empfaenger.name,
                           daten.unterschrift_empfaenger.funktion)
    
    # Prüfer (rechte Spalte)
    pdf.set_xy(x_start + col_width, y_start)
    pdf.unterschrift_block("Unterschrift Prüfer",
                           daten.unterschrift_pruefer.name,
                           daten.unterschrift_pruefer.funktion)

    # Speichern
    pdf.output(str(output_path))
    return output_path


def interactive_inspektion() -> Inspektionsdaten:
    """Interaktive Erfassung der Inspektionsdaten über die Kommandozeile."""
    print("\n" + "=" * 60)
    print("  FASSADENFIX JÄHRLICHE INSPEKTION")
    print("=" * 60)

    daten = Inspektionsdaten()

    # Projektdaten
    print("\n--- PROJEKTDATEN ---")
    daten.projekt.projektnummer = input("Projektnummer: ").strip()
    daten.projekt.auftraggeber = input("Auftraggeber: ").strip()
    daten.projekt.anschrift = input("Anschrift: ").strip()
    daten.projekt.umsetzungsdatum = input("Umsetzungsdatum (YYYY-MM-DD): ").strip()

    # Inspektion
    print("\n--- INSPEKTIONSERGEBNIS ---")
    print("Zustand der Fassade (0=neuwertig, 4=starker Neubefall):")
    try:
        daten.inspektion.zustand_fassade = int(input("Bewertung (0-4): ") or 0)
        daten.inspektion.zustand_fassade = max(0, min(4, daten.inspektion.zustand_fassade))
    except ValueError:
        daten.inspektion.zustand_fassade = 0

    if daten.inspektion.zustand_fassade >= 3:
        print("\n⚠️  Nacharbeiten erforderlich!")
        daten.inspektion.nacharbeiten_notwendig = True
        print("Bereiche für Nacharbeiten (Komma-getrennt):")
        print(f"  Optionen: {', '.join(NACHARBEITEN_BEREICHE[1:])}")
        bereiche_input = input("Bereiche: ").strip()
        daten.inspektion.nacharbeiten_bereiche = [b.strip() for b in bereiche_input.split(",") if b.strip()]

    # Schäden
    print("\n--- SCHÄDEN ---")
    print(f"Schadensarten: {', '.join(SCHAEDEN_ARTEN)}")
    schaeden_input = input("Vorhandene Schäden (Komma-getrennt, oder Enter für keine): ").strip()
    if schaeden_input and schaeden_input.lower() != "keine":
        daten.schaeden.vorhanden = True
        daten.schaeden.arten = [s.strip() for s in schaeden_input.split(",") if s.strip()]
        daten.schaeden.beschreibung = input("Beschreibung der Schäden: ").strip()

    # Gefahren
    print("\n--- WEITERE GEFAHREN ---")
    print(f"Gefahrenarten: {', '.join(GEFAHREN_ARTEN)}")
    gefahren_input = input("Vorhandene Gefahren (Komma-getrennt, oder Enter für keine): ").strip()
    if gefahren_input and gefahren_input.lower() != "keine":
        daten.gefahren.vorhanden = True
        daten.gefahren.arten = [g.strip() for g in gefahren_input.split(",") if g.strip()]
        daten.gefahren.beschreibung = input("Beschreibung der Gefahren: ").strip()

    # Empfehlungen
    print("\n--- EMPFEHLUNGEN ---")
    daten.empfehlungen = input("Empfohlene Maßnahmen: ").strip()

    # Termine
    print("\n--- TERMINE ---")
    daten.garantie_erteilt_bis = input("Garantie erteilt bis (YYYY-MM-DD): ").strip()
    daten.naechster_inspektionstermin = input("Nächster Inspektionstermin (YYYY-MM-DD): ").strip()

    # Unterschriften
    print("\n--- UNTERSCHRIFTEN ---")
    print("Empfänger:")
    daten.unterschrift_empfaenger.name = input("  Name: ").strip()
    daten.unterschrift_empfaenger.funktion = input("  Funktion: ").strip()
    
    print("Prüfer:")
    daten.unterschrift_pruefer.name = input("  Name: ").strip()
    daten.unterschrift_pruefer.funktion = input("  Funktion: ").strip()

    return daten


def main():
    """Hauptfunktion für die interaktive Inspektion."""
    daten = interactive_inspektion()

    # JSON speichern
    json_path = Path(f"inspektion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    daten.to_json(json_path)
    print(f"\n✓ JSON gespeichert: {json_path}")

    # PDF generieren
    pdf_path = Path(f"inspektion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    generate_pdf(daten, pdf_path)
    print(f"✓ PDF generiert: {pdf_path}")

    print("\n" + "=" * 60)
    print("  INSPEKTION ABGESCHLOSSEN")
    print("=" * 60)


if __name__ == "__main__":
    main()
