#!/usr/bin/env python3
"""
FassadenFix Baustellen-Skill
Verwaltet Baustelleninformationen und -logistik für FassadenFix-Projekte.
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
class Adresse:
    """Adressdaten der Baustelle"""
    strasse: str = ""
    plz: str = ""
    ort: str = ""


@dataclass
class Kontakt:
    """Kontaktdaten"""
    name: str = ""
    telefon: str = ""
    email: str = ""


@dataclass
class Zugang:
    """Zugangsinformationen"""
    schluessel: str = ""
    code: str = ""
    ansprechpartner: str = ""
    oeffnungszeiten: str = ""


@dataclass
class Sicherheit:
    """Sicherheitsanforderungen"""
    geruest: bool = False
    absperrung: bool = False
    psa: List[str] = field(default_factory=list)
    gefaehrdungen: List[str] = field(default_factory=list)


@dataclass
class Baustelle:
    """Vollständige Baustellendaten"""
    projekt_name: str = ""
    baustellen_id: str = ""
    adresse: Adresse = field(default_factory=Adresse)
    bauherr: Kontakt = field(default_factory=Kontakt)
    bauleiter: str = ""
    startdatum: str = ""
    enddatum: str = ""
    status: str = "geplant"
    zugang: Zugang = field(default_factory=Zugang)
    sicherheit: Sicherheit = field(default_factory=Sicherheit)
    ressourcen: List[Dict[str, Any]] = field(default_factory=list)
    notizen: str = ""
    erstellt_am: str = field(default_factory=lambda: datetime.now().isoformat())


class BaustellenPDF(FPDF):
    """PDF-Generator für Baustellendatenblätter"""
    
    def __init__(self, baustelle: Baustelle):
        super().__init__()
        self.baustelle = baustelle
        self.add_page()
        
    def header(self):
        # FassadenFix Header
        self.set_fill_color(*FF_GREEN)
        self.rect(0, 0, 210, 25, 'F')
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'FassadenFix - Baustellendatenblatt', 0, 1, 'C')
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
        b = self.baustelle
        
        # Projektinformationen
        self.add_section("Projektinformationen")
        self.add_field("Baustellen-ID", b.baustellen_id)
        self.add_field("Projektname", b.projekt_name)
        self.add_field("Status", b.status.upper())
        self.add_field("Bauleiter", b.bauleiter)
        self.ln(5)
        
        # Adresse
        self.add_section("Standort")
        self.add_field("Straße", b.adresse.strasse)
        self.add_field("PLZ / Ort", f"{b.adresse.plz} {b.adresse.ort}")
        self.ln(5)
        
        # Bauherr
        self.add_section("Bauherr / Auftraggeber")
        self.add_field("Name", b.bauherr.name)
        self.add_field("Telefon", b.bauherr.telefon)
        self.add_field("E-Mail", b.bauherr.email)
        self.ln(5)
        
        # Zeitraum
        self.add_section("Projektzeitraum")
        self.add_field("Startdatum", b.startdatum)
        self.add_field("Enddatum", b.enddatum or "Offen")
        self.ln(5)
        
        # Zugang
        if b.zugang.schluessel or b.zugang.code or b.zugang.ansprechpartner:
            self.add_section("Zugangsinformationen")
            if b.zugang.schluessel:
                self.add_field("Schlüssel", b.zugang.schluessel)
            if b.zugang.code:
                self.add_field("Zugangscode", b.zugang.code)
            if b.zugang.ansprechpartner:
                self.add_field("Ansprechpartner", b.zugang.ansprechpartner)
            if b.zugang.oeffnungszeiten:
                self.add_field("Öffnungszeiten", b.zugang.oeffnungszeiten)
            self.ln(5)
        
        # Sicherheit
        self.add_section("Sicherheitsanforderungen")
        self.add_field("Gerüst erforderlich", "Ja" if b.sicherheit.geruest else "Nein")
        self.add_field("Absperrung erforderlich", "Ja" if b.sicherheit.absperrung else "Nein")
        if b.sicherheit.psa:
            self.add_field("PSA", ", ".join(b.sicherheit.psa))
        if b.sicherheit.gefaehrdungen:
            self.add_field("Gefährdungen", ", ".join(b.sicherheit.gefaehrdungen))
        self.ln(5)
        
        # Ressourcen
        if b.ressourcen:
            self.add_section("Zugewiesene Ressourcen")
            for res in b.ressourcen:
                res_type = res.get('typ', 'Ressource')
                res_name = res.get('name', 'Unbekannt')
                self.add_field(res_type, res_name)
            self.ln(5)
        
        # Notizen
        if b.notizen:
            self.add_section("Notizen")
            self.set_font('Helvetica', '', 10)
            self.set_text_color(0, 0, 0)
            self.multi_cell(0, 6, b.notizen)
        
        return self.output()


def generate_baustellen_id() -> str:
    """Generiert eine eindeutige Baustellen-ID"""
    timestamp = datetime.now().strftime("%Y%m%d")
    import random
    suffix = f"{random.randint(1, 999):03d}"
    return f"FF-BAU-{timestamp}-{suffix}"


def execute(params: dict) -> dict:
    """
    Führt den Baustellen-Skill aus.
    
    Args:
        params: Dictionary mit Baustellendaten
        
    Returns:
        Dictionary mit Ergebnis (baustellen_id, status, pdf_path, baustellen_daten)
    """
    try:
        # Adresse parsen
        adresse_data = params.get('adresse', {})
        adresse = Adresse(
            strasse=adresse_data.get('strasse', ''),
            plz=adresse_data.get('plz', ''),
            ort=adresse_data.get('ort', '')
        )
        
        # Bauherr parsen
        bauherr_data = params.get('bauherr', {})
        bauherr = Kontakt(
            name=bauherr_data.get('name', ''),
            telefon=bauherr_data.get('telefon', ''),
            email=bauherr_data.get('email', '')
        )
        
        # Zugang parsen
        zugang_data = params.get('zugang', {})
        zugang = Zugang(
            schluessel=zugang_data.get('schluessel', ''),
            code=zugang_data.get('code', ''),
            ansprechpartner=zugang_data.get('ansprechpartner', ''),
            oeffnungszeiten=zugang_data.get('oeffnungszeiten', '')
        )
        
        # Sicherheit parsen
        sicherheit_data = params.get('sicherheit', {})
        sicherheit = Sicherheit(
            geruest=sicherheit_data.get('geruest', False),
            absperrung=sicherheit_data.get('absperrung', False),
            psa=sicherheit_data.get('psa', []),
            gefaehrdungen=sicherheit_data.get('gefaehrdungen', [])
        )
        
        # Baustelle erstellen
        baustelle = Baustelle(
            projekt_name=params.get('projekt_name', ''),
            baustellen_id=generate_baustellen_id(),
            adresse=adresse,
            bauherr=bauherr,
            bauleiter=params.get('bauleiter', ''),
            startdatum=params.get('startdatum', ''),
            enddatum=params.get('enddatum', ''),
            status='geplant',
            zugang=zugang,
            sicherheit=sicherheit,
            ressourcen=params.get('ressourcen', []),
            notizen=params.get('notizen', '')
        )
        
        # PDF generieren
        pdf = BaustellenPDF(baustelle)
        pdf_bytes = pdf.generate()
        
        # PDF speichern
        output_dir = Path("/tmp/fassadenfix")
        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = output_dir / f"{baustelle.baustellen_id}.pdf"
        pdf_path.write_bytes(pdf_bytes)
        
        return {
            "status": "success",
            "baustellen_id": baustelle.baustellen_id,
            "baustellen_status": baustelle.status,
            "pdf_path": str(pdf_path),
            "baustellen_daten": asdict(baustelle)
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
