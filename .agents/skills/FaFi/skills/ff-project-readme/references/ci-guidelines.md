# FassadenFix CI-Richtlinien für README-Dateien

Dieses Dokument fasst die Corporate Identity Richtlinien zusammen, die bei der Erstellung von README-Dateien für FassadenFix-Projekte einzuhalten sind.

## Inhaltsverzeichnis

1. [Farben](#farben)
2. [Typografie](#typografie)
3. [Logo-Verwendung](#logo-verwendung)
4. [Tonalität](#tonalität)
5. [Badges](#badges)
6. [Struktur](#struktur)

---

## Farben

### Primärfarbe: FassadenFix Grün

| Eigenschaft | Wert |
|-------------|------|
| **Pantone** | 368 C |
| **HEX** | `#77bc1f` |
| **RGB** | R119 G188 B31 |
| **CMYK** | C59 M0 Y100 K0 |

**Verwendung in README:**
- Badge-Farben
- Hervorgehobene Links
- Akzent-Elemente

### Sekundärfarbe: Dunkelgrau

| Eigenschaft | Wert |
|-------------|------|
| **Pantone** | 445 C |
| **HEX** | `#4e5758` |
| **RGB** | R78 G87 B88 |
| **CMYK** | C65 M48 Y49 K41 |

**Verwendung in README:**
- Sekundäre Badges
- Textfarbe (bei HTML-Elementen)

---

## Typografie

### Schriftart: Raleway

| Verwendung | Gewicht |
|------------|---------|
| Logo | Bold (700) |
| Überschriften | Bold (700) |
| Fließtext | Regular (400) |

**Hinweis:** In Markdown-README-Dateien wird die Schriftart durch GitHub/GitLab bestimmt. Bei HTML-Elementen innerhalb der README kann Raleway via Google Fonts eingebunden werden.

---

## Logo-Verwendung

### Offizielle Logo-Dateien

| Anwendung | Datei | Pfad |
|-----------|-------|------|
| README Header | `FassadenFix_Logo_bunt_transparent_300px.png` | `standard/` |
| Kleine Darstellung | `FassadenFix_Logo_96x96.jpg` | `varianten/` |

### Logo-Pfad

```
/home/ubuntu/skills/fassadenfix-assets/templates/logos/
```

### Einbindung in README

```markdown
<div align="center">
  <img src="[LOGO-PFAD]" alt="FassadenFix Logo" width="300">
</div>
```

### Verboten

- Eigene Logo-Varianten erstellen
- Logo-Farben ändern
- Seitenverhältnis verzerren
- Effekte hinzufügen (Schatten, Glanz)

---

## Tonalität

### Grundprinzipien

| Prinzip | Beschreibung |
|---------|--------------|
| **Persönlich & nahbar** | Direkte Ansprache, menschliche Verbindung |
| **Selbstbewusst & werteorientiert** | Stärke gekoppelt an Werte |
| **Partnerschaftlich** | Beziehung statt Transaktion |
| **Ehrlich & transparent** | Offene Kommunikation |

### Sprachliche Dos and Don'ts

| ✅ DO | ❌ DON'T |
|-------|----------|
| "Ihr sicherer Weg zur sauberen Fassade" | "Wir reinigen Fassaden" |
| "Partnerschaft auf Augenhöhe" | "Wir sind der Dienstleister" |
| "Garantierte Ergebnisse" | "Wir versuchen unser Bestes" |
| "Transparente Preise" | "Günstige Angebote" |

### Empfohlene Formulierungen

**Einleitung:**
> "Wie bei allen FassadenFix-Lösungen steht Qualität und Transparenz im Vordergrund."

**Footer:**
> "Erstellt mit 💚 von FassadenFix"

**Claim:**
> "Ihr sicherer Weg zur sauberen Fassade"

---

## Badges

### FassadenFix Standard-Badges

```markdown
<!-- Projekt-Badge -->
[![FassadenFix](https://img.shields.io/badge/FassadenFix-Projekt-77bc1f?style=flat-square)](https://fassadenfix.de)

<!-- Status-Badges -->
[![Status](https://img.shields.io/badge/Status-Aktiv-77bc1f?style=flat-square)]()
[![Status](https://img.shields.io/badge/Status-In_Entwicklung-4e5758?style=flat-square)]()

<!-- Versions-Badge -->
[![Version](https://img.shields.io/badge/Version-1.0.0-77bc1f?style=flat-square)]()

<!-- CI-Badge -->
[![CI](https://img.shields.io/badge/CI-konform-77bc1f?style=flat-square)]()
```

### Badge-Farben

| Status | Farbe |
|--------|-------|
| Aktiv/Positiv | `77bc1f` (Grün) |
| Neutral/In Entwicklung | `4e5758` (Grau) |

---

## Struktur

### Pflichtabschnitte

1. **Header** - Logo, Titel, Kurzbeschreibung, Badges
2. **Übersicht** - Ausführliche Beschreibung
3. **Funktionen** - Feature-Liste (Tabelle)
4. **Installation** - Schrittweise Anleitung
5. **Verwendung** - Code-Beispiele
6. **Kontakt** - FassadenFix Kontaktdaten
7. **Footer** - Branding-Element

### Optionale Abschnitte

- Konfiguration
- API-Dokumentation
- Beitrag (Contributing)
- Lizenz
- Changelog
- Screenshots

### Formatierung

| Element | Empfehlung |
|---------|------------|
| Überschriften | H1 nur einmal (Titel), dann H2/H3 |
| Listen | Tabellen bevorzugen |
| Code | Mit Syntax-Highlighting |
| Links | Inline-Links mit aussagekräftigem Text |

---

## Quelle

Diese Richtlinien basieren auf den FassadenFix Skills:
- `fassadenfix-branding`
- `fassadenfix-identity`
- `fassadenfix-assets`
- `fassadenfix-copywriting`
