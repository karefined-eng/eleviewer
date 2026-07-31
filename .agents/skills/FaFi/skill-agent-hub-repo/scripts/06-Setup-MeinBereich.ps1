<#
.SYNOPSIS
    Richtet die "Mein Bereich" Seite mit persönlichen Kacheln ein
.DESCRIPTION
    Dieses Skript konfiguriert die persönliche Mitarbeiter-Startseite mit:
    - Dynamischer Begrüßung
    - Kacheln für Urlaub, Krankmeldung, Aufgaben, Dokumente, Kalender
.NOTES
    Voraussetzung: Hub-Site und Seiten müssen existieren
#>

param(
    [Parameter(Mandatory = $false)]
    [string]$ConfigPath = "..\config\settings.json",

    [Parameter(Mandatory = $false)]
    [string]$TemplatePath = "..\templates\mein-bereich-template.json"
)

# Konfiguration laden
$config = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json
$template = Get-Content -Path $TemplatePath -Raw | ConvertFrom-Json
$tenantUrl = $config.tenant.url
$siteUrl = $tenantUrl + $config.hubSite.url

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FassadenFix Intranet - Mein Bereich" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Mit Site verbinden
Write-Host "`n[1/5] Verbinde mit Site..." -ForegroundColor Yellow
Connect-PnPOnline -Url $siteUrl -Interactive

# Seite prüfen/erstellen
Write-Host "`n[2/5] Prüfe Seite..." -ForegroundColor Yellow
$pageName = $template.page.name
$page = Get-PnPPage -Identity "$pageName.aspx" -ErrorAction SilentlyContinue

if (-not $page) {
    Add-PnPPage -Name $pageName -Title $template.page.title -LayoutType Article -HeaderLayoutType NoImage
    Write-Host "  + Seite erstellt: $($template.page.title)" -ForegroundColor Green
} else {
    Write-Host "  - Seite existiert bereits: $($template.page.title)" -ForegroundColor Yellow
}

# Seite konfigurieren
Write-Host "`n[3/5] Konfiguriere Seiteninhalt..." -ForegroundColor Yellow

$page = Get-PnPPage -Identity "$pageName.aspx"

# Bestehende Sektionen entfernen (falls vorhanden)
try {
    # Seite leeren und neu aufbauen
    Set-PnPPage -Identity "$pageName.aspx" -LayoutType Article
} catch {
    Write-Host "  Hinweis: Seitenbereinigung übersprungen" -ForegroundColor Yellow
}

# Willkommenstext hinzufügen
$welcomeHtml = @"
<div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
    <h1 style="color: #333; margin-top: 0;">Willkommen im FassadenFix Intranet</h1>
    <p style="font-size: 16px; color: #666;">Dies ist dein persönlicher Bereich. Hier findest du wichtige Links und Funktionen.</p>
</div>
"@

Add-PnPPageTextPart -Page $pageName -Text $welcomeHtml
Write-Host "  + Willkommensbereich hinzugefügt" -ForegroundColor Green

# Kacheln-Bereich hinzufügen
Write-Host "`n[4/5] Füge Kacheln hinzu..." -ForegroundColor Yellow

$tilesHtml = @"
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 30px;">

    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 25px; color: white; text-align: center;">
        <div style="font-size: 36px; margin-bottom: 10px;">📅</div>
        <h3 style="margin: 0 0 10px 0; color: white;">Urlaub beantragen</h3>
        <p style="margin: 0; opacity: 0.9; font-size: 14px;">Urlaubsantrag stellen</p>
    </div>

    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 12px; padding: 25px; color: white; text-align: center;">
        <div style="font-size: 36px; margin-bottom: 10px;">🏥</div>
        <h3 style="margin: 0 0 10px 0; color: white;">Krankmeldung</h3>
        <p style="margin: 0; opacity: 0.9; font-size: 14px;">Krankmeldung einreichen</p>
    </div>

    <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 12px; padding: 25px; color: white; text-align: center;">
        <div style="font-size: 36px; margin-bottom: 10px;">✅</div>
        <h3 style="margin: 0 0 10px 0; color: white;">Meine Aufgaben</h3>
        <p style="margin: 0; opacity: 0.9; font-size: 14px;">Offene Aufgaben anzeigen</p>
    </div>

    <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); border-radius: 12px; padding: 25px; color: white; text-align: center;">
        <div style="font-size: 36px; margin-bottom: 10px;">📁</div>
        <h3 style="margin: 0 0 10px 0; color: white;">Meine Dokumente</h3>
        <p style="margin: 0; opacity: 0.9; font-size: 14px;">OneDrive öffnen</p>
    </div>

    <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); border-radius: 12px; padding: 25px; color: white; text-align: center;">
        <div style="font-size: 36px; margin-bottom: 10px;">📆</div>
        <h3 style="margin: 0 0 10px 0; color: white;">Mein Kalender</h3>
        <p style="margin: 0; opacity: 0.9; font-size: 14px;">Outlook Kalender</p>
    </div>

</div>
"@

Add-PnPPageTextPart -Page $pageName -Text $tilesHtml
Write-Host "  + Kacheln hinzugefügt" -ForegroundColor Green

# Hinweis für dynamische Inhalte
$dynamicNote = @"
<div style="margin-top: 40px; padding: 15px; background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 8px;">
    <strong>Hinweis für Administratoren:</strong>
    <p style="margin: 5px 0 0 0;">Für dynamische Benutzernamen und funktionale Links müssen folgende Schritte durchgeführt werden:</p>
    <ul style="margin: 10px 0 0 0;">
        <li>SPFx Webpart für personalisierte Begrüßung installieren</li>
        <li>Power Automate Flows für Urlaub/Krankmeldung einrichten</li>
        <li>Links mit tatsächlichen Tenant-URLs aktualisieren</li>
    </ul>
</div>
"@

Add-PnPPageTextPart -Page $pageName -Text $dynamicNote
Write-Host "  + Administratorhinweis hinzugefügt" -ForegroundColor Green

# Seite veröffentlichen
Write-Host "`n[5/5] Veröffentliche Seite..." -ForegroundColor Yellow
Set-PnPPage -Identity "$pageName.aspx" -Publish
Write-Host "  + Seite veröffentlicht" -ForegroundColor Green

# Zusammenfassung
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "'Mein Bereich' erfolgreich konfiguriert!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Seite: /SitePages/$pageName.aspx"
Write-Host ""
Write-Host "Enthaltene Kacheln:"
Write-Host "  - Urlaub beantragen"
Write-Host "  - Krankmeldung"
Write-Host "  - Meine Aufgaben"
Write-Host "  - Meine Dokumente"
Write-Host "  - Mein Kalender"
Write-Host ""
Write-Host "Nächste Schritte:"
Write-Host "  1. SPFx Webpart für dynamische Begrüßung installieren"
Write-Host "  2. Power Automate Flows einrichten"
Write-Host "  3. Links mit echten URLs aktualisieren"
Write-Host "========================================`n" -ForegroundColor Cyan

Disconnect-PnPOnline
