# Anweisung: SharePoint-Setup für FassadenFix Intranet

**Version:** 1.0
**Datum:** 2026-01-13
**Autor:** Manus AI

## 1. Zweck und Geltungsbereich

Diese Anweisung leitet technische Administratoren und KI-Systeme an, das FassadenFix Intranet auf Microsoft SharePoint Online normgerecht und konsistent zu implementieren. Sie basiert auf der übergeordneten **Master Instruction (Stufe 1)** und den Prinzipien der **Manus-optimierten Anweisungsvorlage (Version 1.6)**.

Der Geltungsbereich umfasst die erstmalige Einrichtung sowie die spätere Erweiterung der SharePoint-Umgebung. Ziel ist die Schaffung einer **strukturierten, expliziten und versionierten Wissens- und Arbeitsplattform** für Menschen und Maschinen, die als alleinige "Single Source of Truth" für Organisations- und Prozesswissen dient.

## 2. Vorbereitung

Stellen Sie sicher, dass die folgenden Voraussetzungen erfüllt sind, bevor Sie mit der Einrichtung beginnen.

### 2.1. Technische Voraussetzungen

| Komponente | Anforderung |
| :--- | :--- |
| **Microsoft 365** | Business-Lizenz mit SharePoint Online |
| **Benutzerrechte** | SharePoint Administrator-Rechte im Tenant |
| **PowerShell** | Version 5.1 oder höher |
| **PnP.PowerShell** | Das Modul muss für den ausführenden Benutzer installiert sein |

### 2.2. PnP.PowerShell Modul installieren

Führen Sie den folgenden Befehl in einer PowerShell-Konsole aus, um das erforderliche Modul zu installieren:

```powershell
Install-Module -Name PnP.PowerShell -Scope CurrentUser -Force
```

## 3. Konfiguration

Die zentrale Konfiguration des Intranets erfolgt über die Datei `config/settings.json`. Passen Sie diese Datei vor der ersten Ausführung der Skripte an.

### 3.1. Konfigurationsparameter

| Parameter | Beschreibung |
| :--- | :--- |
| `tenantUrl` | Die primäre URL Ihres SharePoint-Tenants (z.B. `https://yourcompany.sharepoint.com`). |
| `adminEmail` | Die E-Mail-Adresse des Administrators, der die Skripte ausführt. |
| `siteUrl` | Die gewünschte relative URL für die Intranet-Hub-Site (z.B. `/sites/FassadenFixIntranet`). |

### 3.2. Beispiel `settings.json`

```json
{
  "tenant": {
    "url": "https://fassadenfix.sharepoint.com",
    "adminEmail": "admin@fassadenfix.com"
  },
  "hubSite": {
    "name": "FassadenFix Intranet",
    "url": "/sites/FaFi-Intranet",
    "description": "Zentrales Wissens- und Arbeitssystem der FassadenFix GmbH",
    "language": 1031
  },
  "pages": {
    "unternehmen": [
      { "name": "unternehmen-ueberblick", "title": "Unternehmen - Überblick", "layout": "Article" },
      { "name": "organisation-werte", "title": "Organisation & Werte", "layout": "Article" },
      { "name": "arbeitsschutz", "title": "Arbeitsschutz & Pflichtunterweisungen", "layout": "Article" }
    ],
    "abteilungen": [
      { "name": "anwendungstechnik", "title": "Anwendungstechnik", "layout": "Article" },
      { "name": "verwaltung", "title": "Verwaltung", "layout": "Article" },
      { "name": "vertrieb", "title": "Vertrieb", "layout": "Article" },
      { "name": "operative-teams", "title": "Operative Teams", "layout": "Article" }
    ],
    "teams": [
      { "name": "teams-uebersicht", "title": "Teams", "layout": "Article" }
    ],
    "personal": [
      { "name": "mein-bereich", "title": "Mein Bereich", "layout": "Home" }
    ]
  }
}
```

## 4. Automatisierte Einrichtung

Die Einrichtung erfolgt durch die Ausführung von PowerShell-Skripten aus dem `scripts`-Verzeichnis des geklonten Repositories.

### 4.1. Master-Skript ausführen

Das Skript `Deploy-Intranet.ps1` dient als Master-Skript und führt alle notwendigen Einzelschritte in der korrekten Reihenfolge aus.

1.  Öffnen Sie eine PowerShell-Konsole.
2.  Navigieren Sie in das `scripts`-Verzeichnis: `cd /home/ubuntu/FaFi/scripts`
3.  Starten Sie das Deployment:

    ```powershell
    .\Deploy-Intranet.ps1
    ```

Das Skript wird Sie zur interaktiven Anmeldung an Ihrem Microsoft 365-Tenant auffordern.

### 4.2. Detaillierte Ausführungslogik

Das Master-Skript führt die folgenden Schritte sequenziell aus:

| Skript | Reihenfolge | Zweck |
| :--- | :--- | :--- |
| `01-Create-HubSite.ps1` | 1 | Erstellt die zentrale Communication Site und registriert sie als Hub-Site. |
| `02-Create-Pages.ps1` | 2 | Legt die in `settings.json` definierte Seitenstruktur an. |
| `03-Setup-Navigation.ps1` | 3 | Konfiguriert die globale Top-Navigation der Hub-Site. |
| `04-Setup-Permissions.ps1` | 4 | Richtet das definierte Berechtigungskonzept ein. |
| `05-Create-TeamTemplate.ps1` | 5 | Erstellt eine Vorlage für neue Team-Bereiche. |
| `06-Setup-MeinBereich.ps1` | 6 | Konfiguriert die personalisierte "Mein Bereich"-Seite. |

## 5. Ergebnis: Intranet-Struktur

Nach erfolgreicher Ausführung der Skripte ist die folgende logische Struktur im SharePoint implementiert. Diese Struktur folgt strikt den Prinzipien der **Prozess-, Rollen- und Zwecklogik**.

```
FassadenFix Intranet (Hub-Site)
├── Start
├── Unternehmen
│   ├── Unternehmen - Überblick
│   ├── Organisation & Werte
│   └── Arbeitsschutz & Pflichtunterweisungen
├── Abteilungen
│   ├── Anwendungstechnik
│   ├── Verwaltung
│   ├── Vertrieb
│   └── Operative Teams
├── Teams (erweiterbar nach 2-Pizza-Prinzip)
└── Mein Bereich
    ├── Urlaub beantragen
    ├── Krankmeldung
    ├── Meine Aufgaben
    ├── Meine Dokumente
    └── Mein Kalender
```

## 6. Berechtigungskonzept

Das eingerichtete Berechtigungskonzept stellt sicher, dass der Zugriff auf Inhalte rollenbasiert und nach dem Need-to-know-Prinzip erfolgt.

| Bereich | Gruppe | Berechtigung |
| :--- | :--- | :--- |
| **Hub-Site** | Alle Mitarbeiter | Lesen |
| **Abteilungen** | Zugehörige Abteilungsgruppe | Lesen/Bearbeiten |
| **Teams** | Zugehörige Team-Gruppe | Vollzugriff |
| **Administration** | Websitebesitzer | Vollzugriff |

## 7. Nächste Schritte

Nach der erfolgreichen technischen Einrichtung ist das Intranet bereit für die inhaltliche Befüllung. Dieser Prozess muss sich strikt an die **Inhaltsprinzipien** der Master Instruction halten (Verbindlichkeit, Explizitheit, Rollen- und Prozessbezug).
