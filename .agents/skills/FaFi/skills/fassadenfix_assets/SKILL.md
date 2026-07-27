---
name: fassadenfix-assets
description: "Verwaltet FassadenFix Logo-Varianten, Favicons, Icons und Vorlagen. Verwenden für: Logo-Auswahl, Favicon-Integration, Icon-Bibliothek, Dokumentvorlagen, E-Mail-Signaturen, Asset-Download."
default_enabled: true
priority: 90
scope: global
platforms:
  - claude
  - manus
  - chatgpt_codex
  - gemini
  - antigravity
related_skills:
  - fassadenfix-branding
  - fassadenfix-identity
---

# FassadenFix Assets Skill

## Übersicht

Dieser Skill stellt alle visuellen Assets von FassadenFix bereit und definiert deren korrekte Verwendung. Er dient als zentrale Anlaufstelle für Logos, Favicons, Icons und Vorlagen.

**Status:** STANDARD-SKILL (Opt-Out-Prinzip)
**Priorität:** Hoch (90)
**Geltungsbereich:** Global - alle visuellen Materialien

---

## ❗️ VERPFLICHTENDE REGEL: OFFIZIELLE LOGO-DATEIEN

> **WICHTIG:** Die folgenden Logo-Dateien sind die **EINZIG GENEHMIGTEN** Varianten für alle FassadenFix-Materialien. Die Verwendung anderer Logo-Versionen ist **STRIKT UNTERSAGT**.

### Offizielle CI-Farben (Bestätigt durch Logo-Finale.pdf)

| Farbe | Pantone | HEX | RGB | CMYK |
|-------|---------|-----|-----|------|
| **FassadenFix Grün** | **368 C** | `#77bc1f` | R119 G188 B31 | C59 M0 Y100 K0 |
| **Dunkelgrau** | **445 C** | `#4e5758` | R78 G87 B88 | C65 M48 Y49 K41 |

### Offizielle Typografie

| Element | Schriftart | Gewicht |
|---------|------------|--------|
| **Logo** | Raleway | **Bold (700)** |

### Genehmigte Logo-Dateien

Die offiziellen Logo-Dateien befinden sich unter:
```
/home/ubuntu/skills/fassadenfix-assets/templates/logos/
```

---

## Offizieller Logo-Katalog

### Standard-Logos (Primäre Verwendung)

| Dateiname | Pfad | Verwendung |
|-----------|------|------------|
| **FassadenFix_Logo_bunt_transparent.png** | `templates/logos/standard/` | **PRIMÄR** - Transparenter Hintergrund, alle Standardanwendungen |
| **FassadenFix_Logo_bunt_1000px.png** | `templates/logos/standard/` | Hochauflösend (1000px), Print und große Darstellungen |
| **FassadenFix_Logo_bunt_transparent_300px.png** | `templates/logos/standard/` | Web-optimiert (300px), Header, E-Mails |
| **FassadenFix-Logo.png** | `templates/logos/standard/` | Kompaktes Standard-Logo |

### Logo-Varianten (Spezielle Anwendungen)

| Dateiname | Pfad | Verwendung |
|-----------|------|------------|
| **FassadenFix_Logo_400x80.png** | `templates/logos/varianten/` | Banner, Header (Querformat) |
| **FassadenFix_Logo_schwarz_transparent.png** | `templates/logos/varianten/` | Monochrom, Druck, Stempel |
| **FassadenFix_Logo_weiß.png** | `templates/logos/varianten/` | Dunkle Hintergründe, Footer |
| **FassadenFix_Logo_rechteck.png** | `templates/logos/varianten/` | Rechteckiges Format |
| **FassadenFix_Logo_rechteck.jpg** | `templates/logos/varianten/` | Rechteckig (JPG für E-Mail) |
| **FassadenFix_Logo_96x96.jpg** | `templates/logos/varianten/` | Favicon, kleine Icons |

### Partner-Logos (DESWOS)

| Dateiname | Pfad | Verwendung |
|-----------|------|------------|
| **FassadenFix_Deswos.png** | `templates/logos/partner/` | DESWOS-Partnerschaft Standard |
| **FassadenFix_Deswos2.png** | `templates/logos/partner/` | DESWOS-Variante 2 |
| **FassadenFix_Deswos3.png** | `templates/logos/partner/` | DESWOS-Variante 3 |

### Quelldateien (Nur für Druckerei/Designer)

