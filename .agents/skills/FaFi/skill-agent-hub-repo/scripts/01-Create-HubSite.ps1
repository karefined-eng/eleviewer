<#
.SYNOPSIS
    Erstellt die FassadenFix Intranet Hub-Site
.DESCRIPTION
    Dieses Skript erstellt eine SharePoint Communication Site und registriert sie als Hub-Site.
.NOTES
    Voraussetzung: PnP.PowerShell Modul
#>

param(
    [Parameter(Mandatory = $false)]
    [string]$ConfigPath = "..\config\settings.json"
)

# Konfiguration laden
$config = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json
$tenantUrl = $config.tenant.url
$adminUrl = $config.tenant.adminUrl
$hubSite = $config.hubSite

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FassadenFix Intranet - Hub-Site Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Mit SharePoint Admin Center verbinden
Write-Host "`n[1/4] Verbinde mit SharePoint Admin Center..." -ForegroundColor Yellow
Connect-PnPOnline -Url $adminUrl -Interactive

# Prüfen ob Site bereits existiert
$siteUrl = $tenantUrl + $hubSite.url
Write-Host "`n[2/4] Prüfe ob Site bereits existiert..." -ForegroundColor Yellow

$existingSite = Get-PnPTenantSite -Url $siteUrl -ErrorAction SilentlyContinue

if ($existingSite) {
    Write-Host "Site existiert bereits: $siteUrl" -ForegroundColor Red
    Write-Host "Überspringe Erstellung..." -ForegroundColor Yellow
} else {
    # Communication Site erstellen
    Write-Host "`n[3/4] Erstelle Communication Site..." -ForegroundColor Yellow

    New-PnPSite -Type CommunicationSite `
        -Title $hubSite.name `
        -Url $siteUrl `
        -Lcid $hubSite.language `
        -Description $hubSite.description `
        -SiteDesign Blank

    Write-Host "Communication Site erstellt: $siteUrl" -ForegroundColor Green

    # Warten bis Site verfügbar ist
    Write-Host "Warte auf Site-Verfügbarkeit..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
}

# Als Hub-Site registrieren
Write-Host "`n[4/4] Registriere als Hub-Site..." -ForegroundColor Yellow

$hubSiteInfo = Get-PnPHubSite -Identity $siteUrl -ErrorAction SilentlyContinue

if ($hubSiteInfo) {
    Write-Host "Site ist bereits als Hub-Site registriert." -ForegroundColor Yellow
} else {
    Register-PnPHubSite -Site $siteUrl
    Write-Host "Hub-Site erfolgreich registriert!" -ForegroundColor Green
}

# Zusammenfassung
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Hub-Site Setup abgeschlossen!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Site URL: $siteUrl"
Write-Host "Site Name: $($hubSite.name)"
Write-Host "Sprache: Deutsch (LCID $($hubSite.language))"
Write-Host "Hub-Status: Registriert"
Write-Host "========================================`n" -ForegroundColor Cyan

# Verbindung trennen
Disconnect-PnPOnline
