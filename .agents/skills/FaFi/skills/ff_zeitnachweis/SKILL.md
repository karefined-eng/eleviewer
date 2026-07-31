---
name: ff-zeitnachweis
description: "Verarbeitet und berechnet Arbeitszeiten fuer Mitarbeiter digital. Verwenden für: Tageserfassung (Beginn, Ende, Pausen), Projektzuordnung, Ueberstundenberechnung, monatliche PDF-Zusammenfassung."
---

# Skill: FassadenFix Zeitnachweis

Dieser Skill digitalisiert die Arbeitszeiterfassung fuer Mitarbeiter. Er ermoeglicht die taegliche Erfassung von Arbeitszeiten mit Projektzuordnung und generiert monatliche Zusammenfassungen.

## Workflow

Der Skill unterstuetzt die taegliche Zeiterfassung und monatliche Auswertung.

1.  **Tageserfassung:** Arbeitsbeginn, -ende, Pausen und Projektzuordnung.
2.  **Projektzuordnung:** Zuordnung der Arbeitszeit zu Baustellen/Projekten.
3.  **Pausenerfassung:** Dokumentation von Pausen gemaess Arbeitszeitgesetz.
4.  **Ueberstunden:** Automatische Berechnung von Mehr- und Minderarbeit.
5.  **Monatsbericht:** Zusammenfassung aller Eintraege mit Gesamtstunden.
6.  **Unterschrift:** Digitale Bestaetigung durch Mitarbeiter und Vorgesetzten.

## Verwendung

Der Skill kann als eigenstaendige Zeiterfassungs-App, als Teil des Mitarbeiterportals oder durch den `ff-projekt-manager` Agent verwendet werden.

## Kernfunktionalitaet

| Funktion | Beschreibung |
| :--- | :--- |
| **Tageserfassung** | Erfassung von Arbeitsbeginn, -ende und Pausen |
| **Projektzuordnung** | Zuordnung der Arbeitszeit zu Projekten/Baustellen |
| **Pausenberechnung** | Automatische Pruefung der gesetzlichen Pausenregelung |
| **Ueberstunden** | Berechnung von Mehr- und Minderarbeit |
| **Monatsbericht** | PDF-Zusammenfassung mit Gesamtstunden |
| **Unterschriften** | Digitale Bestaetigung durch Mitarbeiter und Vorgesetzten |

## Arbeitszeitregelungen

Der Skill beruecksichtigt folgende gesetzliche Vorgaben:
- Maximale Arbeitszeit: 10 Stunden pro Tag
- Pausenregelung: 30 Min. bei mehr als 6 Std., 45 Min. bei mehr als 9 Std.
- Ruhezeit: Mindestens 11 Stunden zwischen Arbeitstagen

## Referenzen

Die Original-Vorlagen befinden sich unter:
- `/home/ubuntu/vorlagen_fassadenfix_strukturiert/05_hr_personal/formulare/`
