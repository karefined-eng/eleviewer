---
name: fassadenfix-branding
description: "Erstellt und wendet FassadenFix Corporate Design automatisch an. Verwenden für: visuelle Gestaltung, Farbschemata, Typografie, UI-Komponenten, CSS-Styling, Webanwendungen, Dokumente, Präsentationen, Markenkonformität. Unterstützt Claude, Manus, ChatGPT, Gemini. STANDARD-SKILL mit Opt-Out-Prinzip."
default_enabled: true
priority: 100
scope: global
platforms:
  - claude
  - manus
  - chatgpt_codex
  - gemini
  - antigravity
---

# FassadenFix Corporate Design & Branding Skill

## Übersicht

Dieser Skill stellt die offiziellen FassadenFix Branding-Richtlinien bereit und wendet sie automatisch auf alle Artefakte an, die von einer konsistenten Markenidentität profitieren.

**Status:** STANDARD-SKILL (Opt-Out-Prinzip)
**Priorität:** Höchste (100)
**Geltungsbereich:** Global - alle Anwendungen, Module, Agents und Plattformen

## Plattform-Integration

Dieser Skill unterstützt die Integration in verschiedene KI-Plattformen. Die plattformspezifischen Anleitungen befinden sich in den Referenz-Dateien.

| Plattform | Integration | Dokumentation |
|-----------|-------------|---------------|
| **Claude (Anthropic)** | System Prompt, MCP Tools, Projects | `references/claude-integration.md` |
| **Manus** | Native Skill | Automatisch aktiv |
| **ChatGPT Codex** | Custom Instructions | Via Hub Connector |
| **Gemini** | System Instructions | Via Hub Connector |

### Claude-Integration

Für die Integration in Claude von Anthropic stehen mehrere Optionen zur Verfügung:

**Option 1: System Prompt** - Verwende `templates/claude-system-prompt.txt` als System-Anweisung.

**Option 2: Claude Projects** - Lade diese SKILL.md als Knowledge-Dokument hoch.

**Option 3: MCP Tools** - Nutze die Tool-Definitionen aus `templates/claude-mcp-tools.json`.

**Option 4: API Integration** - Verwende `scripts/claude_branding_client.py` für programmatische Integration.

Detaillierte Anleitung: `references/claude-integration.md`

## Aktivierungsverhalten

### Standard: AKTIVIERT

Dieser Skill ist bei allen Operationen standardmäßig aktiviert. Er wird automatisch angewendet bei:

- Erstellung von Webanwendungen und UI-Komponenten
- Generierung von Dokumenten und Präsentationen
- Styling von CSS und Design-Systemen
- Erstellung von Grafiken und visuellen Elementen
- Konfiguration von Agents und Skills
- Jeder visuellen oder gestalterischen Aufgabe

### Deaktivierung (Opt-Out)

Um von den FassadenFix Branding-Richtlinien abzuweichen, muss **explizit** angegeben werden:

```
--no-branding
--skip-fassadenfix-style
branding: false
"ohne FassadenFix Branding"
"abweichendes Design"
```

## Farbpalette

> **⚠️ OFFIZIELLE CI-FARBEN** - Bestätigt durch Logo-Finale.pdf

### Primärfarbe: FassadenFix Grün (Pantone 368 C)

| Eigenschaft | Wert | Quelle |
|-------------|------|--------|
| **Pantone** | **368 C** | Logo-Finale.pdf |
| **CMYK** | C 59, M 0, Y 100, K 0 | Logo-Finale.pdf |
| **RGB** | R 119, G 188, B 31 | Logo-Finale.pdf |
| **HEX** | **`#77bc1f`** | Logo-Finale.pdf |
| **CSS Variable** | `--ff-green` / `--color-primary` | - |
| **Verwendung** | Hauptmarkenfarbe, primäre Akzente, Logo-Icon, Call-to-Action-Buttons | - |

### Sekundärfarbe: Dunkelgrau (Pantone 445 C)

