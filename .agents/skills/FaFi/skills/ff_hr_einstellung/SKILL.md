---
name: ff-hr-einstellung
description: "Verarbeitet und digitalisiert Personalfrageboegen fuer neue Mitarbeiter. Verwenden für: Eingabe von Stammdaten (Name, Adresse, Bankverbindung), Dokumenten-Upload, IBAN-Validierung, PDF-Generierung."
---

# Skill: FassadenFix HR-Einstellung

Dieser Skill digitalisiert den Personalfragebogen und den Einstellungsprozess fuer neue Mitarbeiter. Er erfasst alle notwendigen Daten fuer die Lohnbuchhaltung und Sozialversicherung.

## Workflow

Der Skill fuehrt durch den vollstaendigen Einstellungsprozess.

1.  **Persoenliche Angaben:** Name, Adresse, Geburtsdatum, Staatsangehoerigkeit.
2.  **Bankverbindung:** IBAN und BIC fuer Gehaltsueberweisungen.
3.  **Beschaeftigungsdaten:** Eintrittsdatum, Steuerklasse, Taetigkeit, Arbeitszeit.
4.  **Sozialversicherung:** Krankenkasse, RV-Nummer, Kinderstatus.
5.  **Entlohnung:** Gehalt, Gleitzone, Steuer-ID.
6.  **Dokumente:** Upload von Ausweis, Fuehrerschein, Zertifikaten.
7.  **PDF generieren:** Ausgefuellter Personalfragebogen zur Unterschrift.

## Verwendung

Der Skill wird bei der Einstellung neuer Mitarbeiter verwendet, entweder als eigenstaendiges Formular oder als Teil des `ff-hr-onboarding` Workflows.

## Kernfunktionalitaet

| Funktion | Beschreibung |
| :--- | :--- |
| **Persoenliche Daten** | Vollstaendige Erfassung aller Stammdaten |
| **Bankverbindung** | IBAN-Validierung und Bankdaten |
| **Steuerliche Daten** | Steuerklasse, Kinderfreibetraege, Kirchensteuer |
| **Sozialversicherung** | Krankenkasse, RV-Nummer, Pflegeversicherung |
| **Dokumenten-Upload** | Ausweis, Fuehrerschein, Zertifikate |
| **PDF-Generierung** | Druckfertiger Personalfragebogen |

## Referenzen

Die Original-Vorlagen befinden sich unter:
- `/home/ubuntu/vorlagen_fassadenfix_strukturiert/05_hr_personal/onboarding/FF-HR-ONB-010_Personalfragebogen.pdf`
- `/home/ubuntu/vorlagen_fassadenfix_strukturiert/05_hr_personal/formulare/FF-HR-FOR-080_Personalfragebogen_2022.docx`
