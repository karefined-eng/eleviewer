<#
.SYNOPSIS
    Konfiguriert Berechtigungen für das FassadenFix Intranet
.DESCRIPTION
    Dieses Skript richtet das Berechtigungskonzept ein:
    - Alle Mitarbeiter: Lesen auf Hub-Site
    - Abteilungen & Teams: Vorbereitet für gruppenbasierte Rechte
    - Admin: Globaler Besitzer
.NOTES
    Voraussetzung: Hub-Site muss existieren
#>

param(
    [Parameter(Mandatory = $false)]
    [string]$ConfigPath = "..\config\settings.json"
)

# Konfiguration laden
$config = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json
$tenantUrl = $config.tenant.url
$adminUrl = $config.tenant.adminUrl
$siteUrl = $tenantUrl + $config.hubSite.url
$permissions = $config.permissions

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FassadenFix Intranet - Berechtigungen" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Mit Site verbinden
Write-Host "`n[1/4] Verbinde mit Site..." -ForegroundColor Yellow
Connect-PnPOnline -Url $siteUrl -Interactive

# SharePoint-Gruppen erstellen/prüfen
Write-Host "`n[2/4] Prüfe SharePoint-Gruppen..." -ForegroundColor Yellow

# Besitzer-Gruppe
$ownersGroup = Get-PnPGroup -Identity $permissions.ownersGroup -ErrorAction SilentlyContinue
if (-not $ownersGroup) {
    New-PnPGroup -Title $permissions.ownersGroup -Description "Besitzer des Intranets mit Vollzugriff"
    Write-Host "  + Gruppe erstellt: $($permissions.ownersGroup)" -ForegroundColor Green
} else {
    Write-Host "  - Gruppe existiert: $($permissions.ownersGroup)" -ForegroundColor Yellow
}

# Mitglieder-Gruppe
$membersGroup = Get-PnPGroup -Identity $permissions.membersGroup -ErrorAction SilentlyContinue
if (-not $membersGroup) {
    New-PnPGroup -Title $permissions.membersGroup -Description "Mitglieder mit Bearbeitungsrechten"
    Write-Host "  + Gruppe erstellt: $($permissions.membersGroup)" -ForegroundColor Green
} else {
    Write-Host "  - Gruppe existiert: $($permissions.membersGroup)" -ForegroundColor Yellow
}

# Besucher-Gruppe
$visitorsGroup = Get-PnPGroup -Identity $permissions.visitorsGroup -ErrorAction SilentlyContinue
if (-not $visitorsGroup) {
    New-PnPGroup -Title $permissions.visitorsGroup -Description "Besucher mit Leserechten"
    Write-Host "  + Gruppe erstellt: $($permissions.visitorsGroup)" -ForegroundColor Green
} else {
    Write-Host "  - Gruppe existiert: $($permissions.visitorsGroup)" -ForegroundColor Yellow
}

# Berechtigungen zuweisen
Write-Host "`n[3/4] Weise Berechtigungen zu..." -ForegroundColor Yellow

# Besitzer bekommen Vollzugriff
Set-PnPGroupPermissions -Identity $permissions.ownersGroup -AddRole "Vollzugriff"
Write-Host "  + Vollzugriff für: $($permissions.ownersGroup)" -ForegroundColor Green

# Mitglieder bekommen Bearbeiten
Set-PnPGroupPermissions -Identity $permissions.membersGroup -AddRole "Bearbeiten"
Write-Host "  + Bearbeiten für: $($permissions.membersGroup)" -ForegroundColor Green

# Besucher bekommen Lesen
Set-PnPGroupPermissions -Identity $permissions.visitorsGroup -AddRole "Lesen"
Write-Host "  + Lesen für: $($permissions.visitorsGroup)" -ForegroundColor Green

# Abteilungsgruppen vorbereiten
Write-Host "`n[4/4] Bereite Abteilungsgruppen vor..." -ForegroundColor Yellow

$abteilungen = @(
    @{Name = "FassadenFix Anwendungstechnik"; Desc = "Mitglieder der Abteilung Anwendungstechnik"},
    @{Name = "FassadenFix Verwaltung"; Desc = "Mitglieder der Abteilung Verwaltung"},
    @{Name = "FassadenFix Vertrieb"; Desc = "Mitglieder der Abteilung Vertrieb"},
    @{Name = "FassadenFix Operative Teams"; Desc = "Mitglieder der Operativen Teams"}
)

foreach ($abt in $abteilungen) {
    $existingGroup = Get-PnPGroup -Identity $abt.Name -ErrorAction SilentlyContinue
    if (-not $existingGroup) {
        New-PnPGroup -Title $abt.Name -Description $abt.Desc
        Write-Host "  + Gruppe erstellt: $($abt.Name)" -ForegroundColor Green
    } else {
        Write-Host "  - Gruppe existiert: $($abt.Name)" -ForegroundColor Yellow
    }
}

# Zusammenfassung
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Berechtigungen konfiguriert!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Berechtigungsübersicht:"
Write-Host "  - Besitzer: Vollzugriff"
Write-Host "  - Mitglieder: Bearbeiten"
Write-Host "  - Besucher: Lesen"
Write-Host "  - Abteilungsgruppen: Vorbereitet"
Write-Host ""
Write-Host "Nächste Schritte:"
Write-Host "  1. Benutzer zu Gruppen hinzufügen"
Write-Host "  2. 'Alle Mitarbeiter' aus Azure AD verknüpfen"
Write-Host "  3. Abteilungsberechtigungen auf Seiten setzen"
Write-Host "========================================`n" -ForegroundColor Cyan

Disconnect-PnPOnline