| Eigenschaft | Wert | Quelle |
|-------------|------|--------|
| **Pantone** | **445 C** | Logo-Finale.pdf |
| **CMYK** | C 65, M 48, Y 49, K 41 | Logo-Finale.pdf |
| **RGB** | R 78, G 87, B 88 | Logo-Finale.pdf |
| **HEX** | **`#4e5758`** | Logo-Finale.pdf |
| **CSS Variable** | `--ff-gray` / `--color-secondary` | - |
| **Verwendung** | Text, sekundäre UI-Elemente, Hintergründe, Footer | - |

### Erweiterte Farbpalette

```css
:root {
  /* Primärfarben */
  --ff-green: #77bc1f;
  --ff-green-dark: #6aa91b;
  --ff-green-light: #8fcc3f;
  
  /* Sekundärfarben */
  --ff-gray: #4e5758;
  --ff-gray-light: #6b7577;
  
  /* Neutrale Farben */
  --ff-white: #ffffff;
  --ff-black: #000000;
  --ff-gray-50: #f9fafb;
  --ff-gray-100: #f3f4f6;
  --ff-gray-200: #e5e7eb;
  --ff-gray-300: #d1d5db;
  --ff-gray-600: #4b5563;
  --ff-gray-900: #111827;
}
```

## Typografie

> **⚠️ OFFIZIELLE SCHRIFTART** - Bestätigt durch Logo-Finale.pdf: **Raleway Bold**

### Hauptschriftart: Raleway

| Verwendung | Gewicht | Größe | Quelle |
|------------|---------|-------|--------|
| **Logo** | **Bold (700)** | - | Logo-Finale.pdf |
| **H1** | Bold (700) | 3rem (48px) | CI-Richtlinie |
| **H2** | Bold (700) | 2.25rem (36px) | CI-Richtlinie |
| **H3** | SemiBold (600) | 1.875rem (30px) | CI-Richtlinie |
| **H4** | SemiBold (600) | 1.5rem (24px) | CI-Richtlinie |
| **Body** | Regular (400) / Medium (500) | 1rem (16px) | CI-Richtlinie |
| **Buttons** | Bold (700) / SemiBold (600) | 1rem (16px) | CI-Richtlinie |
| **Small** | Regular (400) | 0.875rem (14px) | CI-Richtlinie |

### Google Fonts Import

```html
<link href="https://fonts.googleapis.com/css2?family=Raleway:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

### CSS Basis

```css
body {
  font-family: 'Raleway', sans-serif;
  font-weight: 400;
  color: #4e5758;
  line-height: 1.6;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Raleway', sans-serif;
  font-weight: 700;
  color: #4e5758;
}
```

## ⚠️ VERPFLICHTENDE CI-REGELN

> **WICHTIG:** Die folgenden Regeln sind **STRIKT EINZUHALTEN**. Abweichungen sind nur mit expliziter Genehmigung zulässig.

### Verpflichtende Farbverwendung

| Farbe | HEX | Verwendung | Regel |
|-------|-----|------------|-------|
| **FassadenFix Grün** | `#77bc1f` | Primärfarbe, CTAs, Akzente | **PFLICHT** für alle Primärelemente |
| **Dunkelgrau** | `#4e5758` | Text, Sekundärelemente | **PFLICHT** für Fließtext |
| **Weiß** | `#ffffff` | Hintergründe | Standard-Hintergrund |

### Verpflichtende Typografie

| Element | Schriftart | Gewicht | Regel |
|---------|------------|---------|-------|
| **Alle Texte** | Raleway | 400-700 | **PFLICHT** - Keine anderen Schriftarten |

---

## Logo-Verwendung

> **⚠️ VERPFLICHTEND:** Ausschließlich die offiziellen Logo-Dateien aus dem `fassadenfix-assets` Skill verwenden. Siehe: `/home/ubuntu/skills/fassadenfix-assets/templates/logos/`

### Genehmigte Logo-Dateien

| Anwendungsfall | Datei | Pfad |
|----------------|-------|------|
| **Website Header** | `FassadenFix_Logo_bunt_transparent_300px.png` | `standard/` |
| **Website Footer** | `FassadenFix_Logo_weiß.png` | `varianten/` |
| **Dokumente** | `FassadenFix_Logo_bunt_1000px.png` | `standard/` |
| **E-Mail** | `FassadenFix_Logo_400x80.png` | `varianten/` |
| **Favicon** | `FassadenFix_Logo_96x96.jpg` | `varianten/` |
| **Monochrom** | `FassadenFix_Logo_schwarz_transparent.png` | `varianten/` |