| Dateiname | Pfad | Verwendung |
|-----------|------|------------|
| **Logo-Finale.ai** | `templates/logos/quelldateien/` | Adobe Illustrator Quelldatei |
| **Logo-Finale.pdf** | `templates/logos/quelldateien/` | Vektorgrafik PDF |
| **Bunt_2021_FF.ai** | `templates/logos/quelldateien/` | Farbversion Quelldatei |

---

## Logo-Auswahl nach Anwendungsfall

### Empfohlene Logos nach Kontext

| Anwendungsfall | Empfohlenes Logo | Begründung |
|----------------|------------------|------------|
| **Website Header** | `FassadenFix_Logo_bunt_transparent_300px.png` | Web-optimiert, transparent |
| **Website Footer (dunkel)** | `FassadenFix_Logo_weiß.png` | Gute Lesbarkeit auf dunkel |
| **E-Mail-Signatur** | `FassadenFix_Logo_400x80.png` | Querformat, kompakt |
| **Dokumente/Angebote** | `FassadenFix_Logo_bunt_1000px.png` | Hochauflösend für Print |
| **Favicon** | `FassadenFix_Logo_96x96.jpg` | Optimale Größe |
| **Social Media** | `FassadenFix_Logo_rechteck.png` | Passt in quadratische Formate |
| **Druck (SW)** | `FassadenFix_Logo_schwarz_transparent.png` | Monochrom für Stempel etc. |
| **Nachhaltigkeit** | `FassadenFix_Deswos.png` | Zeigt DESWOS-Partnerschaft |

---

## Verwendungsregeln

### ✅ ERLAUBT

- Verwendung der offiziellen Logo-Dateien aus diesem Katalog
- Skalierung unter Beibehaltung des Seitenverhältnisses
- Platzierung auf weißem oder hellem Hintergrund (Standard-Logo)
- Platzierung auf dunklem Hintergrund (Weiß-Variante)

### ❌ VERBOTEN

- Erstellung eigener Logo-Varianten
- Änderung der Farben
- Verzerrung des Seitenverhältnisses
- Hinzufügen von Effekten (Schatten, Glanz, etc.)
- Verwendung nicht genehmigter Logo-Dateien
- Kombination mit anderen Logos ohne Genehmigung

---

## Logo-Richtlinien

| Regel | Wert | Begründung |
|-------|------|------------|
| **Mindestbreite Web** | 120px | Lesbarkeit |
| **Mindestbreite Print** | 30mm | Druckqualität |
| **Schutzraum** | 1x Icon-Höhe | Visuelle Klarheit |
| **Seitenverhältnis** | Immer beibehalten | Markenintegrität |
| **Farben** | Nur definierte Varianten | Konsistenz |

---

## Favicon-Varianten

### Größen und Formate

| Format | Größe | Verwendung |
|--------|-------|------------|
| **favicon.ico** | 16x16, 32x32, 48x48 | Browser-Tab (Legacy) |
| **favicon.svg** | Skalierbar | Moderne Browser |
| **apple-touch-icon.png** | 180x180 | iOS Home Screen |
| **android-chrome-192.png** | 192x192 | Android Chrome |
| **android-chrome-512.png** | 512x512 | Android Splash |
| **mstile-150x150.png** | 150x150 | Windows Tiles |

### Favicon SVG-Code

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="6" fill="#77bc1f"/>
  <path d="M8 10h16v2H8zm0 5h12v2H8zm0 5h14v2H8z" fill="white"/>
  <path d="M22 15l4 4-4 4" stroke="white" stroke-width="2" 
        fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

### HTML Integration

```html
<head>
  <!-- Favicon -->
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <meta name="theme-color" content="#77bc1f">
</head>
```

---

## Icon-Bibliothek

### Empfohlene Icon-Sets

| Icon-Set | Verwendung | Integration |
|----------|------------|-------------|
| **Lucide React** | Web-Anwendungen | `npm install lucide-react` |
| **Lucide Icons** | Allgemein | CDN oder Download |
| **Custom Icons** | Markenspezifisch | SVG in assets/ |

### Icon-Styling Richtlinien

```css
/* FassadenFix Icon-Styling */
.ff-icon {
  color: #77bc1f;           /* Primärfarbe */
  stroke-width: 2;          /* Konsistente Strichstärke */
}

.ff-icon-secondary {
  color: #4e5758;           /* Sekundärfarbe */
}

.ff-icon-light {
  color: #ffffff;           /* Für dunkle Hintergründe */
}
```

