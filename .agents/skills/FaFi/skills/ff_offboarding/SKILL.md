---
name: ff-offboarding
description: "Unterstützt den Offboarding-Prozess für ausscheidende Mitarbeiter. Verwenden für: Rückgabe von Firmeneigentum, Zugriffsrechte-Entzug, Wissenstransfer, Austrittsdokumentation, Zeugnis-Erstellung."
version: 1.0.0
author: FassadenFix
category: HR & Interne Prozesse
---

# FassadenFix Offboarding-Skill

## Übersicht

Der `ff-offboarding` Skill unterstützt den strukturierten Offboarding-Prozess für ausscheidende Mitarbeiter bei FassadenFix. Er verwaltet Checklisten für die Rückgabe von Firmeneigentum, den Entzug von Zugriffsrechten, den Wissenstransfer und die Austrittsdokumentation.

## Hauptfunktionen

| Funktion | Beschreibung |
|----------|--------------|
| **Rückgabe-Checkliste** | Tracking aller zurückzugebenden Gegenstände |
| **Zugriffsrechte-Management** | Dokumentation zu entziehender Berechtigungen |
| **Wissenstransfer** | Strukturierte Übergabe an Nachfolger |
| **Zeugnis-Vorbereitung** | Anforderungen für Arbeitszeugnis |
| **PDF-Generierung** | Automatische Erstellung des Offboarding-Protokolls |

## Offboarding-Checkliste (15 Punkte)

### Rückgabe von Firmeneigentum
1. ☐ Schlüssel / Zugangskarten
2. ☐ Laptop / Computer
3. ☐ Diensthandy
4. ☐ Arbeitskleidung / PSA
5. ☐ Werkzeug / Geräte
6. ☐ Dienstfahrzeug (falls zugewiesen)
7. ☐ Tankkarten / Firmenkreditkarten

### Zugriffsrechte
8. ☐ E-Mail-Konto deaktivieren
9. ☐ Systemzugänge sperren
10. ☐ Gebäudezugang entziehen
11. ☐ Fahrzeugberechtigung entfernen

### Dokumentation
12. ☐ Wissenstransfer durchgeführt
13. ☐ Übergabe an Nachfolger
14. ☐ Arbeitszeugnis erstellt
15. ☐ Austrittsgespräch geführt

## Anwendungsfälle

1. **Offboarding starten** - Prozess für ausscheidenden Mitarbeiter initiieren
2. **Checkliste aktualisieren** - Status einzelner Punkte aktualisieren
3. **Wissenstransfer dokumentieren** - Übergabethemen erfassen
4. **Zeugnis anfordern** - Zeugnis-Anforderungen definieren
5. **Protokoll generieren** - Offboarding-Dokumentation erstellen

## Workflow

```
1. Offboarding initiieren
   └── Mitarbeiterdaten, Austrittsdatum, Grund eingeben
   
2. Rückgabe koordinieren
   └── Firmeneigentum zurücknehmen und dokumentieren
   
3. Zugriffsrechte entziehen
   └── Alle Berechtigungen deaktivieren
   
4. Wissenstransfer durchführen
   └── Übergabe an Nachfolger dokumentieren
   
5. Zeugnis erstellen
   └── Arbeitszeugnis vorbereiten
   
6. Protokoll generieren
   └── Offboarding-Dokumentation erstellen
```

## Eingabeparameter

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `mitarbeiter` | object | ✓ | Mitarbeiterdaten (name, personalnummer, abteilung) |
| `austrittsdatum` | string | ✓ | Letzter Arbeitstag (YYYY-MM-DD) |
| `austrittsgrund` | string | ✓ | Grund für das Ausscheiden |
| `rueckgabe` | object | - | Rückgabe-Checkliste |
| `zugriffsrechte` | object | - | Zu entziehende Zugriffsrechte |
| `wissenstransfer` | object | - | Wissenstransfer-Dokumentation |
| `zeugnis` | object | - | Zeugnis-Anforderungen |
| `notizen` | string | - | Zusätzliche Notizen |

### Austrittsgründe

| Grund | Beschreibung |
|-------|--------------|
| `kuendigung_mitarbeiter` | Kündigung durch den Mitarbeiter |
| `kuendigung_arbeitgeber` | Kündigung durch den Arbeitgeber |
| `aufhebung` | Aufhebungsvertrag |
| `befristung` | Auslaufen eines befristeten Vertrags |
| `rente` | Eintritt in den Ruhestand |

## Ausgabe

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `offboarding_id` | string | Eindeutige Offboarding-ID (Format: FF-OFF-YYYYMMDD-XXX) |
| `status` | string | Aktueller Status (gestartet, in_bearbeitung, abgeschlossen) |
| `checkliste` | object | Offboarding-Checkliste mit Status |
| `offene_punkte` | array | Liste der noch offenen Punkte |
| `pdf_path` | string | Pfad zum generierten Offboarding-Protokoll |

## Beispiel

```python
# Offboarding starten
result = execute({
    "mitarbeiter": {
        "name": "Max Mustermann",
        "personalnummer": "FF-2023-042",
        "abteilung": "Fassadenreinigung",
        "position": "Fassadenreiniger",
        "eintrittsdatum": "2023-03-15"
    },
    "austrittsdatum": "2026-02-28",
    "austrittsgrund": "kuendigung_mitarbeiter",
    "rueckgabe": {
        "schluessel": True,
        "laptop": False,
        "handy": True,
        "arbeitskleidung": True,
        "werkzeug": True,
        "fahrzeug": False
    },
    "wissenstransfer": {
        "nachfolger": "Hans Schmidt",
        "uebergabe_themen": [
            "Kundenkontakte Region Nord",
            "Spezialreinigungsverfahren",
            "Gerätewartung"
        ]
    },
    "zeugnis": {
        "typ": "qualifiziert",
        "bewertung": "gut",
        "schwerpunkte": ["Teamarbeit", "Kundenorientierung", "Fachkompetenz"]
    }
})
```

## Integration

Dieser Skill integriert sich mit:
- `ff-hr-einstellung` - Mitarbeiterstammdaten
- `ff-hr-onboarding` - Onboarding-Historie
- `ff-fuhrpark` - Fahrzeugzuweisung
- `ff-zeitnachweis` - Letzte Arbeitszeiterfassung

## FassadenFix Branding

Alle generierten PDFs verwenden automatisch das FassadenFix Corporate Design:
- **Primärfarbe:** #77bc1f (Grün)
- **Sekundärfarbe:** #4e5758 (Grau)
- **Logo:** Automatisch eingefügt
