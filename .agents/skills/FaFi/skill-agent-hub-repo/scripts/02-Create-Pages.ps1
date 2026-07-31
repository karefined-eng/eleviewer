<#
.SYNOPSIS
    Erstellt die Seitenstruktur für das FassadenFix Intranet
.DESCRIPTION
    Dieses Skript erstellt alle definierten Seiten als leere Platzhalter.
.NOTES
    Voraussetzung: Hub-Site muss bereits existieren
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
Write-Host "FassadenFix Intranet - Seitenstruktur" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Mit Site verbinden
Write-Host "`n[1/5] Verbinde mit Site..." -ForegroundColor Yellow
Connect-PnPOnline -Url $siteUrl -Interactive

# Funktion zum Erstellen einer Seite
function New-IntranetPage {
    param(
        [string]$Name,
        [string]$Title,
        [string]$Layout = "Article"
    )

    $pageName = "$Name.aspx"
    $existingPage = Get-PnPPage -Identity $pageName -ErrorAction SilentlyContinue

    if ($existingPage) {
        Write-Host "  - Seite existiert bereits: $Title" -ForegroundColor Yellow
        return
    }

    Add-PnPPage -Name $Name -Title $Title -LayoutType $Layout -HeaderLayoutType NoImage
    Write-Host "  + Seite erstellt: $Title" -ForegroundColor Green
}

# Unternehmensseiten erstellen
Write-Host "`n[2/5] Erstelle Unternehmensseiten..." -ForegroundColor Yellow
foreach ($page in $config.pages.unternehmen) {
    New-IntranetPage -Name $page.name -Title $page.title -Layout $page.layout
}

# Abteilungsseiten erstellen
Write-Host "`n[3/5] Erstelle Abteilungsseiten..." -ForegroundColor Yellow
foreach ($page in $config.pages.abteilungen) {
    New-IntranetPage -Name $page.name -Title $page.title -Layout $page.layout
}

# Teams-Seiten erstellen
Write-Host "`n[4/5] Erstelle Teams-Seiten..." -ForegroundColor Yellow
foreach ($page in $config.pages.teams) {
    New-IntranetPage -Name $page.name -Title $page.title -Layout $page.layout
}

# Persönliche Seiten erstellen
Write-Host "`n[5/5] Erstelle persönliche Seiten..." -ForegroundColor Yellow
foreach ($page in $config.pages.personal) {
    New-IntranetPage -Name $page.name -Title $page.title -Layout $page.layout
}

# Alle Seiten veröffentlichen
Write-Host "`nVeröffentliche alle Seiten..." -ForegroundColor Yellow
$allPages = Get-PnPListItem -List "SitePages" | Where-Object { $_["FileLeafRef"] -ne "Home.aspx" }
foreach ($page in $allPages) {
    $pageName = $page["FileLeafRef"]
    try {
        Set-PnPPage -Identity $pageName -Publish
        Write-Host "  + Veröffentlicht: $pageName" -ForegroundColor Green
    } catch {
        Write-Host "  - Fehler bei: $pageName" -ForegroundColor Red
    }
}

# Zusammenfassung
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Seitenstruktur erstellt!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

$totalPages = $config.pages.unternehmen.Count + $config.pages.abteilungen.Count + $config.pages.teams.Count + $config.pages.personal.Count
Write-Host "Gesamt erstellte Seiten: $totalPages"
Write-Host "========================================`n" -ForegroundColor Cyan

Disconnect-PnPOnline
