<#
.SYNOPSIS
    Master-Deployment-Skript für FassadenFix Intranet
.DESCRIPTION
    Führt alle Setup-Skripte in der richtigen Reihenfolge aus.
.NOTES
    Ausführung: .\Deploy-Intranet.ps1
#>

param(
    [Parameter(Mandatory = $false)]
    [switch]$SkipHubSite,

    [Parameter(Mandatory = $false)]
    [switch]$SkipPages,

    [Parameter(Mandatory = $false)]
    [switch]$SkipNavigation,

    [Parameter(Mandatory = $false)]
    [switch]$SkipPermissions,

    [Parameter(Mandatory = $false)]
    [switch]$SkipMeinBereich
)

$ErrorActionPreference = "Stop"
$scriptPath = $PSScriptRoot

Write-Host @"

===============================================
  FassadenFix Intranet - Vollständiges Setup
===============================================

  Dieses Skript führt folgende Schritte aus:
  1. Hub-Site erstellen und registrieren
  2. Seitenstruktur anlegen
  3. Navigation konfigurieren
  4. Berechtigungen einrichten
  5. 'Mein Bereich' Seite einrichten

===============================================

"@ -ForegroundColor Cyan

# Voraussetzungen prüfen
Write-Host "Prüfe Voraussetzungen..." -ForegroundColor Yellow

# PnP PowerShell prüfen
$pnpModule = Get-Module -Name PnP.PowerShell -ListAvailable
if (-not $pnpModule) {
    Write-Host "FEHLER: PnP.PowerShell Modul nicht installiert!" -ForegroundColor Red
    Write-Host "Installieren Sie es mit: Install-Module -Name PnP.PowerShell -Scope CurrentUser" -ForegroundColor Yellow
    exit 1
}
Write-Host "  + PnP.PowerShell gefunden: v$($pnpModule.Version)" -ForegroundColor Green

# Konfiguration prüfen
$configPath = Join-Path $scriptPath "..\config\settings.json"
if (-not (Test-Path $configPath)) {
    Write-Host "FEHLER: Konfigurationsdatei nicht gefunden: $configPath" -ForegroundColor Red
    exit 1
}
Write-Host "  + Konfiguration gefunden" -ForegroundColor Green

# Konfiguration laden und anzeigen
$config = Get-Content -Path $configPath -Raw | ConvertFrom-Json
Write-Host "`nKonfiguration:" -ForegroundColor Yellow
Write-Host "  Tenant URL: $($config.tenant.url)"
Write-Host "  Site URL: $($config.hubSite.url)"
Write-Host "  Site Name: $($config.hubSite.name)"

# Bestätigung
Write-Host "`n" -NoNewline
$confirm = Read-Host "Möchten Sie mit dem Setup fortfahren? (j/n)"
if ($confirm -ne "j" -and $confirm -ne "J") {
    Write-Host "Setup abgebrochen." -ForegroundColor Yellow
    exit 0
}

# Skripte ausführen
$startTime = Get-Date

# 1. Hub-Site erstellen
if (-not $SkipHubSite) {
    Write-Host "`n`n" -NoNewline
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host "SCHRITT 1: Hub-Site erstellen" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    & "$scriptPath\01-Create-HubSite.ps1"
} else {
    Write-Host "`nSCHRITT 1: Hub-Site wird übersprungen (-SkipHubSite)" -ForegroundColor Yellow
}

# 2. Seiten erstellen
if (-not $SkipPages) {
    Write-Host "`n`n" -NoNewline
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host "SCHRITT 2: Seitenstruktur anlegen" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    & "$scriptPath\02-Create-Pages.ps1"
} else {
    Write-Host "`nSCHRITT 2: Seiten werden übersprungen (-SkipPages)" -ForegroundColor Yellow
}

# 3. Navigation konfigurieren
if (-not $SkipNavigation) {
    Write-Host "`n`n" -NoNewline
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host "SCHRITT 3: Navigation konfigurieren" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    & "$scriptPath\03-Setup-Navigation.ps1"
} else {
    Write-Host "`nSCHRITT 3: Navigation wird übersprungen (-SkipNavigation)" -ForegroundColor Yellow
}

# 4. Berechtigungen einrichten
if (-not $SkipPermissions) {
    Write-Host "`n`n" -NoNewline
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host "SCHRITT 4: Berechtigungen einrichten" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    & "$scriptPath\04-Setup-Permissions.ps1"
} else {
    Write-Host "`nSCHRITT 4: Berechtigungen werden übersprungen (-SkipPermissions)" -ForegroundColor Yellow
}

# 5. Mein Bereich einrichten
if (-not $SkipMeinBereich) {
    Write-Host "`n`n" -NoNewline
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host "SCHRITT 5: 'Mein Bereich' einrichten" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    & "$scriptPath\06-Setup-MeinBereich.ps1"
} else {
    Write-Host "`nSCHRITT 5: 'Mein Bereich' wird übersprungen (-SkipMeinBereich)" -ForegroundColor Yellow
}

# Zusammenfassung
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host @"

===============================================
  SETUP ABGESCHLOSSEN
===============================================

  Dauer: $($duration.ToString("mm\:ss")) Minuten

  Erstellte Ressourcen:
  - Hub-Site: $($config.hubSite.name)
  - Unternehmensseiten: $($config.pages.unternehmen.Count)
  - Abteilungsseiten: $($config.pages.abteilungen.Count)
  - Sonstige Seiten: $($config.pages.teams.Count + $config.pages.personal.Count)

  Nächste Schritte:
  1. Tenant-URL in config/settings.json anpassen
  2. Benutzer zu Gruppen hinzufügen
  3. Team-Bereiche nach Bedarf erstellen:
     .\05-Create-TeamTemplate.ps1 -TeamName "Teamname"
  4. Power Automate Flows einrichten

  Site-URL: $($config.tenant.url)$($config.hubSite.url)

===============================================

"@ -ForegroundColor Green