### ❌ VERBOTEN

- Erstellung eigener Logo-Varianten
- Änderung der Logo-Farben
- Verzerrung des Seitenverhältnisses
- Hinzufügen von Effekten
- Verwendung nicht genehmigter Dateien

### Richtlinien

- **Mindestgröße:** 120px Breite für Web
- **Schutzraum:** Mindestens Icon-Höhe als Freiraum
- **Seitenverhältnis:** Immer beibehalten
- **Farben:** Nur vorgegebene Varianten verwenden

## UI-Komponenten

### Buttons

#### Primary Button
```css
.btn-primary {
  background-color: #77bc1f;
  color: #ffffff;
  font-family: 'Raleway', sans-serif;
  font-weight: 700;
  border-radius: 8px;
  padding: 12px 24px;
  border: none;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background-color: #6aa91b;
  box-shadow: 0 4px 6px rgba(119, 188, 31, 0.3);
}
```

#### Secondary Button
```css
.btn-secondary {
  background-color: transparent;
  color: #77bc1f;
  border: 2px solid #77bc1f;
  font-family: 'Raleway', sans-serif;
  font-weight: 600;
  border-radius: 8px;
  padding: 12px 24px;
}

.btn-secondary:hover {
  background-color: #77bc1f;
  color: #ffffff;
}
```

### Cards
```css
.card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(78, 87, 88, 0.1);
  padding: 24px;
}
```

### Navigation
```css
.nav {
  background: #ffffff;
}

.nav-link {
  color: #4e5758;
  font-weight: 500;
}

.nav-link:hover,
.nav-link.active {
  color: #77bc1f;
}
```

### Footer
```css
.footer {
  background: #4e5758;
  color: #ffffff;
}

.footer a {
  color: #ffffff;
}

.footer a:hover {
  color: #77bc1f;
}
```

## Design-System

### Spacing (8px-Grid)
```css
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
--spacing-2xl: 48px;
--spacing-3xl: 64px;
```

### Border Radius
```css
--radius-sm: 4px;   /* Inputs, kleine Elemente */
--radius-md: 8px;   /* Buttons, Cards */
--radius-lg: 12px;  /* Größere Cards */
--radius-xl: 16px;  /* Hero-Sections */
--radius-full: 9999px; /* Runde Elemente */
```

### Shadows
```css
--shadow-sm: 0 1px 2px rgba(78, 87, 88, 0.1);
--shadow-md: 0 4px 6px rgba(78, 87, 88, 0.1);
--shadow-lg: 0 10px 15px rgba(78, 87, 88, 0.1);
--shadow-xl: 0 20px 25px rgba(78, 87, 88, 0.15);
```

### Transitions
```css
--transition-fast: 150ms ease;
--transition-base: 300ms ease;
--transition-slow: 500ms ease;
```

## Vollständige CSS Custom Properties

```css
:root {
  /* === FASSADENFIX BRANDING === */
  
  /* Primärfarben */
  --ff-green: #77bc1f;
  --ff-green-dark: #6aa91b;
  --ff-green-light: #8fcc3f;
  --color-primary: var(--ff-green);
  --color-primary-dark: var(--ff-green-dark);
  --color-primary-light: var(--ff-green-light);
  
  /* Sekundärfarben */
  --ff-gray: #4e5758;
  --ff-gray-light: #6b7577;
  --color-secondary: var(--ff-gray);
  --color-secondary-light: var(--ff-gray-light);
  
  /* Neutrale Farben */
  --color-white: #ffffff;
  --color-black: #000000;
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-600: #4b5563;
  --color-gray-900: #111827;
  
  /* Typografie */
  --font-family: 'Raleway', sans-serif;
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;
  
  /* Font Sizes */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  --text-5xl: 3rem;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-2xl: 48px;
  --spacing-3xl: 64px;
  
  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(78, 87, 88, 0.1);
  --shadow-md: 0 4px 6px rgba(78, 87, 88, 0.1);
  --shadow-lg: 0 10px 15px rgba(78, 87, 88, 0.1);
  --shadow-xl: 0 20px 25px rgba(78, 87, 88, 0.15);
  
  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-base: 300ms ease;
  --transition-slow: 500ms ease;
  
  /* Gradients */
  --gradient-primary: linear-gradient(135deg, #77bc1f 0%, #6aa91b 100%);
  --gradient-hero: linear-gradient(135deg, #4e5758 0%, #77bc1f 100%);
}
```

