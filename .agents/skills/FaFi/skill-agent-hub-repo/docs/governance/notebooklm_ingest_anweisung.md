'''
# Anweisung: NotebookLM-Ingest für FassadenFix Intranet

**Version:** 1.0
**Datum:** 2026-01-13
**Autor:** Manus AI

## 1. Zweck und Geltungsbereich

Diese Anweisung definiert den verbindlichen Prozess für die Aufnahme (Ingest) von Inhalten aus dem **FassadenFix SharePoint Intranet** in **Google NotebookLM**. Sie stellt sicher, dass NotebookLM als wissenskonformer Assistent agiert und das SharePoint-Intranet als alleinige **Single Source of Truth** respektiert wird.

Diese Anweisung ist eine direkte Ableitung der **Master Instruction (Stufe 1)** und der **Manus-optimierten Anweisungsvorlage (Version 1.6)**. Sie gilt für alle Personen und Systeme, die den Ingest-Prozess durchführen oder verantworten.

## 2. Grundprinzip: Strikte Ableitung

NotebookLM darf unter keinen Umständen als eigenständige Wissensquelle agieren. Jede Antwort und jede Information, die von NotebookLM generiert wird, muss **direkt und vollständig** auf die Inhalte zurückführbar sein, die aus dem SharePoint-Intranet ingestiert wurden.

> **Verbotene Aktionen (gemäß Stufe 2 Anweisung):**
> *   Wissen halluzinieren
> *   Branchenwissen ergänzen
> *   „Best Practices“ einführen, die nicht im Intranet definiert sind
> *   Inhalte verallgemeinern oder uminterpretieren
> *   Implizite Annahmen treffen

## 3. Ingest-Quelle

Die einzige zulässige Quelle für den Ingest in NotebookLM ist ein Export der finalen, veröffentlichten Inhalte aus dem FassadenFix SharePoint Intranet.

*   **Quelle:** FassadenFix SharePoint Intranet (`https://fassadenfix.sharepoint.com/sites/FaFi-Intranet`)
*   **Format:** Export als einzelne, strukturierte Markdown-Dateien oder PDFs pro Wissensartikel/Seite.
*   **Zustand:** Nur freigegebene und aktuell gültige Versionen dürfen ingestiert werden. Entwürfe oder veraltete Dokumente sind ausgeschlossen.

## 4. Ingest-Prozess (Manuell)

Bis zur Etablierung eines automatisierten Prozesses ist der folgende manuelle Ingest-Prozess verbindlich.

### 4.1. Schritt 1: Export aus SharePoint

1.  Navigieren Sie zu der SharePoint-Seite, die als Wissensquelle dienen soll.
2.  Nutzen Sie die "Export zu PDF" oder eine äquivalente Funktion, um eine saubere, lesbare Kopie der Seite zu erstellen. Achten Sie darauf, dass alle relevanten Inhalte (Text, Tabellen, Bilder mit Alternativtext) erfasst werden.
3.  Speichern Sie die exportierten Dateien in einem dedizierten, versionierten Ordner (z.B. `notebooklm-ingest/2026-01-13/`).

### 4.2. Schritt 2: Neues NotebookLM-Projekt erstellen

1.  Öffnen Sie [Google NotebookLM](https://notebooklm.google.com/).
2.  Erstellen Sie ein neues Notebook mit dem Namen **"FassadenFix Wissensbasis"**.

### 4.3. Schritt 3: Quellen hinzufügen

1.  Wählen Sie im Notebook die Option "Quelle hinzufügen".
2.  Laden Sie **alle** exportierten Dateien aus dem unter 4.1 erstellten Ordner hoch.
3.  Stellen Sie sicher, dass alle Quellen erfolgreich und ohne Fehler verarbeitet wurden.

### 4.4. Schritt 4: Konfiguration und Test

1.  Fügen Sie die **"Manus-optimierte Anweisungsvorlage (Version 1.6)"** als explizite Anweisung in das NotebookLM-Prompting-Interface ein, um das Verhalten des Modells zu steuern.
2.  Führen Sie Test-Abfragen durch, um die korrekte Funktionsweise sicherzustellen. Beispiele:
    *   Frage: "Was sind unsere Unternehmenswerte?" (Erwartet: Direkte Wiedergabe der Werte von der SharePoint-Seite)
    *   Frage: "Wie melde ich mich krank?" (Erwartet: Wiedergabe des Prozesses gemäß der Arbeitsanweisung im Intranet)
    *   Frage: "Was ist die beste Methode für Fassadenreinigung?" (Erwartet: "Diese Information ist im aktuellen FassadenFix Intranet nicht definiert.", falls nicht explizit beschrieben)

## 5. Aktualisierung der Wissensbasis

Die Wissensbasis in NotebookLM muss regelmäßig aktualisiert werden, um die Konsistenz mit dem SharePoint-Intranet zu gewährleisten.

*   **Aktualisierungsintervall:** Mindestens wöchentlich sowie bei jeder wesentlichen Änderung an Kernprozessen oder Arbeitsanweisungen.
*   **Prozess:** Bei jeder Aktualisierung muss das **gesamte NotebookLM-Projekt archiviert** und ein **neues Projekt** mit dem vollständigen, aktuellen Export aus SharePoint erstellt werden. Ein inkrementelles Hinzufügen oder Entfernen einzelner Quellen ist **verboten**, da dies zu inkonsistenten Zuständen führen kann.

## 6. Fehler- und Unsicherheitsregel

Wenn eine Information in den ingestierten Quellen nicht vorhanden ist, muss die Antwort von NotebookLM strikt der Vorgabe aus der Stufe-2-Anweisung folgen:

> "Diese Information ist im aktuellen FassadenFix Intranet nicht definiert."

Es dürfen keine Vorschläge, Alternativen oder externen Informationen angeboten werden. Das Ziel ist nicht, um jeden Preis hilfreich zu sein, sondern **korrekt, konsistent und regelkonform** zu agieren.
'''
