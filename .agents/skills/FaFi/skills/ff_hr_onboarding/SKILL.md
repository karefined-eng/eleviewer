---
name: ff-hr-onboarding
description: "Verwaltet und automatisiert den Onboarding-Prozess fuer neue Mitarbeiter. Verwenden für: Checklisten-Workflow (17 Punkte), Dokumenten-Sammlung, Statusverfolgung, automatische Erinnerungen."
---

# Skill: FassadenFix HR-Onboarding

Dieser Skill automatisiert den Onboarding-Prozess fuer neue Mitarbeiter mit einem strukturierten Checklisten-Workflow. Er stellt sicher, dass alle notwendigen Schritte und Dokumente erfasst werden.

## Workflow

Der Skill fuehrt durch den vollstaendigen Onboarding-Prozess.

1.  **Bewerberverfahren:** Pruefung und Einladung zum Gespraech.
2.  **Dokumentensammlung:** Kopien von Ausweis, Fuehrerschein, Zertifikaten.
3.  **Personalfragebogen:** Ausfuellen und Einreichen (via ff-hr-einstellung).
4.  **Probearbeit:** Terminierung und Anmeldung bei der Personalabteilung.
5.  **Arbeitsvertrag:** Erstellung und Unterzeichnung.
6.  **Arbeitsmittel:** Vereinbarung und Uebergabe.
7.  **Sicherheitsunterweisung:** Arbeitsschutz und Hebebuehnen-Beauftragung.
8.  **Abschluss:** Stundenzettel und finale Dokumentation.

## Verwendung

Der Skill orchestriert den gesamten Onboarding-Prozess und ruft bei Bedarf andere Skills wie `ff-hr-einstellung` auf. Er kann als eigenstaendiger Workflow oder durch einen HR-Agent gesteuert werden.

## Kernfunktionalitaet

| Funktion | Beschreibung |
| :--- | :--- |
| **Checkliste** | Strukturierter Workflow mit allen Onboarding-Schritten |
| **Statusverfolgung** | Echtzeit-Uebersicht ueber den Fortschritt |
| **Dokumentensammlung** | Zentrale Erfassung aller erforderlichen Dokumente |
| **Erinnerungen** | Automatische Benachrichtigungen bei offenen Aufgaben |
| **Berichterstellung** | PDF-Zusammenfassung des Onboarding-Status |

## Erforderliche Dokumente

Der Onboarding-Prozess erfordert folgende Dokumente:
- Personalausweis (Kopie)
- Fuehrerschein (Kopie)
- Krankenversicherungskarte (Kopie)
- Ausbildungszertifikate (falls vorhanden)
- Bedienerscheine (falls vorhanden)
- Unterschriebener Personalfragebogen
- Unterschriebener Arbeitsvertrag

## Referenzen

Die Original-Vorlagen befinden sich unter:
- `/home/ubuntu/vorlagen_fassadenfix_strukturiert/05_hr_personal/onboarding/`