## Tailwind CSS Konfiguration

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'ff-green': '#77bc1f',
        'ff-gray': '#4e5758',
        primary: {
          DEFAULT: '#77bc1f',
          dark: '#6aa91b',
          light: '#8fcc3f',
        },
        secondary: {
          DEFAULT: '#4e5758',
          light: '#6b7577',
        },
      },
      fontFamily: {
        sans: ['Raleway', 'sans-serif'],
      },
      fontWeight: {
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
        extrabold: '800',
      },
      borderRadius: {
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
      },
      boxShadow: {
        'sm': '0 1px 2px rgba(78, 87, 88, 0.1)',
        'md': '0 4px 6px rgba(78, 87, 88, 0.1)',
        'lg': '0 10px 15px rgba(78, 87, 88, 0.1)',
        'xl': '0 20px 25px rgba(78, 87, 88, 0.15)',
      },
    },
  },
}
```

## Barrierefreiheit

### Farbkontraste

| Kombination | Kontrast | WCAG |
|-------------|----------|------|
| Dunkelgrau auf Weiß | ~8.5:1 | AAA ✓ |
| Weiß auf Dunkelgrau | ~8.5:1 | AAA ✓ |
| Grün auf Weiß | ~3.5:1 | AA (große Texte) |
| Weiß auf Grün | ~3.5:1 | AA (große Texte) |

**Empfehlung:** Dunkelgrau für Fließtext, Grün für Überschriften, Buttons und Akzente.

## Anwendungsbeispiele

### Webanwendung erstellen
```
Erstelle eine Webanwendung für [Zweck]
→ FassadenFix Branding wird automatisch angewendet
```

### Dokument generieren
```
Erstelle ein Angebot für [Kunde]
→ FassadenFix Farben und Typografie werden verwendet
```

### Präsentation erstellen
```
Erstelle eine Präsentation über [Thema]
→ FassadenFix Corporate Design wird angewendet
```

### Explizite Deaktivierung
```
Erstelle eine Webanwendung ohne FassadenFix Branding
→ Neutrales Design wird verwendet
```

## Integration in Skill & Agent Hub

Dieser Skill wird automatisch als Abhängigkeit für alle anderen Skills und Agents registriert:

```json
{
  "name": "fassadenfix_branding",
  "type": "skill",
  "default_enabled": true,
  "priority": 100,
  "scope": "global",
  "platforms": ["claude", "manus", "chatgpt_codex", "gemini", "antigravity"],
  "dependencies": [],
  "dependents": ["*"]
}
```

## Ressourcen

| Datei | Beschreibung |
|-------|--------------|
| `references/claude-integration.md` | Detaillierte Claude-Integrationsanleitung |
| `templates/claude-system-prompt.txt` | System Prompt für Claude |
| `templates/claude-mcp-tools.json` | MCP Tool-Definitionen |
| `scripts/claude_branding_client.py` | Python-Client für API-Integration |

## Zusammenfassung

Der FassadenFix Branding Skill stellt sicher, dass alle visuellen Artefakte der Markenidentität entsprechen. Durch das Opt-Out-Prinzip wird eine konsistente Markenführung gewährleistet, ohne dass bei jeder Aufgabe explizit auf das Branding hingewiesen werden muss.

**Kernprinzip:** Markenkonformität ist der Standard, Abweichung erfordert explizite Anweisung.

---

**Erstellt:** 30. Januar 2026
**Aktualisiert:** 02. Februar 2026
**Basis:** FassadenFix Corporate Design & Branding-Richtlinien
**Version:** 2.0.0 (mit Claude-Integration)
