#!/usr/bin/env python3
"""
FassadenFix Fuhrpark-Skill
Verwaltet den FassadenFix Fuhrpark und die Fahrzeugzuordnung.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict, field
from fpdf import FPDF

# FassadenFix Branding Farben
FF_GREEN = (119, 188, 31)  # #77bc1f
FF_GRAY = (78, 87, 88)     # #4e5758


@dataclass
class Fahrzeug:
    """Fahrzeugdaten"""
    fahrzeug_id: str = ""
    kennzeichen: str = ""
    typ: str = ""  # transporter, pkw, lkw, anhaenger, spezial
    marke: str = ""
    modell: str = ""
    baujahr: int = 0
    km_stand: int = 0
    status: str = "verfuegbar"  # verfuegbar, gebucht, wartung, defekt
    erstellt_am: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Buchung:
    """Fahrzeugbuchung"""
    buchung_id: str = ""
    fahrzeug_id: str = ""
    baustelle_id: str = ""
    fahrer: str = ""
    datum_von: str = ""
    datum_bis: str = ""
    status: str = "aktiv"  # aktiv, abgeschlossen, storniert


@dataclass
class Wartung:
    """Wartungseintrag"""
    wartung_id: str = ""
    fahrzeug_id: str = ""
    typ: str = ""  # inspektion, oelwechsel, reifen, reparatur, tuev
    datum: str = ""
    km_stand: int = 0
    kosten: float = 0.0
    werkstatt: str = ""
    notizen: str = ""


@dataclass
class Tankbeleg:
    """Tankbeleg"""
    beleg_id: str = ""
    fahrzeug_id: str = ""
    datum: str = ""
    liter: float = 0.0
    kosten: float = 0.0
    km_stand: int = 0
    tankstelle: str = ""


class FuhrparkPDF(FPDF):
    """PDF-Generator für Fuhrparkberichte"""
    
    def __init__(self, fahrzeug: Fahrzeug, buchungen: List[Buchung] = None, 
                 wartungen: List[Wartung] = None, tankbelege: List[Tankbeleg] = None):
        super().__init__()
        self.fahrzeug = fahrzeug
        self.buchungen = buchungen or []
        self.wartungen = wartungen or []
        self.tankbelege = tankbelege or []
        self.add_page()
        
    def header(self):
        self.set_fill_color(*FF_GREEN)
        self.rect(0, 0, 210, 25, 'F')
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'FassadenFix - Fahrzeugbericht', 0, 1, 'C')
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
        
    def generate(self) -> bytes:
        f = self.fahrzeug
        
        # Fahrzeuginformationen
        self.add_section("Fahrzeuginformationen")
        self.add_field("Fahrzeug-ID", f.fahrzeug_id)
        self.add_field("Kennzeichen", f.kennzeichen)
        self.add_field("Typ", f.typ.upper())
        self.add_field("Marke / Modell", f"{f.marke} {f.modell}")
        self.add_field("Baujahr", str(f.baujahr))
        self.add_field("Kilometerstand", f"{f.km_stand:,} km".replace(",", "."))
        self.add_field("Status", f.status.upper())
        self.ln(5)
        
        # Aktive Buchungen
        if self.buchungen:
            self.add_section("Aktive Buchungen")
            for b in self.buchungen:
                self.add_field("Baustelle", b.baustelle_id)
                self.add_field("Fahrer", b.fahrer)
                self.add_field("Zeitraum", f"{b.datum_von} bis {b.datum_bis}")
                self.ln(2)
            self.ln(3)
        
        # Wartungshistorie
        if self.wartungen:
            self.add_section("Letzte Wartungen")
            for w in self.wartungen[-5:]:  # Letzte 5 Wartungen
                self.add_field(w.typ.upper(), f"{w.datum} - {w.kosten:.2f} EUR")
            self.ln(3)
        
        # Tankbelege
        if self.tankbelege:
            self.add_section("Letzte Tankbelege")
            for t in self.tankbelege[-5:]:  # Letzte 5 Belege
                self.add_field(t.datum, f"{t.liter:.1f} L - {t.kosten:.2f} EUR")
        
        return self.output()


def generate_id(prefix: str) -> str:
    """Generiert eine eindeutige ID"""
    import random
    suffix = f"{random.randint(1, 999):03d}"
    return f"FF-{prefix}-{suffix}"


def execute(params: dict) -> dict:
    """
    Führt den Fuhrpark-Skill aus.
    
    Args:
        params: Dictionary mit Aktionsparametern
        
    Returns:
        Dictionary mit Ergebnis
    """
    try:
        aktion = params.get('aktion', '')
        
        if aktion == 'fahrzeug_anlegen':
            fahrzeug_daten = params.get('fahrzeug_daten', {})
            fahrzeug = Fahrzeug(
                fahrzeug_id=generate_id("FZG"),
                kennzeichen=fahrzeug_daten.get('kennzeichen', ''),
                typ=fahrzeug_daten.get('typ', 'transporter'),
                marke=fahrzeug_daten.get('marke', ''),
                modell=fahrzeug_daten.get('modell', ''),
                baujahr=fahrzeug_daten.get('baujahr', 0),
                km_stand=fahrzeug_daten.get('km_stand', 0),
                status='verfuegbar'
            )
            
            # PDF generieren
            pdf = FuhrparkPDF(fahrzeug)
            pdf_bytes = pdf.generate()
            
            output_dir = Path("/tmp/fassadenfix")
            output_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = output_dir / f"{fahrzeug.fahrzeug_id}.pdf"
            pdf_path.write_bytes(pdf_bytes)
            
            return {
                "status": "success",
                "aktion": "fahrzeug_anlegen",
                "fahrzeug_id": fahrzeug.fahrzeug_id,
                "fahrzeug_status": fahrzeug.status,
                "pdf_path": str(pdf_path),
                "fahrzeug_daten": asdict(fahrzeug)
            }
            
        elif aktion == 'fahrzeug_buchen':
            buchung_daten = params.get('buchung', {})
            buchung = Buchung(
                buchung_id=generate_id("BUC"),
                fahrzeug_id=params.get('fahrzeug_id', ''),
                baustelle_id=buchung_daten.get('baustelle_id', ''),
                fahrer=buchung_daten.get('fahrer', ''),
                datum_von=buchung_daten.get('datum_von', ''),
                datum_bis=buchung_daten.get('datum_bis', ''),
                status='aktiv'
            )
            
            return {
                "status": "success",
                "aktion": "fahrzeug_buchen",
                "buchung_id": buchung.buchung_id,
                "fahrzeug_id": buchung.fahrzeug_id,
                "buchung_daten": asdict(buchung)
            }
            
        elif aktion == 'wartung_eintragen':
            wartung_daten = params.get('wartung', {})
            wartung = Wartung(
                wartung_id=generate_id("WAR"),
                fahrzeug_id=params.get('fahrzeug_id', ''),
                typ=wartung_daten.get('typ', ''),
                datum=wartung_daten.get('datum', datetime.now().strftime("%Y-%m-%d")),
                km_stand=wartung_daten.get('km_stand', 0),
                kosten=wartung_daten.get('kosten', 0.0),
                werkstatt=wartung_daten.get('werkstatt', ''),
                notizen=wartung_daten.get('notizen', '')
            )
            
            # Nächste Wartung berechnen (z.B. in 6 Monaten oder 15.000 km)
            naechste_wartung_datum = (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")
            naechste_wartung_km = wartung.km_stand + 15000
            
            return {
                "status": "success",
                "aktion": "wartung_eintragen",
                "wartung_id": wartung.wartung_id,
                "fahrzeug_id": wartung.fahrzeug_id,
                "wartung_daten": asdict(wartung),
                "naechste_wartung": {
                    "datum": naechste_wartung_datum,
                    "km_stand": naechste_wartung_km
                }
            }
            
        elif aktion == 'tankbeleg_erfassen':
            tankbeleg_daten = params.get('tankbeleg', {})
            tankbeleg = Tankbeleg(
                beleg_id=generate_id("TNK"),
                fahrzeug_id=params.get('fahrzeug_id', ''),
                datum=tankbeleg_daten.get('datum', datetime.now().strftime("%Y-%m-%d")),
                liter=tankbeleg_daten.get('liter', 0.0),
                kosten=tankbeleg_daten.get('kosten', 0.0),
                km_stand=tankbeleg_daten.get('km_stand', 0),
                tankstelle=tankbeleg_daten.get('tankstelle', '')
            )
            
            # Verbrauch berechnen (falls möglich)
            verbrauch_pro_100km = None
            if tankbeleg.liter > 0 and tankbeleg.km_stand > 0:
                # Vereinfachte Berechnung
                verbrauch_pro_100km = round((tankbeleg.liter / 100) * 100, 2)
            
            return {
                "status": "success",
                "aktion": "tankbeleg_erfassen",
                "beleg_id": tankbeleg.beleg_id,
                "fahrzeug_id": tankbeleg.fahrzeug_id,
                "tankbeleg_daten": asdict(tankbeleg),
                "preis_pro_liter": round(tankbeleg.kosten / tankbeleg.liter, 3) if tankbeleg.liter > 0 else None
            }
            
        elif aktion == 'status_abfragen':
            fahrzeug_id = params.get('fahrzeug_id', '')
            
            # Simulierte Statusabfrage
            return {
                "status": "success",
                "aktion": "status_abfragen",
                "fahrzeug_id": fahrzeug_id,
                "fahrzeug_status": "verfuegbar",
                "buchungen": [],
                "naechste_wartung": {
                    "datum": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                    "typ": "inspektion"
                }
            }
            
        else:
            return {
                "status": "error",
                "message": f"Unbekannte Aktion: {aktion}. Verfügbare Aktionen: fahrzeug_anlegen, fahrzeug_buchen, wartung_eintragen, tankbeleg_erfassen, status_abfragen"
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
