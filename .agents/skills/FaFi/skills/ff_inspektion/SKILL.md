---
name: ff-inspektion
description: "Erstellt digitale Inspektionsprotokolle fuer die jaehrliche Fassadenkontrolle. Verwenden für: Zustandsbewertung (Skala 0-4), Schadensdokumentation mit Fotos, Empfehlungen zur Nacharbeit, PDF-Generierung."
---

# Skill: FassadenFix Jaehrliche Inspektion

Dieser Skill digitalisiert die jaehrliche Inspektion von Fassaden zur Kontrolle der "5 Jahre algenfrei"-Garantie.

## Workflow

Der Skill fuehrt einen Pruefer durch den standardisierten Inspektionsprozess und generiert ein digitales Protokoll.

1.  **Projektdaten laden:** Der Skill laedt die urspruenglichen Projektdaten (Auftraggeber, Anschrift, Umsetzungsdatum) anhand der Projektnummer.
2.  **Zustand bewerten:** Der Zustand der Fassade wird auf einer Skala von 0 (neuwertig) bis 4 (starker Neubefall) bewertet.
3.  **Nacharbeiten definieren:** Festlegung, ob und welche Bereiche (Eingangsseite, Rueckseite, Giebel) kostenfreie Nacharbeiten erfordern.
4.  **Schaeden und Gefahren erfassen:** Dokumentation von spezifischen Schaeden (Loecher, Risse, Graffiti) und weiteren Gefahren (Vogelnester, Bewuchs, etc.) mit Fotomoeglichkeit.
5.  **Empfehlungen geben:** Formulierung von Massnahmen, um einen Neubefall weiter hinauszuzoegern.
6.  **Protokoll generieren:** Erstellung eines digitalen Inspektionsprotokolls im PDF-Format, inklusive digitaler Unterschriften von Pruefer und Empfaenger.

## Verwendung

Dieser Skill kann auf verschiedene Weisen genutzt werden:

-   **Als mobile App fuer Pruefer:** Eine Tablet-Anwendung, die den Pruefer vor Ort durch die Inspektion leitet.
-   **Als Teil eines Agents:** Der `ff-projekt-manager`-Agent kann diesen Skill jaehrlich automatisch aufrufen und einen Pruefer mit der Durchfuehrung beauftragen.

## Kernfunktionalitaet

| Funktion | Beschreibung |
| :--- | :--- |
| **Gefuehrter Inspektionsprozess** | Schritt-fuer-Schritt-Anleitung fuer den Pruefer |
| **Bewertungsskala** | Visuelle Skala zur einfachen Zustandserfassung (0-4) |
| **Checklisten fuer Schaeden/Gefahren** | Schnelle Auswahl vordefinierter Punkte |
| **Fotodokumentation** | Direkte Zuordnung von Fotos zu spezifischen Schaeden |
| **Digitale Unterschriften** | Rechtssichere Abnahme des Protokolls |
| **PDF-Generierung** | Automatisierte Erstellung des finalen Inspektionsberichts |

## Referenzen

Die Original-Vorlage befindet sich unter:
- `/home/ubuntu/vorlagen_fassadenfix_strukturiert/01_projekt_dokumentation/inspektion/FF-INS-001_Inspektionsprotokoll.pdf`
