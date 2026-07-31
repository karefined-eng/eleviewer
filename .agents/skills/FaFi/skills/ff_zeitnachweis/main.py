#!/usr/bin/env python3
"""
FassadenFix Zeitnachweis
Digitaler Stundenzettel fuer Mitarbeiter.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, asdict, field
from fpdf import FPDF

# FassadenFix Branding Farben
FF_GREEN = (119, 188, 31)
FF_GRAY = (78, 87, 88)
FF_WHITE = (255, 255, 255)

# Arbeitszeitregelungen
STANDARD_ARBEITSZEIT = 8.0  # Stunden
MAX_ARBEITSZEIT = 10.0  # Stunden
PAUSE_AB_6H = 0.5  # 30 Minuten
PAUSE_AB_9H = 0.75  # 45 Minuten


@dataclass
class Tageseintrag:
    """Ein Tageseintrag im Stundenzettel"""
    datum: str
    wochentag: str = ""
    arbeitsbeginn: str = ""
    arbeitsende: str = ""
    pause_minuten: int = 30
    projekt: str = ""
    taetigkeit: str = ""
    arbeitszeit_stunden: float = 0.0
    ueberstunden: float = 0.0
    notizen: str = ""

    def __post_init__(self):
        if self.datum and not self.wochentag:
            try:
                d = datetime.strptime(self.datum, "%Y-%m-%d")
                wochentage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
                self.wochentag = wochentage[d.weekday()]
            except ValueError:
                pass

    def berechne_arbeitszeit(self):
        """Berechnet die Arbeitszeit aus Beginn, Ende und Pause"""
        if not self.arbeitsbeginn or not self.arbeitsende:
            return
        
        try:
            beginn = datetime.strptime(self.arbeitsbeginn, "%H:%M")
            ende = datetime.strptime(self.arbeitsende, "%H:%M")
            diff = ende - beginn
            brutto_stunden = diff.total_seconds() / 3600
            self.arbeitszeit_stunden = brutto_stunden - (self.pause_minuten / 60)
            self.ueberstunden = self.arbeitszeit_stunden - STANDARD_ARBEITSZEIT
        except ValueError:
            pass

    def pruefe_pausenregelung(self) -> str:
        """Prueft ob die Pausenregelung eingehalten wird"""
        if self.arbeitszeit_stunden > 9 and self.pause_minuten < 45:
            return "WARNUNG: Bei mehr als 9 Std. Arbeitszeit sind 45 Min. Pause erforderlich"
        elif self.arbeitszeit_stunden > 6 and self.pause_minuten < 30:
            return "WARNUNG: Bei mehr als 6 Std. Arbeitszeit sind 30 Min. Pause erforderlich"
        return "OK"


@dataclass
class Monatsnachweis:
    """Monatlicher Zeitnachweis"""
    mitarbeiter_name: str = ""
    mitarbeiter_id: str = ""
    monat: int = 0
    jahr: int = 0
    abteilung: str = ""
    vorgesetzter: str = ""
    
    # Eintraege
    eintraege: List[Tageseintrag] = field(default_factory=list)
    
    # Zusammenfassung
    soll_stunden: float = 0.0
    ist_stunden: float = 0.0
    ueberstunden_gesamt: float = 0.0
    urlaubstage: int = 0
    krankheitstage: int = 0
    
    # Unterschriften
    unterschrift_mitarbeiter: str = ""
    unterschrift_vorgesetzter: str = ""
    unterschrift_datum: str = ""

    def __post_init__(self):
        if not self.monat:
            self.monat = datetime.now().month
        if not self.jahr:
            self.jahr = datetime.now().year

    def berechne_zusammenfassung(self):
        """Berechnet die Monatszusammenfassung"""
        self.ist_stunden = sum(e.arbeitszeit_stunden for e in self.eintraege)
        self.ueberstunden_gesamt = sum(e.ueberstunden for e in self.eintraege)
        
        # Soll-Stunden basierend auf Arbeitstagen (vereinfacht)
        arbeitstage = len([e for e in self.eintraege if e.arbeitszeit_stunden > 0])
        self.soll_stunden = arbeitstage * STANDARD_ARBEITSZEIT

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, path: Optional[Path] = None) -> str:
        data = self.to_dict()
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        if path:
            path.write_text(json_str, encoding="utf-8")
        return json_str


class ZeitnachweisePDF(FPDF):
    """PDF-Generator fuer Zeitnachweis im FassadenFix Design"""

    def __init__(self):
        super().__init__("L")  # Querformat
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(*FF_GREEN)
        self.cell(0, 10, "FASSADENFIX", align="L")
        self.ln(8)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 8, "STUNDENNACHWEIS", align="L")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 10, f"FassadenFix | Stundennachweis | Seite {self.page_no()}", align="C")

    def mitarbeiter_info(self, nachweis: Monatsnachweis):
        monate = ["", "Januar", "Februar", "Maerz", "April", "Mai", "Juni",
                  "Juli", "August", "September", "Oktober", "November", "Dezember"]
        
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*FF_GRAY)
        
        # Linke Spalte
        self.cell(70, 6, f"Mitarbeiter: {nachweis.mitarbeiter_name}", align="L")
        # Rechte Spalte
        self.cell(0, 6, f"Monat: {monate[nachweis.monat]} {nachweis.jahr}", align="R")
        self.ln(6)
        
        self.cell(70, 6, f"Abteilung: {nachweis.abteilung}", align="L")
        self.cell(0, 6, f"Vorgesetzter: {nachweis.vorgesetzter}", align="R")
        self.ln(10)

    def stundenzettel_tabelle(self, eintraege: List[Tageseintrag]):
        # Tabellenkopf
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(*FF_GREEN)
        self.set_text_color(*FF_WHITE)
        
        spalten = [
            ("Datum", 22),
            ("Tag", 12),
            ("Beginn", 18),
            ("Ende", 18),
            ("Pause", 15),
            ("Projekt", 50),
            ("Taetigkeit", 60),
            ("Std.", 18),
            ("+-", 15),
            ("Notizen", 45)
        ]
        
        for titel, breite in spalten:
            self.cell(breite, 7, titel, border=1, align="C", fill=True)
        self.ln()
        
        # Tabelleninhalt
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*FF_GRAY)
        
        for eintrag in eintraege:
            # Zeilenfarbe alternieren
            if eintraege.index(eintrag) % 2 == 0:
                self.set_fill_color(245, 245, 245)
            else:
                self.set_fill_color(*FF_WHITE)
            
            # Datum formatieren
            datum_fmt = eintrag.datum
            try:
                d = datetime.strptime(eintrag.datum, "%Y-%m-%d")
                datum_fmt = d.strftime("%d.%m.")
            except ValueError:
                pass
            
            self.cell(22, 6, datum_fmt, border=1, align="C", fill=True)
            self.cell(12, 6, eintrag.wochentag, border=1, align="C", fill=True)
            self.cell(18, 6, eintrag.arbeitsbeginn, border=1, align="C", fill=True)
            self.cell(18, 6, eintrag.arbeitsende, border=1, align="C", fill=True)
            self.cell(15, 6, str(eintrag.pause_minuten), border=1, align="C", fill=True)
            self.cell(50, 6, eintrag.projekt[:20] if eintrag.projekt else "", border=1, align="L", fill=True)
            self.cell(60, 6, eintrag.taetigkeit[:25] if eintrag.taetigkeit else "", border=1, align="L", fill=True)
            self.cell(18, 6, f"{eintrag.arbeitszeit_stunden:.1f}", border=1, align="C", fill=True)
            
            # Ueberstunden farbig
            if eintrag.ueberstunden > 0:
                self.set_text_color(*FF_GREEN)
            elif eintrag.ueberstunden < 0:
                self.set_text_color(200, 50, 50)
            self.cell(15, 6, f"{eintrag.ueberstunden:+.1f}", border=1, align="C", fill=True)
            self.set_text_color(*FF_GRAY)
            
            self.cell(45, 6, eintrag.notizen[:18] if eintrag.notizen else "", border=1, align="L", fill=True)
            self.ln()

    def zusammenfassung(self, nachweis: Monatsnachweis):
        self.ln(5)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*FF_GRAY)
        
        # Zusammenfassungsbox
        self.set_fill_color(245, 245, 245)
        self.cell(70, 7, f"Soll-Stunden: {nachweis.soll_stunden:.1f}", border=1, align="L", fill=True)
        self.cell(70, 7, f"Ist-Stunden: {nachweis.ist_stunden:.1f}", border=1, align="L", fill=True)
        
        if nachweis.ueberstunden_gesamt >= 0:
            self.set_text_color(*FF_GREEN)
        else:
            self.set_text_color(200, 50, 50)
        self.cell(70, 7, f"Ueberstunden: {nachweis.ueberstunden_gesamt:+.1f}", border=1, align="L", fill=True)
        self.ln(7)
        
        self.set_text_color(*FF_GRAY)
        self.cell(70, 7, f"Urlaubstage: {nachweis.urlaubstage}", border=1, align="L", fill=True)
        self.cell(70, 7, f"Krankheitstage: {nachweis.krankheitstage}", border=1, align="L", fill=True)
        self.ln(15)

    def unterschriften(self):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*FF_GRAY)
        
        self.cell(0, 5, "Ich bestaetige die Richtigkeit der oben gemachten Angaben.", ln=True)
        self.ln(10)
        
        self.set_draw_color(*FF_GRAY)
        x = self.get_x()
        y = self.get_y()
        
        # Mitarbeiter
        self.line(x, y + 10, x + 80, y + 10)
        self.set_xy(x, y + 12)
        self.cell(80, 5, "Unterschrift Mitarbeiter", align="C")
        
        # Datum
        self.line(x + 100, y + 10, x + 150, y + 10)
        self.set_xy(x + 100, y + 12)
        self.cell(50, 5, "Datum", align="C")
        
        # Vorgesetzter
        self.line(x + 170, y + 10, x + 260, y + 10)
        self.set_xy(x + 170, y + 12)
        self.cell(90, 5, "Unterschrift Vorgesetzter", align="C")


def generate_zeitnachweis_pdf(nachweis: Monatsnachweis, output_path: Path) -> Path:
    """Generiert ein PDF-Dokument fuer den Zeitnachweis."""
    pdf = ZeitnachweisePDF()
    
    # Mitarbeiter-Info
    pdf.mitarbeiter_info(nachweis)
    
    # Stundenzettel-Tabelle
    pdf.stundenzettel_tabelle(nachweis.eintraege)
    
    # Zusammenfassung
    nachweis.berechne_zusammenfassung()
    pdf.zusammenfassung(nachweis)
    
    # Unterschriften
    pdf.unterschriften()
    
    # Speichern
    pdf.output(str(output_path))
    return output_path


def erstelle_beispiel_monat() -> Monatsnachweis:
    """Erstellt einen Beispiel-Monatsnachweis"""
    nachweis = Monatsnachweis(
        mitarbeiter_name="Max Mustermann",
        mitarbeiter_id="MA-001",
        monat=2,
        jahr=2026,
        abteilung="Anwendungstechnik",
        vorgesetzter="Thomas Mueller"
    )
    
    # Beispiel-Eintraege fuer eine Woche
    beispiel_tage = [
        ("2026-02-02", "07:00", "16:00", 30, "FF-2026-001", "Fassadenreinigung"),
        ("2026-02-03", "07:30", "16:30", 30, "FF-2026-001", "Fassadenreinigung"),
        ("2026-02-04", "07:00", "17:00", 45, "FF-2026-002", "Algenentfernung"),
        ("2026-02-05", "06:30", "15:30", 30, "FF-2026-002", "Algenentfernung"),
        ("2026-02-06", "07:00", "14:00", 30, "Buero", "Dokumentation"),
    ]
    
    for datum, beginn, ende, pause, projekt, taetigkeit in beispiel_tage:
        eintrag = Tageseintrag(
            datum=datum,
            arbeitsbeginn=beginn,
            arbeitsende=ende,
            pause_minuten=pause,
            projekt=projekt,
            taetigkeit=taetigkeit
        )
        eintrag.berechne_arbeitszeit()
        nachweis.eintraege.append(eintrag)
    
    return nachweis


def main():
    """Hauptfunktion fuer den Zeitnachweis."""
    print("\n" + "=" * 60)
    print("  FASSADENFIX ZEITNACHWEIS")
    print("=" * 60)
    
    # Beispiel-Nachweis erstellen
    nachweis = erstelle_beispiel_monat()
    
    # JSON speichern
    json_path = Path(f"zeitnachweis_{nachweis.monat:02d}_{nachweis.jahr}.json")
    nachweis.to_json(json_path)
    print(f"\nJSON gespeichert: {json_path}")
    
    # PDF generieren
    pdf_path = Path(f"zeitnachweis_{nachweis.monat:02d}_{nachweis.jahr}.pdf")
    generate_zeitnachweis_pdf(nachweis, pdf_path)
    print(f"PDF generiert: {pdf_path}")
    
    # Zusammenfassung
    nachweis.berechne_zusammenfassung()
    print(f"\nSoll-Stunden: {nachweis.soll_stunden:.1f}")
    print(f"Ist-Stunden: {nachweis.ist_stunden:.1f}")
    print(f"Ueberstunden: {nachweis.ueberstunden_gesamt:+.1f}")
    
    print("\n" + "=" * 60)
    print("  ZEITNACHWEIS ERSTELLT")
    print("=" * 60)


if __name__ == "__main__":
    main()
