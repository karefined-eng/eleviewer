<#
.SYNOPSIS
    Konfiguriert die Navigation für das FassadenFix Intranet
.DESCRIPTION
    Dieses Skript richtet die Top-Navigation gemäß Vorgaben ein.
.NOTES
    Voraussetzung: Hub-Site und Seiten müssen existieren
#>

param(
    [Parameter(Mandatory = $false)]
    [string]$ConfigPath = "..\config\settings.json"
)

# Konfiguration laden
$config = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json
$tenantUrl = $config.tenant.url
$siteUrl = $tenantUrl + $config.hubSite.url

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FassadenFix Intranet - Navigation Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Mit Site verbinden
Write-Host "`n[1/3] Verbinde mit Site..." -ForegroundColor Yellow
Connect-PnPOnline -Url $siteUrl -Interactive

# Bestehende Navigation löschen
Write-Host "`n[2/3] Entferne bestehende Navigation..." -ForegroundColor Yellow
$existingNodes = Get-PnPNavigationNode -Location TopNavigationBar
foreach ($node in $existingNodes) {
    Remove-PnPNavigationNode -Identity $node.Id -Force
    Write-Host "  - Entfernt: $($node.Title)" -ForegroundColor Yellow
}

# Neue Navigation erstellen
Write-Host "`n[3/3] Erstelle neue Navigation..." -ForegroundColor Yellow

foreach ($navItem in $config.navigation.topNav) {
    $url = $tenantUrl + $navItem.url

    # Hauptnavigationspunkt erstellen
    $parentNode = Add-PnPNavigationNode -Location TopNavigationBar -Title $navItem.title -Url $url
    Write-Host "  + $($navItem.title)" -ForegroundColor Green

    # Unternavigation erstellen falls vorhanden
    if ($navItem.children) {
        foreach ($child in $navItem.children) {
            $childUrl = $tenantUrl + $child.url
            Add-PnPNavigationNode -Location TopNavigationBar -Title $child.title -Url $childUrl -Parent $parentNode.Id
            Write-Host "    + $($child.title)" -ForegroundColor Cyan
        }
    }
}

# Zusammenfassung
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Navigation konfiguriert!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Top-Navigation Einträge:"
foreach ($navItem in $config.navigation.topNav) {
    Write-Host "  - $($navItem.title)"
    if ($navItem.children) {
        foreach ($child in $navItem.children) {
            Write-Host "    - $($child.title)"
        }
    }
}
Write-Host "========================================`n" -ForegroundColor Cyan

Disconnect-PnPOnline
