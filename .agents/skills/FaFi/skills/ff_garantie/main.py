#!/usr/bin/env python3
"""
FassadenFix Garantieurkunde
Erstellt professionelle Garantieurkunden nach Projektabnahme.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict, field
from fpdf import FPDF

# FassadenFix Branding Farben
FF_GREEN = (119, 188, 31)  # #77bc1f
FF_GRAY = (78, 87, 88)     # #4e5758
FF_WHITE = (255, 255, 255)

# Garantietexte
PAUSCHALFESTPREIS_TEXT = """Unsere Preise sind individuell und serioes als Pauschalfestpreise kalkuliert. Das heisst, Sie erhalten stets eine Rechnung in maximaler Hoehe Ihres Angebots. Sollten wir aufgrund zuegiger Arbeiten weniger Zeit benoetigen als veranschlagt, werden wir Minderkosten* zu Ihrem Vorteil abziehen."""

ALGENFREIHEIT_TEXT = """Wir versprechen nicht nur die standardmaessige 5-Jahresgarantie fuer die korrekte handwerkliche Ausfuehrung nach VOB. Wir garantieren sogar die Langlebigkeit unserer Ergebnisse. Unsere Leistung hat Bestand. Das garantieren wir fuer mindestens 5 Jahre.**"""

FUSSNOTE_1 = "* z.B. Buehnentechnik oder Uebernachtungen"
FUSSNOTE_2 = "** gemaess AGB / Angebot"


@dataclass
class Garantie:
    """Garantieurkunde Daten"""
    kundenname: str = ""
    kundenadresse: str = ""
    projektnummer: str = ""
    abnahmedatum: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    garantie_bis: str = ""
    geschaeftsfuehrer: str = "Alexander Retzlaff"

    def __post_init__(self):
        if not self.garantie_bis and self.abnahmedatum:
            try:
                abnahme = datetime.strptime(self.abnahmedatum, "%Y-%m-%d")
                garantie_ende = abnahme + timedelta(days=5*365)
                self.garantie_bis = garantie_ende.strftime("%Y-%m-%d")
            except ValueError:
                pass

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, path: Optional[Path] = None) -> str:
        data = self.to_dict()
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        if path:
            path.write_text(json_str, encoding="utf-8")
        return json_str


class GarantiePDF(FPDF):
    """PDF-Generator fuer Garantieurkunde im FassadenFix Design"""

    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # Logo-Bereich
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(*FF_GREEN)
        self.cell(15, 12, "", align="L")  # Icon-Platzhalter
        self.set_text_color(*FF_GRAY)
        self.cell(70, 12, "FASSADEN", align="L")
        self.set_text_color(*FF_GREEN)
        self.cell(0, 12, "FIX", align="L")
        self.ln(20)

    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*FF_GREEN)
        self.cell(0, 4, FUSSNOTE_1, align="R")
        self.ln(4)
        self.cell(0, 4, FUSSNOTE_2, align="R")

    def titel(self):
        self.set_font("Helvetica", "B", 36)
        self.set_text_color(*FF_GREEN)
        self.cell(0, 20, "GARANTIEURKUNDE", align="C", ln=True)
        self.ln(10)

    def kundenname(self, name: str):
        self.set_font("Helvetica", "", 14)
        self.set_text_color(*FF_GRAY)
        
        # Unterstrichen
        self.set_draw_color(*FF_GRAY)
        x = 30
        self.set_x(x)
        self.cell(150, 10, name, align="C", ln=True)
        self.line(x, self.get_y(), x + 150, self.get_y())
        self.ln(15)

    def garantie_abschnitt(self, titel: str, text: str):
        # Titel in Gruen
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*FF_GREEN)
        self.cell(0, 8, titel, ln=True)
        self.ln(3)
        
        # Text in Grau
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*FF_GRAY)
        self.multi_cell(0, 6, text)
        self.ln(10)

    def unterschriften_bereich(self, datum: str, geschaeftsfuehrer: str):
        self.ln(20)
        
        # Dekorative Welle (vereinfacht als Linie)
        self.set_draw_color(*FF_GREEN)
        self.set_line_width(2)
        y = self.get_y()
        
        # Geschwungene Linie simulieren
        for i in range(20):
            x = 10 + i * 9
            offset = 3 if i % 2 == 0 else -3
            self.line(x, y + offset, x + 9, y - offset if i % 2 == 0 else y + offset)
        
        self.ln(15)
        
        # Unterschriftsbereich
        self.set_line_width(0.5)
        x = self.get_x()
        y = self.get_y()
        
        # Datum links
        self.line(x + 20, y + 10, x + 70, y + 10)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*FF_GRAY)
        self.set_xy(x + 20, y + 12)
        self.cell(50, 5, "Datum", align="C")
        self.set_xy(x + 20, y + 2)
        self.cell(50, 5, datum, align="C")
        
        # Geschaeftsfuehrer rechts
        self.line(x + 100, y + 10, x + 180, y + 10)
        self.set_xy(x + 100, y + 12)
        self.cell(80, 5, geschaeftsfuehrer, align="C")
        self.ln(5)
        self.set_xy(x + 100, y + 17)
        self.set_font("Helvetica", "I", 9)
        self.cell(80, 5, "Geschaeftsfuehrer", align="C")
        self.ln(3)
        self.set_xy(x + 100, y + 22)
        self.cell(80, 5, "FassadenFix", align="C")


def generate_garantie_pdf(garantie: Garantie, output_path: Path) -> Path:
    """Generiert ein PDF-Dokument fuer die Garantieurkunde."""
    pdf = GarantiePDF()
    
    # Titel
    pdf.titel()
    
    # Kundenname
    pdf.kundenname(garantie.kundenname)
    
    # Garantie-Abschnitte
    pdf.garantie_abschnitt("Garantierter Pauschalfestpreis", PAUSCHALFESTPREIS_TEXT)
    pdf.garantie_abschnitt("Ergebnisgarantie - 5 Jahre Algenfreiheit", ALGENFREIHEIT_TEXT)
    
    # Unterschriften
    datum_formatiert = garantie.abnahmedatum
    try:
        d = datetime.strptime(garantie.abnahmedatum, "%Y-%m-%d")
        datum_formatiert = d.strftime("%d.%m.%Y")
    except ValueError:
        pass
    
    pdf.unterschriften_bereich(datum_formatiert, garantie.geschaeftsfuehrer)
    
    # Speichern
    pdf.output(str(output_path))
    return output_path


def interactive_garantie() -> Garantie:
    """Interaktive Erfassung der Garantiedaten."""
    print("\n" + "=" * 60)
    print("  FASSADENFIX GARANTIEURKUNDE")
    print("=" * 60)

    garantie = Garantie()

    # Kundendaten
    print("\n--- KUNDENDATEN ---")
    garantie.kundenname = input("Kundenname/Firma: ").strip()
    garantie.kundenadresse = input("Kundenadresse: ").strip()

    # Projektdaten
    print("\n--- PROJEKTDATEN ---")
    garantie.projektnummer = input("Projektnummer: ").strip()
    abnahme = input("Abnahmedatum (YYYY-MM-DD, Enter fuer heute): ").strip()
    if abnahme:
        garantie.abnahmedatum = abnahme
    
    # Garantie-Ende berechnen
    garantie.__post_init__()
    print(f"\nGarantie gueltig bis: {garantie.garantie_bis}")

    return garantie


def main():
    """Hauptfunktion fuer die interaktive Garantieerstellung."""
    garantie = interactive_garantie()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = garantie.kundenname.replace(" ", "_").replace(",", "")[:20]

    # JSON speichern
    json_path = Path(f"garantie_{safe_name}_{timestamp}.json")
    garantie.to_json(json_path)
    print(f"\nJSON gespeichert: {json_path}")

    # PDF generieren
    pdf_path = Path(f"garantie_{safe_name}_{timestamp}.pdf")
    generate_garantie_pdf(garantie, pdf_path)
    print(f"PDF generiert: {pdf_path}")

    print("\n" + "=" * 60)
    print("  GARANTIEURKUNDE ERSTELLT")
    print("=" * 60)


if __name__ == "__main__":
    main()
