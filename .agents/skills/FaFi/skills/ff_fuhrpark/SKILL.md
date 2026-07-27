---
name: ff-fuhrpark
description: "Verwaltet den FassadenFix Fuhrpark und die Fahrzeugzuordnung. Verwenden für: Fahrzeugdaten, Wartungstermine, Tankbelege, Fahrzeugbuchungen, Flottenübersicht."
version: 1.0.0
author: FassadenFix
category: Interne Prozesse
---

# FassadenFix Fuhrpark-Skill

## Übersicht

Der `ff-fuhrpark` Skill verwaltet den gesamten FassadenFix Fuhrpark. Er ermöglicht die Erfassung von Fahrzeugdaten, Wartungsterminen, Tankbelegen und koordiniert Fahrzeugbuchungen für Baustellen.

## Hauptfunktionen

| Funktion | Beschreibung |
|----------|--------------|
| **Fahrzeugverwaltung** | Erfassung und Pflege aller Fahrzeugdaten |
| **Buchungssystem** | Reservierung von Fahrzeugen für Baustellen |
| **Wartungsplanung** | Tracking von Wartungsterminen und -historie |
| **Tankbelegerfassung** | Dokumentation von Tankbelegen und Kraftstoffkosten |
| **Flottenübersicht** | Gesamtübersicht über alle Fahrzeuge und deren Status |

## Anwendungsfälle

1. **Neues Fahrzeug anlegen** - Erfassung aller Fahrzeugdaten
2. **Fahrzeug buchen** - Reservierung für eine Baustelle
3. **Wartung eintragen** - Dokumentation von Wartungsarbeiten
4. **Tankbeleg erfassen** - Kraftstoffkosten dokumentieren
5. **Status abfragen** - Verfügbarkeit und Zustand prüfen

## Workflow

```
1. Fahrzeug anlegen
   └── Kennzeichen, Typ, Marke, Modell eingeben
   
2. Fahrzeug buchen
   └── Baustelle, Fahrer, Zeitraum auswählen
   
3. Wartung planen
   └── Wartungsintervalle und Termine verwalten
   
4. Tankbelege erfassen
   └── Kraftstoffkosten dokumentieren
   
5. Berichte generieren
   └── Flottenübersicht, Kostenanalyse
```

## Eingabeparameter

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `aktion` | string | ✓ | Auszuführende Aktion |
| `fahrzeug_id` | string | - | Fahrzeug-ID (für bestehende Fahrzeuge) |
| `fahrzeug_daten` | object | - | Fahrzeugdaten (kennzeichen, typ, marke, modell) |
| `buchung` | object | - | Buchungsdaten (baustelle_id, fahrer, datum_von/bis) |
| `wartung` | object | - | Wartungsdaten (typ, datum, km_stand, kosten) |
| `tankbeleg` | object | - | Tankbelegdaten (datum, liter, kosten, km_stand) |

### Verfügbare Aktionen

| Aktion | Beschreibung |
|--------|--------------|
| `fahrzeug_anlegen` | Neues Fahrzeug im System anlegen |
| `fahrzeug_buchen` | Fahrzeug für Baustelle reservieren |
| `wartung_eintragen` | Wartungsarbeiten dokumentieren |
| `tankbeleg_erfassen` | Tankbeleg hinzufügen |
| `status_abfragen` | Fahrzeugstatus und Verfügbarkeit prüfen |

## Ausgabe

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `fahrzeug_id` | string | Eindeutige Fahrzeug-ID (Format: FF-FZG-XXX) |
| `status` | string | Aktueller Status (verfuegbar, gebucht, wartung, defekt) |
| `buchungen` | array | Liste der aktiven Buchungen |
| `naechste_wartung` | object | Nächster Wartungstermin |
| `pdf_path` | string | Pfad zum generierten Fahrzeugbericht |

## Fahrzeugtypen

| Typ | Beschreibung |
|-----|--------------|
| `transporter` | Transporter für Material und Geräte |
| `pkw` | PKW für Mitarbeiter und Bauleitung |
| `lkw` | LKW für größere Transporte |
| `anhaenger` | Anhänger für zusätzliche Kapazität |
| `spezial` | Spezialfahrzeuge (Hubarbeitsbühne, etc.) |

## Beispiel

```python
# Neues Fahrzeug anlegen
result = execute({
    "aktion": "fahrzeug_anlegen",
    "fahrzeug_daten": {
        "kennzeichen": "B-FF 1234",
        "typ": "transporter",
        "marke": "Mercedes-Benz",
        "modell": "Sprinter 316 CDI",
        "baujahr": 2023,
        "km_stand": 15000
    }
})

# Fahrzeug buchen
result = execute({
    "aktion": "fahrzeug_buchen",
    "fahrzeug_id": "FF-FZG-001",
    "buchung": {
        "baustelle_id": "FF-BAU-20260215-001",
        "fahrer": "Hans Schmidt",
        "datum_von": "2026-02-15",
        "datum_bis": "2026-02-20"
    }
})
```

## Integration

Dieser Skill integriert sich mit:
- `ff-baustelle` - Fahrzeugzuweisung zu Baustellen
- `ff-zeitnachweis` - Fahrtzeiterfassung
- `ff-hr-einstellung` - Führerscheindaten der Mitarbeiter

## FassadenFix Branding

Alle generierten PDFs verwenden automatisch das FassadenFix Corporate Design:
- **Primärfarbe:** #77bc1f (Grün)
- **Sekundärfarbe:** #4e5758 (Grau)
- **Logo:** Automatisch eingefügt