---

## Dokumentvorlagen

### Verfügbare Vorlagen

| Vorlage | Format | Verwendung |
|---------|--------|------------|
| **Angebot** | DOCX, PDF | Kundenangebote |
| **Rechnung** | DOCX, PDF | Rechnungsstellung |
| **Präsentation** | PPTX | Kundenpräsentationen |
| **Briefkopf** | DOCX | Geschäftskorrespondenz |
| **Visitenkarte** | PDF, AI | Druckvorlage |

---

## E-Mail-Signatur

### HTML-Signatur

```html
<table cellpadding="0" cellspacing="0" style="font-family: 'Raleway', Arial, sans-serif; font-size: 14px; color: #4e5758;">
  <tr>
    <td style="padding-right: 15px; border-right: 2px solid #77bc1f;">
      <img src="https://fassadenfix.de/logo.png" alt="FassadenFix" width="120">
    </td>
    <td style="padding-left: 15px;">
      <strong style="color: #77bc1f; font-size: 16px;">[Name]</strong><br>
      <span style="color: #6b7577;">[Position]</span><br><br>
      <span>FassadenFix GmbH</span><br>
      <span>Tel: [Telefon]</span><br>
      <span>E-Mail: [E-Mail]</span><br>
      <a href="https://www.fassadenfix.de" style="color: #77bc1f;">www.fassadenfix.de</a>
    </td>
  </tr>
  <tr>
    <td colspan="2" style="padding-top: 10px; font-size: 11px; color: #6b7577;">
      <em>"Ihr sicherer Weg zur sauberen Fassade"</em>
    </td>
  </tr>
</table>
```

---

## Anwendungsbeispiele

### Website erstellen
```
Erstelle eine Website für FassadenFix
→ Header: FassadenFix_Logo_bunt_transparent_300px.png
→ Footer: FassadenFix_Logo_weiß.png
→ Favicon: FassadenFix_Logo_96x96.jpg
```

### Dokument erstellen
```
Erstelle ein Angebot
→ Logo: FassadenFix_Logo_bunt_1000px.png
→ E-Mail-Signatur mit FassadenFix_Logo_400x80.png
```

### Nachhaltigkeits-Content
```
Erstelle Content zur DESWOS-Partnerschaft
→ Partner-Logo: FassadenFix_Deswos.png
```

---

## Deaktivierung (Opt-Out)

```
--no-assets
--skip-fassadenfix-assets
assets: false
"ohne FassadenFix Assets"
"eigene Assets verwenden"
```

---

## Verzeichnisstruktur

```
/home/ubuntu/skills/fassadenfix-assets/templates/logos/
├── standard/
│   ├── FassadenFix_Logo_bunt_transparent.png      # PRIMÄR
│   ├── FassadenFix_Logo_bunt_1000px.png           # Hochauflösend
│   ├── FassadenFix_Logo_bunt_transparent_300px.png # Web-optimiert
│   └── FassadenFix-Logo.png                       # Kompakt
├── varianten/
│   ├── FassadenFix_Logo_400x80.png                # Banner
│   ├── FassadenFix_Logo_schwarz_transparent.png   # Monochrom
│   ├── FassadenFix_Logo_weiß.png                  # Für dunkle BG
│   ├── FassadenFix_Logo_rechteck.png              # Rechteck
│   ├── FassadenFix_Logo_rechteck.jpg              # Rechteck JPG
│   └── FassadenFix_Logo_96x96.jpg                 # Favicon
├── partner/
│   ├── FassadenFix_Deswos.png                     # DESWOS Standard
│   ├── FassadenFix_Deswos2.png                    # DESWOS Var. 2
│   └── FassadenFix_Deswos3.png                    # DESWOS Var. 3
└── quelldateien/
    ├── Logo-Finale.ai                             # AI Quelldatei
    ├── Logo-Finale.pdf                            # Vektor PDF
    └── Bunt_2021_FF.ai                            # Farb-Quelldatei
```

---

## Quelle

Alle Assets basieren auf dem **FassadenFix Corporate Design** und dem `fassadenfix-branding` Skill. Die Logo-Dateien wurden offiziell von FassadenFix bereitgestellt und sind die einzig genehmigten Varianten.
