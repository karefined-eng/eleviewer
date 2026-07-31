# FassadenFix Intranet - SharePoint Setup

## Voraussetzungen

- Microsoft 365 Business Lizenz mit SharePoint Online
- SharePoint Administrator-Rechte
- PnP PowerShell Modul installiert

### PnP PowerShell Installation

```powershell
Install-Module -Name PnP.PowerShell -Scope CurrentUser
```

## Übersicht der Struktur

```
FassadenFix Intranet (Hub-Site)
├── Start
├── Unternehmen
│   ├── Unternehmen – Überblick
│   ├── Organisation & Werte
│   └── Arbeitsschutz & Pflichtunterweisungen
├── Abteilungen
│   ├── Anwendungstechnik
│   ├── Verwaltung
│   ├── Vertrieb
│   └── Operative Teams
├── Teams
│   └── [Team-Unterseiten - später erweiterbar]
│       ├── Dokumentenbibliothek
│       └── Aufgabenübersicht
└── Mein Bereich
    ├── Begrüßung (dynamisch)
    ├── Urlaub beantragen
    ├── Krankmeldung
    ├── Meine Aufgaben
    ├── Meine Dokumente
    └── Mein Kalender
```

## Ausführungsreihenfolge

1. `01-Create-HubSite.ps1` - Hub-Site erstellen und registrieren
2. `02-Create-Pages.ps1` - Seitenstruktur anlegen
3. `03-Setup-Navigation.ps1` - Navigation konfigurieren
4. `04-Setup-Permissions.ps1` - Berechtigungen einrichten
5. `05-Create-TeamTemplate.ps1` - Team-Vorlage erstellen

## Konfiguration

Vor der Ausführung die Datei `config/settings.json` anpassen:

- `tenantUrl`: SharePoint Tenant URL
- `adminEmail`: Administrator E-Mail
- `siteUrl`: Gewünschte Site URL

## Berechtigungskonzept

| Bereich | Berechtigung | Gruppe |
|---------|--------------|--------|
| Hub-Site | Lesen | Alle Mitarbeiter |
| Abteilungen | Lesen/Bearbeiten | Abteilungsgruppen |
| Teams | Vollzugriff | Team-Mitglieder |
| Administration | Vollzugriff | Site-Besitzer |

## Design-Richtlinien

- Schlichtes, übersichtliches Design
- Keine Überfrachtung
- Fokus auf Navigation und Klarheit
- Skalierbar für zukünftige Erweiterungen
