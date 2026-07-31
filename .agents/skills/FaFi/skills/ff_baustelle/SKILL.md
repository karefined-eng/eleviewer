---
name: ff-baustelle
description: "Verwaltet Baustelleninformationen und -logistik für FassadenFix-Projekte. Verwenden für: Standortdaten, Zugangsinformationen, Sicherheitsanforderungen, Ressourcenkoordination, Baustellendokumentation."
version: 1.0.0
author: FassadenFix
category: Projektdurchführung
---

# FassadenFix Baustellen-Skill

## Übersicht

Der `ff-baustelle` Skill verwaltet alle relevanten Informationen zu FassadenFix-Baustellen. Er ermöglicht die strukturierte Erfassung von Standortdaten, Zugangsinformationen, Sicherheitsanforderungen und die Koordination von Ressourcen.

## Hauptfunktionen

| Funktion | Beschreibung |
|----------|--------------|
| **Standortverwaltung** | Erfassung und Verwaltung von Baustellenadressen und Kontaktdaten |
| **Zugangsdokumentation** | Schlüssel, Codes, Ansprechpartner für den Baustellenzugang |
| **Sicherheitsmanagement** | PSA-Anforderungen, Gerüstdokumentation, Absperrungen |
| **Ressourcenplanung** | Zuweisung von Fahrzeugen, Geräten und Material |
| **PDF-Generierung** | Automatische Erstellung von Baustellendatenblättern |

## Anwendungsfälle

1. **Neue Baustelle anlegen** - Erfassung aller relevanten Projektdaten
2. **Baustellenstatus aktualisieren** - Fortschritt und Änderungen dokumentieren
3. **Ressourcen zuweisen** - Fahrzeuge und Geräte für die Baustelle reservieren
4. **Sicherheitsdokumentation** - PSA-Checklisten und Gefährdungsbeurteilungen
5. **Baustellenübergabe** - Dokumentation für Abnahme und Übergabe

## Workflow

```
1. Baustelle anlegen
   └── Projektname, Adresse, Bauherr eingeben
   
2. Zugangsdaten erfassen
   └── Schlüssel, Codes, Ansprechpartner
   
3. Sicherheit konfigurieren
   └── PSA, Gerüst, Absperrungen
   
4. Ressourcen zuweisen
   └── Fahrzeuge, Geräte, Material
   
5. PDF generieren
   └── Baustellendatenblatt erstellen
```

## Eingabeparameter

| Parameter | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `projekt_name` | string | ✓ | Name des Projekts/der Baustelle |
| `adresse` | object | ✓ | Adressdaten (strasse, plz, ort) |
| `bauherr` | object | ✓ | Kontaktdaten des Bauherrn |
| `bauleiter` | string | ✓ | Name des zuständigen Bauleiters |
| `startdatum` | string | ✓ | Geplantes Startdatum (YYYY-MM-DD) |
| `enddatum` | string | - | Geplantes Enddatum |
| `zugang` | object | - | Zugangsinformationen |
| `sicherheit` | object | - | Sicherheitsanforderungen |
| `ressourcen` | array | - | Benötigte Ressourcen |
| `notizen` | string | - | Zusätzliche Notizen |

## Ausgabe

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `baustellen_id` | string | Eindeutige Baustellen-ID (Format: FF-BAU-YYYYMMDD-XXX) |
| `status` | string | Aktueller Status (geplant, aktiv, pausiert, abgeschlossen) |
| `pdf_path` | string | Pfad zum generierten Baustellendatenblatt |
| `baustellen_daten` | object | Vollständige Baustellendaten |

## Beispiel

```python
# Neue Baustelle anlegen
result = execute({
    "projekt_name": "Fassadensanierung Musterstraße 123",
    "adresse": {
        "strasse": "Musterstraße 123",
        "plz": "12345",
        "ort": "Musterstadt"
    },
    "bauherr": {
        "name": "Max Mustermann",
        "telefon": "+49 123 456789",
        "email": "max@example.com"
    },
    "bauleiter": "Hans Schmidt",
    "startdatum": "2026-02-15",
    "enddatum": "2026-03-15",
    "sicherheit": {
        "geruest": True,
        "absperrung": True,
        "psa": ["Helm", "Sicherheitsschuhe", "Warnweste"]
    }
})
```

## Integration

Dieser Skill integriert sich mit:
- `ff-fuhrpark` - Fahrzeugzuweisung
- `ff-zeitnachweis` - Arbeitszeiterfassung auf der Baustelle
- `ff-dokumentation` - Projektdokumentation
- `ff-inspektion` - Inspektionsprotokolle

## FassadenFix Branding

Alle generierten PDFs verwenden automatisch das FassadenFix Corporate Design:
- **Primärfarbe:** #77bc1f (Grün)
- **Sekundärfarbe:** #4e5758 (Grau)
- **Logo:** Automatisch eingefügt
