#!/usr/bin/env python3
"""
FassadenFix Offboarding-Skill
Unterstützt den Offboarding-Prozess für ausscheidende Mitarbeiter.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict, field
from fpdf import FPDF

# FassadenFix Branding Farben
FF_GREEN = (119, 188, 31)  # #77bc1f
FF_GRAY = (78, 87, 88)     # #4e5758


@dataclass
class Mitarbeiter:
    """Mitarbeiterdaten"""
    name: str = ""
    personalnummer: str = ""
    abteilung: str = ""
    position: str = ""
    eintrittsdatum: str = ""


@dataclass
class Rueckgabe:
    """Rückgabe-Checkliste"""
    schluessel: bool = False
    laptop: bool = False
    handy: bool = False
    arbeitskleidung: bool = False
    werkzeug: bool = False
    fahrzeug: bool = False
    tankkarten: bool = False


@dataclass
class Zugriffsrechte:
    """Zugriffsrechte-Status"""
    email: bool = False
    systeme: bool = False
    gebaeude: bool = False
    fahrzeuge: bool = False


@dataclass
class Wissenstransfer:
    """Wissenstransfer-Dokumentation"""
    nachfolger: str = ""
    uebergabe_themen: List[str] = field(default_factory=list)
    dokumentation: str = ""
    abgeschlossen: bool = False


@dataclass
class Zeugnis:
    """Zeugnis-Anforderungen"""
    typ: str = "qualifiziert"  # einfach, qualifiziert
    bewertung: str = ""
    schwerpunkte: List[str] = field(default_factory=list)
    erstellt: bool = False


@dataclass
class Offboarding:
    """Vollständige Offboarding-Daten"""
    offboarding_id: str = ""
    mitarbeiter: Mitarbeiter = field(default_factory=Mitarbeiter)
    austrittsdatum: str = ""
    austrittsgrund: str = ""
    status: str = "gestartet"  # gestartet, in_bearbeitung, abgeschlossen
    rueckgabe: Rueckgabe = field(default_factory=Rueckgabe)
    zugriffsrechte: Zugriffsrechte = field(default_factory=Zugriffsrechte)
    wissenstransfer: Wissenstransfer = field(default_factory=Wissenstransfer)
    zeugnis: Zeugnis = field(default_factory=Zeugnis)
    austrittsgespraech: bool = False
    notizen: str = ""
    erstellt_am: str = field(default_factory=lambda: datetime.now().isoformat())


class OffboardingPDF(FPDF):
    """PDF-Generator für Offboarding-Protokolle"""
    
    def __init__(self, offboarding: Offboarding):
        super().__init__()
        self.offboarding = offboarding
        self.add_page()
        
    def header(self):
        self.set_fill_color(*FF_GREEN)
        self.rect(0, 0, 210, 25, 'F')
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'FassadenFix - Offboarding-Protokoll', 0, 1, 'C')
        self.ln(15)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(*FF_GRAY)
        self.cell(0, 10, f'Seite {self.page_no()} | Erstellt: {datetime.now().strftime("%d.%m.%Y %H:%M")}', 0, 0, 'C')
        
    def add_section(self, title: str):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(*FF_GREEN)
        self.cell(0, 10, title, 0, 1)
        self.set_draw_color(*FF_GREEN)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        
    def add_field(self, label: str, value: str):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*FF_GRAY)
        self.cell(60, 7, label + ":", 0, 0)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 7, str(value), 0, 1)
        
    def add_checkbox(self, label: str, checked: bool):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        checkbox = "[X]" if checked else "[ ]"
        self.cell(0, 6, f"  {checkbox} {label}", 0, 1)
        
    def generate(self) -> bytes:
        o = self.offboarding
        m = o.mitarbeiter
        
        # Mitarbeiterinformationen
        self.add_section("Mitarbeiterinformationen")
        self.add_field("Offboarding-ID", o.offboarding_id)
        self.add_field("Name", m.name)
        self.add_field("Personalnummer", m.personalnummer)
        self.add_field("Abteilung", m.abteilung)
        self.add_field("Position", m.position)
        self.add_field("Eintrittsdatum", m.eintrittsdatum)
        self.add_field("Austrittsdatum", o.austrittsdatum)
        self.add_field("Austrittsgrund", o.austrittsgrund.replace("_", " ").title())
        self.add_field("Status", o.status.upper())
        self.ln(5)
        
        # Rückgabe von Firmeneigentum
        self.add_section("Rückgabe von Firmeneigentum")
        r = o.rueckgabe
        self.add_checkbox("Schlüssel / Zugangskarten", r.schluessel)
        self.add_checkbox("Laptop / Computer", r.laptop)
        self.add_checkbox("Diensthandy", r.handy)
        self.add_checkbox("Arbeitskleidung / PSA", r.arbeitskleidung)
        self.add_checkbox("Werkzeug / Geräte", r.werkzeug)
        self.add_checkbox("Dienstfahrzeug", r.fahrzeug)
        self.add_checkbox("Tankkarten / Firmenkreditkarten", r.tankkarten)
        self.ln(5)
        
        # Zugriffsrechte
        self.add_section("Zugriffsrechte entziehen")
        z = o.zugriffsrechte
        self.add_checkbox("E-Mail-Konto deaktiviert", z.email)
        self.add_checkbox("Systemzugänge gesperrt", z.systeme)
        self.add_checkbox("Gebäudezugang entzogen", z.gebaeude)
        self.add_checkbox("Fahrzeugberechtigung entfernt", z.fahrzeuge)
        self.ln(5)
        
        # Wissenstransfer
        self.add_section("Wissenstransfer")
        w = o.wissenstransfer
        self.add_field("Nachfolger", w.nachfolger or "Nicht definiert")
        if w.uebergabe_themen:
            self.add_field("Übergabethemen", ", ".join(w.uebergabe_themen))
        self.add_checkbox("Wissenstransfer abgeschlossen", w.abgeschlossen)
        self.ln(5)
        
        # Zeugnis
        self.add_section("Arbeitszeugnis")
        ze = o.zeugnis
        self.add_field("Zeugnistyp", ze.typ.title())
        self.add_field("Bewertung", ze.bewertung or "Ausstehend")
        if ze.schwerpunkte:
            self.add_field("Schwerpunkte", ", ".join(ze.schwerpunkte))
        self.add_checkbox("Zeugnis erstellt", ze.erstellt)
        self.ln(5)
        
        # Abschluss
        self.add_section("Abschluss")
        self.add_checkbox("Austrittsgespräch geführt", o.austrittsgespraech)
        
        # Notizen
        if o.notizen:
            self.ln(5)
            self.add_section("Notizen")
            self.set_font('Helvetica', '', 10)
            self.set_text_color(0, 0, 0)
            self.multi_cell(0, 6, o.notizen)
        
        # Unterschriftenfeld
        self.ln(15)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*FF_GRAY)
        self.cell(90, 10, "_" * 40, 0, 0, 'C')
        self.cell(90, 10, "_" * 40, 0, 1, 'C')
        self.cell(90, 5, "Mitarbeiter/in", 0, 0, 'C')
        self.cell(90, 5, "Personalverantwortliche/r", 0, 1, 'C')
        
        return self.output()


def generate_offboarding_id() -> str:
    """Generiert eine eindeutige Offboarding-ID"""
    timestamp = datetime.now().strftime("%Y%m%d")
    import random
    suffix = f"{random.randint(1, 999):03d}"
    return f"FF-OFF-{timestamp}-{suffix}"


def get_offene_punkte(offboarding: Offboarding) -> List[str]:
    """Ermittelt die noch offenen Punkte im Offboarding-Prozess"""
    offene = []
    
    r = offboarding.rueckgabe
    if not r.schluessel:
        offene.append("Schlüssel / Zugangskarten zurückgeben")
    if not r.laptop:
        offene.append("Laptop / Computer zurückgeben")
    if not r.handy:
        offene.append("Diensthandy zurückgeben")
    if not r.arbeitskleidung:
        offene.append("Arbeitskleidung / PSA zurückgeben")
    if not r.werkzeug:
        offene.append("Werkzeug / Geräte zurückgeben")
    if not r.fahrzeug:
        offene.append("Dienstfahrzeug zurückgeben")
    if not r.tankkarten:
        offene.append("Tankkarten / Firmenkreditkarten zurückgeben")
    
    z = offboarding.zugriffsrechte
    if not z.email:
        offene.append("E-Mail-Konto deaktivieren")
    if not z.systeme:
        offene.append("Systemzugänge sperren")
    if not z.gebaeude:
        offene.append("Gebäudezugang entziehen")
    if not z.fahrzeuge:
        offene.append("Fahrzeugberechtigung entfernen")
    
    if not offboarding.wissenstransfer.abgeschlossen:
        offene.append("Wissenstransfer durchführen")
    
    if not offboarding.zeugnis.erstellt:
        offene.append("Arbeitszeugnis erstellen")
    
    if not offboarding.austrittsgespraech:
        offene.append("Austrittsgespräch führen")
    
    return offene


def execute(params: dict) -> dict:
    """
    Führt den Offboarding-Skill aus.
    
    Args:
        params: Dictionary mit Offboarding-Daten
        
    Returns:
        Dictionary mit Ergebnis (offboarding_id, status, checkliste, offene_punkte, pdf_path)
    """
    try:
        # Mitarbeiter parsen
        mitarbeiter_data = params.get('mitarbeiter', {})
        mitarbeiter = Mitarbeiter(
            name=mitarbeiter_data.get('name', ''),
            personalnummer=mitarbeiter_data.get('personalnummer', ''),
            abteilung=mitarbeiter_data.get('abteilung', ''),
            position=mitarbeiter_data.get('position', ''),
            eintrittsdatum=mitarbeiter_data.get('eintrittsdatum', '')
        )
        
        # Rückgabe parsen
        rueckgabe_data = params.get('rueckgabe', {})
        rueckgabe = Rueckgabe(
            schluessel=rueckgabe_data.get('schluessel', False),
            laptop=rueckgabe_data.get('laptop', False),
            handy=rueckgabe_data.get('handy', False),
            arbeitskleidung=rueckgabe_data.get('arbeitskleidung', False),
            werkzeug=rueckgabe_data.get('werkzeug', False),
            fahrzeug=rueckgabe_data.get('fahrzeug', False),
            tankkarten=rueckgabe_data.get('tankkarten', False)
        )
        
        # Zugriffsrechte parsen
        zugriffsrechte_data = params.get('zugriffsrechte', {})
        zugriffsrechte = Zugriffsrechte(
            email=zugriffsrechte_data.get('email', False),
            systeme=zugriffsrechte_data.get('systeme', False),
            gebaeude=zugriffsrechte_data.get('gebaeude', False),
            fahrzeuge=zugriffsrechte_data.get('fahrzeuge', False)
        )
        
        # Wissenstransfer parsen
        wissenstransfer_data = params.get('wissenstransfer', {})
        wissenstransfer = Wissenstransfer(
            nachfolger=wissenstransfer_data.get('nachfolger', ''),
            uebergabe_themen=wissenstransfer_data.get('uebergabe_themen', []),
            dokumentation=wissenstransfer_data.get('dokumentation', ''),
            abgeschlossen=wissenstransfer_data.get('abgeschlossen', False)
        )
        
        # Zeugnis parsen
        zeugnis_data = params.get('zeugnis', {})
        zeugnis = Zeugnis(
            typ=zeugnis_data.get('typ', 'qualifiziert'),
            bewertung=zeugnis_data.get('bewertung', ''),
            schwerpunkte=zeugnis_data.get('schwerpunkte', []),
            erstellt=zeugnis_data.get('erstellt', False)
        )
        
        # Offboarding erstellen
        offboarding = Offboarding(
            offboarding_id=generate_offboarding_id(),
            mitarbeiter=mitarbeiter,
            austrittsdatum=params.get('austrittsdatum', ''),
            austrittsgrund=params.get('austrittsgrund', ''),
            status='gestartet',
            rueckgabe=rueckgabe,
            zugriffsrechte=zugriffsrechte,
            wissenstransfer=wissenstransfer,
            zeugnis=zeugnis,
            austrittsgespraech=params.get('austrittsgespraech', False),
            notizen=params.get('notizen', '')
        )
        
        # Offene Punkte ermitteln
        offene_punkte = get_offene_punkte(offboarding)
        
        # Status aktualisieren
        if len(offene_punkte) == 0:
            offboarding.status = 'abgeschlossen'
        elif len(offene_punkte) < 15:
            offboarding.status = 'in_bearbeitung'
        
        # PDF generieren
        pdf = OffboardingPDF(offboarding)
        pdf_bytes = pdf.generate()
        
        # PDF speichern
        output_dir = Path("/tmp/fassadenfix")
        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = output_dir / f"{offboarding.offboarding_id}.pdf"
        pdf_path.write_bytes(pdf_bytes)
        
        # Checkliste erstellen
        checkliste = {
            "rueckgabe": asdict(rueckgabe),
            "zugriffsrechte": asdict(zugriffsrechte),
            "wissenstransfer_abgeschlossen": wissenstransfer.abgeschlossen,
            "zeugnis_erstellt": zeugnis.erstellt,
            "austrittsgespraech": offboarding.austrittsgespraech
        }
        
        return {
            "status": "success",
            "offboarding_id": offboarding.offboarding_id,
            "offboarding_status": offboarding.status,
            "checkliste": checkliste,
            "offene_punkte": offene_punkte,
            "fortschritt": f"{15 - len(offene_punkte)}/15 Punkte erledigt",
            "pdf_path": str(pdf_path),
            "offboarding_daten": asdict(offboarding)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    import sys
    params = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = execute(params)
    print(json.dumps(result, ensure_ascii=False, indent=2))
