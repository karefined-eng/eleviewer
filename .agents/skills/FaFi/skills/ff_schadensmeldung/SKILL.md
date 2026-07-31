---
name: ff-schadensmeldung
description: "Verarbeitet und dokumentiert Schadensmeldungen digital. Verwenden für: Eingabe von Schadensdaten (Objektadresse, Schadensart), Foto-Upload zur Dokumentation, automatische Benachrichtigung des Projektleiters."
---

# Skill: FassadenFix Schadensmeldung

Dieser Skill ermoeglicht eine schnelle und strukturierte digitale Schadensmeldung fuer Kunden und Mitarbeiter. Die Meldung wird automatisch an den zustaendigen Projektleiter weitergeleitet.

## Workflow

Der Skill fuehrt den Benutzer durch einen einfachen Meldeprozess.

1.  **Objektdaten eingeben:** Projektnummer oder Adresse des betroffenen Objekts.
2.  **Schaden beschreiben:** Art und Umfang des Schadens.
3.  **Fotos hochladen:** Visuelle Dokumentation des Schadens.
4.  **Kontaktdaten angeben:** Name und Erreichbarkeit des Meldenden.
5.  **Meldung absenden:** Automatische Benachrichtigung und Protokollierung.

## Verwendung

Der Skill kann als eigenstaendiges Web-Formular, als Teil einer Kunden-App oder durch den `ff-projekt-manager` Agent verwendet werden.

## Kernfunktionalitaet

| Funktion | Beschreibung |
| :--- | :--- |
| **Schadenserfassung** | Strukturierte Eingabe von Schadensart und -beschreibung |
| **Foto-Upload** | Mehrere Fotos zur Dokumentation |
| **Standort** | Automatische oder manuelle Standorterfassung |
| **Benachrichtigung** | Automatische E-Mail an Projektleiter |
| **Protokoll** | PDF-Zusammenfassung der Meldung |

## Schadensarten

Der Skill unterstuetzt folgende vordefinierte Schadensarten:
- Algen-/Pilzbefall (Neubefall)
- Putzschaeden
- Farbschaeden
- Risse
- Abplatzungen
- Sonstige Schaeden

## Referenzen

Die Original-Vorlagen befinden sich unter:
- `/home/ubuntu/vorlagen_fassadenfix_strukturiert/03_garantie_qualität/`
