<#
.SYNOPSIS
    Erstellt Team-Vorlagen für das 2-Pizza-Prinzip
.DESCRIPTION
    Dieses Skript erstellt eine wiederverwendbare Vorlage für Team-Bereiche
    mit eigener Dokumentenbibliothek und Aufgabenübersicht.
.NOTES
    Voraussetzung: Hub-Site muss existieren
#>

param(
    [Parameter(Mandatory = $false)]
    [string]$ConfigPath = "..\config\settings.json",

    [Parameter(Mandatory = $false)]
    [string]$TeamName = ""
)

# Konfiguration laden
$config = Get-Content -Path $ConfigPath -Raw | ConvertFrom-Json
$tenantUrl = $config.tenant.url
$siteUrl = $tenantUrl + $config.hubSite.url

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FassadenFix Intranet - Team-Vorlage" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Funktion zum Erstellen eines neuen Team-Bereichs
function New-TeamArea {
    param(
        [Parameter(Mandatory = $true)]
        [string]$TeamName
    )

    # Sicheren Namen erstellen
    $safeName = $TeamName -replace '[^a-zA-Z0-9]', '-'
    $safeName = $safeName -replace '-+', '-'
    $safeName = $safeName.Trim('-')

    Write-Host "`nErstelle Team-Bereich: $TeamName" -ForegroundColor Yellow

    # Team-Seite erstellen
    $pageName = "Team-$safeName"
    $existingPage = Get-PnPPage -Identity "$pageName.aspx" -ErrorAction SilentlyContinue

    if ($existingPage) {
        Write-Host "  - Seite existiert bereits: $pageName" -ForegroundColor Yellow
    } else {
        Add-PnPPage -Name $pageName -Title "Team: $TeamName" -LayoutType Article -HeaderLayoutType NoImage
        Write-Host "  + Seite erstellt: Team: $TeamName" -ForegroundColor Green
    }

    # Dokumentenbibliothek erstellen
    $docLibName = "Dokumente-$safeName"
    $existingLib = Get-PnPList -Identity $docLibName -ErrorAction SilentlyContinue

    if ($existingLib) {
        Write-Host "  - Bibliothek existiert bereits: $docLibName" -ForegroundColor Yellow
    } else {
        New-PnPList -Title $docLibName -Template DocumentLibrary -Url "Dokumente-$safeName"
        Write-Host "  + Dokumentenbibliothek erstellt: $docLibName" -ForegroundColor Green
    }

    # Aufgabenliste erstellen (für spätere Power Automate Integration)
    $taskListName = "Aufgaben-$safeName"
    $existingTaskList = Get-PnPList -Identity $taskListName -ErrorAction SilentlyContinue

    if ($existingTaskList) {
        Write-Host "  - Aufgabenliste existiert bereits: $taskListName" -ForegroundColor Yellow
    } else {
        New-PnPList -Title $taskListName -Template Tasks -Url "Aufgaben-$safeName"
        Write-Host "  + Aufgabenliste erstellt: $taskListName" -ForegroundColor Green
    }

    # Team-Gruppe erstellen
    $teamGroupName = "FassadenFix Team - $TeamName"
    $existingGroup = Get-PnPGroup -Identity $teamGroupName -ErrorAction SilentlyContinue

    if (-not $existingGroup) {
        New-PnPGroup -Title $teamGroupName -Description "Mitglieder des Teams $TeamName"
        Write-Host "  + Gruppe erstellt: $teamGroupName" -ForegroundColor Green
    } else {
        Write-Host "  - Gruppe existiert: $teamGroupName" -ForegroundColor Yellow
    }

    # Berechtigungen auf Dokumentenbibliothek setzen
    $docLib = Get-PnPList -Identity $docLibName
    if ($docLib) {
        Set-PnPList -Identity $docLibName -BreakRoleInheritance -CopyRoleAssignments
        Set-PnPListPermission -Identity $docLibName -Group $teamGroupName -AddRole "Bearbeiten"
        Write-Host "  + Berechtigungen gesetzt für: $docLibName" -ForegroundColor Green
    }

    # Berechtigungen auf Aufgabenliste setzen
    $taskList = Get-PnPList -Identity $taskListName
    if ($taskList) {
        Set-PnPList -Identity $taskListName -BreakRoleInheritance -CopyRoleAssignments
        Set-PnPListPermission -Identity $taskListName -Group $teamGroupName -AddRole "Bearbeiten"
        Write-Host "  + Berechtigungen gesetzt für: $taskListName" -ForegroundColor Green
    }

    # Webparts zur Seite hinzufügen
    $page = Get-PnPPage -Identity "$pageName.aspx"
    if ($page) {
        # Dokumentenbibliothek-Webpart
        Add-PnPPageSection -Page $pageName -SectionTemplate TwoColumn -Order 1

        # Text-Webpart mit Willkommenstext
        $welcomeText = @"
<h2>Willkommen im Team-Bereich: $TeamName</h2>
<p>Hier findet ihr alle wichtigen Dokumente und Aufgaben für unser Team.</p>
"@
        Add-PnPPageTextPart -Page $pageName -Section 1 -Column 1 -Text $welcomeText

        # Seite veröffentlichen
        Set-PnPPage -Identity "$pageName.aspx" -Publish
        Write-Host "  + Seite veröffentlicht" -ForegroundColor Green
    }

    Write-Host "`nTeam-Bereich '$TeamName' erfolgreich erstellt!" -ForegroundColor Green

    return @{
        PageUrl = "/SitePages/$pageName.aspx"
        DocumentLibrary = $docLibName
        TaskList = $taskListName
        Group = $teamGroupName
    }
}

# Mit Site verbinden
Write-Host "`nVerbinde mit Site..." -ForegroundColor Yellow
Connect-PnPOnline -Url $siteUrl -Interactive

if ($TeamName -ne "") {
    # Einzelnes Team erstellen
    $result = New-TeamArea -TeamName $TeamName

    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Team-Bereich erstellt!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Seite: $($result.PageUrl)"
    Write-Host "Dokumente: $($result.DocumentLibrary)"
    Write-Host "Aufgaben: $($result.TaskList)"
    Write-Host "Gruppe: $($result.Group)"
    Write-Host "========================================`n" -ForegroundColor Cyan
} else {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Team-Vorlage Verwendung" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Um ein neues Team zu erstellen, führen Sie aus:"
    Write-Host ""
    Write-Host "  .\05-Create-TeamTemplate.ps1 -TeamName 'Teamname'"
    Write-Host ""
    Write-Host "Beispiele:"
    Write-Host "  .\05-Create-TeamTemplate.ps1 -TeamName 'Fassadenbau Nord'"
    Write-Host "  .\05-Create-TeamTemplate.ps1 -TeamName 'Montage Süd'"
    Write-Host "  .\05-Create-TeamTemplate.ps1 -TeamName 'Projektplanung'"
    Write-Host ""
    Write-Host "Jedes Team erhält automatisch:"
    Write-Host "  - Eigene Teamseite"
    Write-Host "  - Eigene Dokumentenbibliothek"
    Write-Host "  - Eigene Aufgabenliste"
    Write-Host "  - Eigene Berechtigungsgruppe"
    Write-Host "========================================`n" -ForegroundColor Cyan
}

Disconnect-PnPOnline
