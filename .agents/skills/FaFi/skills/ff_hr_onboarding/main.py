#!/usr/bin/env python3
"""
FassadenFix HR-Onboarding
Strukturierter Onboarding-Prozess fuer neue Mitarbeiter.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, asdict, field
from enum import Enum
from fpdf import FPDF

# FassadenFix Branding Farben
FF_GREEN = (119, 188, 31)
FF_GRAY = (78, 87, 88)
FF_WHITE = (255, 255, 255)


class ChecklistenStatus(Enum):
    OFFEN = "offen"
    IN_BEARBEITUNG = "in_bearbeitung"
    ABGESCHLOSSEN = "abgeschlossen"
    UEBERSPRUNGEN = "uebersprungen"


@dataclass
class ChecklistenPunkt:
    """Ein Punkt in der Onboarding-Checkliste"""
    id: str
    titel: str
    beschreibung: str
    kategorie: str
    pflicht: bool = True
    status: str = "offen"
    erledigt_am: str = ""
    notizen: str = ""


@dataclass
class Dokument:
    """Ein erforderliches Dokument"""
    typ: str
    name: str
    eingereicht: bool = False
    eingereicht_am: str = ""
    datei_pfad: str = ""


@dataclass
class OnboardingProzess:
    """Vollstaendiger Onboarding-Prozess"""
    mitarbeiter_id: str = ""
    mitarbeiter_name: str = ""
    position: str = ""
    eintrittsdatum: str = ""
    vorgesetzter: str = ""
    hr_verantwortlich: str = ""
    
    # Checkliste
    checkliste: List[ChecklistenPunkt] = field(default_factory=list)
    
    # Dokumente
    dokumente: List[Dokument] = field(default_factory=list)
    
    # Status
    gestartet_am: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    abgeschlossen_am: str = ""
    gesamtstatus: str = "in_bearbeitung"

    def __post_init__(self):
        if not self.checkliste:
            self.checkliste = self._standard_checkliste()
        if not self.dokumente:
            self.dokumente = self._standard_dokumente()

    def _standard_checkliste(self) -> List[ChecklistenPunkt]:
        """Erstellt die Standard-Onboarding-Checkliste"""
        return [
            ChecklistenPunkt("BEW-01", "Bewerber pruefen", "Zugewiesene potenzielle Bewerber pruefen", "Bewerberverfahren"),
            ChecklistenPunkt("BEW-02", "Einladung Gespraech", "Einladung zum Bewerbungsgespraech versenden", "Bewerberverfahren"),
            ChecklistenPunkt("DOK-01", "Personalausweis", "Kopie des Personalausweises anfordern", "Dokumentensammlung"),
            ChecklistenPunkt("DOK-02", "Fuehrerschein", "Kopie des Fuehrerscheins anfordern", "Dokumentensammlung"),
            ChecklistenPunkt("DOK-03", "KKV-Karte", "Kopie der Krankenversicherungskarte anfordern", "Dokumentensammlung"),
            ChecklistenPunkt("DOK-04", "Zertifikate", "Ausbildungszertifikate und Bedienerscheine anfordern", "Dokumentensammlung", pflicht=False),
            ChecklistenPunkt("PER-01", "Personalfragebogen", "Personalfragebogen aushaendigen und einsammeln", "Personalverwaltung"),
            ChecklistenPunkt("PRO-01", "Probearbeit planen", "Termin/Zeitraum der Probearbeit festlegen", "Probearbeit"),
            ChecklistenPunkt("PRO-02", "Probearbeit anmelden", "Probearbeit bei Personalabteilung anmelden", "Probearbeit"),
            ChecklistenPunkt("PRO-03", "Stundenzettel", "Stundenzettel unterschreiben lassen und einreichen", "Probearbeit"),
            ChecklistenPunkt("VER-01", "Arbeitsvertrag", "Arbeitsvertrag erstellen und unterzeichnen lassen", "Vertragswerk"),
            ChecklistenPunkt("VER-02", "Vertraulichkeit", "Vertraulichkeitsvereinbarung unterzeichnen lassen", "Vertragswerk"),
            ChecklistenPunkt("ARB-01", "Arbeitsmittel", "Arbeitsmittel-Vereinbarung erstellen", "Arbeitsmittel"),
            ChecklistenPunkt("ARB-02", "Dienstwagen", "Dienstwagen-Vertrag (falls zutreffend)", "Arbeitsmittel", pflicht=False),
            ChecklistenPunkt("SIC-01", "Arbeitsschutz", "Arbeitsschutzunterweisung durchfuehren", "Sicherheit"),
            ChecklistenPunkt("SIC-02", "Hebebuehne", "Hebebuehnen-Beauftragung (falls zutreffend)", "Sicherheit", pflicht=False),
            ChecklistenPunkt("ABN-01", "Abschluss", "Onboarding abschliessen und dokumentieren", "Abschluss"),
        ]

    def _standard_dokumente(self) -> List[Dokument]:
        """Erstellt die Standard-Dokumentenliste"""
        return [
            Dokument("ausweis", "Personalausweis (Kopie)"),
            Dokument("fuehrerschein", "Fuehrerschein (Kopie)"),
            Dokument("kkv", "Krankenversicherungskarte (Kopie)"),
            Dokument("zertifikate", "Ausbildungszertifikate"),
            Dokument("personalfragebogen", "Personalfragebogen (unterschrieben)"),
            Dokument("arbeitsvertrag", "Arbeitsvertrag (unterschrieben)"),
            Dokument("vertraulichkeit", "Vertraulichkeitsvereinbarung"),
        ]

    def fortschritt(self) -> float:
        """Berechnet den Fortschritt in Prozent"""
        if not self.checkliste:
            return 0.0
        erledigt = sum(1 for p in self.checkliste if p.status in ["abgeschlossen", "uebersprungen"])
        return (erledigt / len(self.checkliste)) * 100

    def naechster_schritt(self) -> Optional[ChecklistenPunkt]:
        """Gibt den naechsten offenen Schritt zurueck"""
        for punkt in self.checkliste:
            if punkt.status == "offen":
                return punkt
        return None

    def punkt_erledigen(self, punkt_id: str, notizen: str = ""):
        """Markiert einen Checklistenpunkt als erledigt"""
        for punkt in self.checkliste:
            if punkt.id == punkt_id:
                punkt.status = "abgeschlossen"
                punkt.erledigt_am = datetime.now().strftime("%Y-%m-%d %H:%M")
                punkt.notizen = notizen
                break

    def to_dict(self) -> dict:
        data = asdict(self)
        # Enum-Werte konvertieren
        for punkt in data.get("checkliste", []):
            if isinstance(punkt.get("status"), ChecklistenStatus):
                punkt["status"] = punkt["status"].value
        return data

    def to_json(self, path: Optional[Path] = None) -> str:
        data = self.to_dict()
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        if path:
            path.write_text(json_str, encoding="utf-8")
        return json_str


class OnboardingPDF(FPDF):
    """PDF-Generator fuer Onboarding-Status im FassadenFix Design"""

    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(*FF_GREEN)
        self.cell(0, 10, "FASSADENFIX", align="L")
        self.ln(8)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 8, "ONBOARDING CHECKLISTE", align="L")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 10, f"FassadenFix | Onboarding | Erstellt: {datetime.now().strftime('%d.%m.%Y')}", align="C")

    def mitarbeiter_info(self, prozess: OnboardingProzess):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*FF_GRAY)
        self.cell(50, 6, "Mitarbeiter:", align="L")
        self.set_font("Helvetica", "", 11)
        self.cell(0, 6, prozess.mitarbeiter_name, ln=True)
        
        self.set_font("Helvetica", "B", 11)
        self.cell(50, 6, "Position:", align="L")
        self.set_font("Helvetica", "", 11)
        self.cell(0, 6, prozess.position, ln=True)
        
        self.set_font("Helvetica", "B", 11)
        self.cell(50, 6, "Eintrittsdatum:", align="L")
        self.set_font("Helvetica", "", 11)
        self.cell(0, 6, prozess.eintrittsdatum, ln=True)
        
        # Fortschrittsbalken
        self.ln(5)
        fortschritt = prozess.fortschritt()
        self.set_font("Helvetica", "B", 10)
        self.cell(50, 6, f"Fortschritt: {fortschritt:.0f}%", align="L")
        self.ln(6)
        
        # Balken zeichnen
        x = self.get_x()
        y = self.get_y()
        self.set_fill_color(220, 220, 220)
        self.rect(x, y, 150, 8, "F")
        self.set_fill_color(*FF_GREEN)
        self.rect(x, y, 150 * (fortschritt / 100), 8, "F")
        self.ln(15)

    def checkliste_section(self, kategorie: str, punkte: List[ChecklistenPunkt]):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*FF_GREEN)
        self.cell(0, 8, kategorie, ln=True)
        self.set_draw_color(*FF_GREEN)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        
        for punkt in punkte:
            x = self.get_x()
            y = self.get_y()
            
            # Checkbox
            self.set_draw_color(*FF_GRAY)
            self.rect(x, y, 4, 4)
            if punkt.status == "abgeschlossen":
                self.set_font("Helvetica", "B", 8)
                self.set_text_color(*FF_GREEN)
                self.set_xy(x + 0.5, y - 0.5)
                self.cell(4, 4, "X")
            elif punkt.status == "uebersprungen":
                self.set_font("Helvetica", "", 8)
                self.set_text_color(*FF_GRAY)
                self.set_xy(x + 0.5, y - 0.5)
                self.cell(4, 4, "-")
            
            # Titel
            self.set_xy(x + 7, y)
            self.set_font("Helvetica", "", 10)
            self.set_text_color(*FF_GRAY)
            pflicht_marker = "" if punkt.pflicht else " (optional)"
            self.cell(0, 5, f"{punkt.titel}{pflicht_marker}", ln=True)
            
            # Status und Datum
            if punkt.erledigt_am:
                self.set_x(x + 7)
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(100, 100, 100)
                self.cell(0, 4, f"Erledigt: {punkt.erledigt_am}", ln=True)
            
            self.ln(2)
        
        self.ln(5)


def generate_onboarding_pdf(prozess: OnboardingProzess, output_path: Path) -> Path:
    """Generiert ein PDF-Dokument fuer den Onboarding-Status."""
    pdf = OnboardingPDF()
    
    # Mitarbeiter-Info
    pdf.mitarbeiter_info(prozess)
    
    # Checkliste nach Kategorien gruppieren
    kategorien = {}
    for punkt in prozess.checkliste:
        if punkt.kategorie not in kategorien:
            kategorien[punkt.kategorie] = []
        kategorien[punkt.kategorie].append(punkt)
    
    for kategorie, punkte in kategorien.items():
        pdf.checkliste_section(kategorie, punkte)
    
    # Speichern
    pdf.output(str(output_path))
    return output_path


def interactive_onboarding() -> OnboardingProzess:
    """Interaktive Erfassung eines neuen Onboarding-Prozesses."""
    print("\n" + "=" * 60)
    print("  FASSADENFIX ONBOARDING")
    print("=" * 60)

    prozess = OnboardingProzess()

    # Mitarbeiterdaten
    print("\n--- MITARBEITERDATEN ---")
    prozess.mitarbeiter_name = input("Name des neuen Mitarbeiters: ").strip()
    prozess.position = input("Position: ").strip()
    prozess.eintrittsdatum = input("Geplantes Eintrittsdatum (TT.MM.JJJJ): ").strip()
    prozess.vorgesetzter = input("Vorgesetzter: ").strip()
    prozess.hr_verantwortlich = input("HR-Verantwortlich: ").strip()

    # ID generieren
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    prozess.mitarbeiter_id = f"ONB-{timestamp}"

    return prozess


def main():
    """Hauptfunktion fuer das interaktive Onboarding."""
    prozess = interactive_onboarding()

    # JSON speichern
    safe_name = prozess.mitarbeiter_name.replace(" ", "_")[:20]
    json_path = Path(f"onboarding_{safe_name}_{prozess.mitarbeiter_id}.json")
    prozess.to_json(json_path)
    print(f"\nJSON gespeichert: {json_path}")

    # PDF generieren
    pdf_path = Path(f"onboarding_{safe_name}_{prozess.mitarbeiter_id}.pdf")
    generate_onboarding_pdf(prozess, pdf_path)
    print(f"PDF generiert: {pdf_path}")

    # Status anzeigen
    print(f"\nFortschritt: {prozess.fortschritt():.0f}%")
    naechster = prozess.naechster_schritt()
    if naechster:
        print(f"Naechster Schritt: {naechster.titel}")

    print("\n" + "=" * 60)
    print("  ONBOARDING GESTARTET")
    print("=" * 60)


if __name__ == "__main__":
    main()
