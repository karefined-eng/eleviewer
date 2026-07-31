---
name: ff-objekterfassung
description: "Verarbeitet und digitalisiert Objektdaten fuer Fassadenprojekte. Verwenden für: Eingabe von Projektdaten (Anschrift, Immobilienart, Putzart), Zustandsdokumentation mit Fotos, automatische Flaechenberechnung, PDF-Generierung."
---

# Skill: FassadenFix Objekterfassung

Dieser Skill digitalisiert den Prozess der Objekterfassung fuer Fassadenprojekte und ersetzt die manuelle Dateneingabe ueber PDF-Formulare.

## Workflow

Der Skill fuehrt den Anwender durch einen schrittweisen Prozess, um alle relevanten Objektdaten digital zu erfassen. Das Ergebnis ist ein strukturiertes Datenobjekt und ein automatisch generiertes PDF-Dokument.

1.  **Projektdaten abfragen:** Der Skill fragt nach grundlegenden Projektdaten wie Anschrift, Art der Immobilie und Putzart.
2.  **Schaeden dokumentieren:** Erfassung von vorhandenen Schaeden und Besonderheiten.
3.  **Massen ermitteln:** Eingabe der gemessenen Werte zur Flaechenberechnung.
4.  **Fotos hinzufuegen:** Moeglichkeit zum Upload von Fotos zur visuellen Dokumentation.
5.  **Checkliste abarbeiten:** Abarbeiten einer kurzen Checkliste (z.B. 360-Grad-Rundgang).
6.  **PDF generieren:** Aus den erfassten Daten wird ein PDF-Dokument generiert, das dem urspruenglichen Formular entspricht.

## Verwendung

Dieser Skill kann auf verschiedene Weisen genutzt werden:

-   **Als interaktive Web-Anwendung:** Ein einfacher Web-Client, der die Schritte des Workflows als Formular abbildet.
-   **Als CLI-Tool:** Ein Kommandozeilen-Skript, das den Benutzer durch die einzelnen Abfragen fuehrt.
-   **Als Teil eines Agents:** Der `ff-projekt-manager`-Agent kann diesen Skill aufrufen, um die Objekterfassung als ersten Schritt in einem neuen Projekt zu starten.

## Kernfunktionalitaet

| Funktion | Beschreibung |
| :--- | :--- |
| **Formular-basierte Dateneingabe** | Strukturierte Erfassung aller relevanten Felder |
| **Foto-Upload** | Integration fuer die visuelle Dokumentation |
| **Automatische Flaechenberechnung** | Berechnung der Gesamtflaeche aus gemessenen Werten |
| **PDF-Generierung** | Erstellung eines standardisierten PDF-Protokolls |

## Referenzen

Die Original-Vorlage befindet sich unter:
- `/home/ubuntu/vorlagen_fassadenfix_strukturiert/01_projekt_dokumentation/objektaufnahme/FF-OBJ-001_Objektdatenblatt.pdf`
