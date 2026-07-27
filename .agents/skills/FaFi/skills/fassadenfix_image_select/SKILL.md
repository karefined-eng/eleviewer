---
name: fassadenfix-image-select
description: "Analysiert und bewertet Bilder nach FassadenFix Markenrichtlinien und wählt passende Motive aus. Verwenden für: Bildstil-Vorgaben, Qualitätskriterien, Farbharmonie, Hero-Bilder, Teamfotos, Baustellenbilder."
default_enabled: true
priority: 85
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
  - fassadenfix-assets
---

# FassadenFix Image Select Skill

## Übersicht

Dieser Skill definiert Richtlinien für die Auswahl und Bewertung von Bildern für FassadenFix Marketingmaterialien. Er stellt sicher, dass alle verwendeten Bilder zur Markenidentität passen und professionelle Qualitätsstandards erfüllen.

**Status:** STANDARD-SKILL (Opt-Out-Prinzip)
**Priorität:** Hoch (85)
**Geltungsbereich:** Global - alle Bildauswahl-Entscheidungen

---

## ⚠️ VERPFLICHTENDE CI-REGELN FÜR BILDER

> **WICHTIG:** Alle Bilder müssen mit den FassadenFix CI-Farben harmonieren. Die folgenden Regeln sind **STRIKT EINZUHALTEN**.

### Verpflichtende Farbharmonie (Bestätigt durch Logo-Finale.pdf)

| Markenfarbe | Pantone | HEX | RGB | Bildfarben müssen harmonieren mit |
|-------------|---------|-----|-----|-----------------------------------|
| **FassadenFix Grün** | **368 C** | `#77bc1f` | R119 G188 B31 | Natur, Weiß, Grau, Blau, Grüntöne |
| **Dunkelgrau** | **445 C** | `#4e5758` | R78 G87 B88 | Alle neutralen Töne, Architektur |

### ❌ VERBOTENE Farbkombinationen

- Bilder mit dominantem Rot, Orange oder Pink
- Grelle Neonfarben
- Farben, die mit Grün (#77bc1f) kollidieren

### Verpflichtende Logo-Platzierung

> Bei Bildern mit Logo-Overlay **ausschließlich** die offiziellen Dateien aus `fassadenfix-assets` verwenden.
> Pfad: `/home/ubuntu/skills/fassadenfix-assets/templates/logos/`

| Hintergrund | Logo-Variante |
|-------------|---------------|
| Hell/Weiß | `FassadenFix_Logo_bunt_transparent_300px.png` |
| Dunkel | `FassadenFix_Logo_weiß.png` |

---

## Bildkategorien

| Kategorie | Verwendung | Priorität |
|-----------|------------|----------|
| **Hero-Bilder** | Landingpages, Banner, Header | Sehr hoch |
| **Fassadenbilder** | Vorher/Nachher, Referenzen | Hoch |
| **Teamfotos** | Über uns, Vertrauen | Hoch |
| **Baustellenbilder** | Prozess, Transparenz | Mittel |
| **Umwelt/Natur** | Nachhaltigkeit | Mittel |

---

## Bildstil-Richtlinien

### Allgemeine Stilprinzipien

| Prinzip | Beschreibung |
|---------|--------------|
| **Professionell** | Hochwertige, scharfe Aufnahmen |
| **Authentisch** | Echte Projekte und Team |
| **Modern** | Zeitgemäße Ästhetik |
| **Vertrauenswürdig** | Seriös und kompetent |

### Farbharmonie mit Markenfarben (Pantone-Referenz)

| Markenfarbe | Pantone | Harmoniert mit | Vermeiden |
|-------------|---------|----------------|----------|
| **Grün (#77bc1f)** | **368 C** | Natur, Weiß, Grau, Blau | Rot, Orange, Pink |
| **Dunkelgrau (#4e5758)** | **445 C** | Alle neutralen Töne | Grelle Neonfarben |

---

## Qualitätskriterien

### Technische Anforderungen

| Kriterium | Minimum | Empfohlen |
|-----------|---------|----------|
| **Auflösung Web** | 1920x1080px | 2560x1440px |
| **Auflösung Print** | 300 DPI | 300 DPI |
| **Dateigröße Web** | < 500KB | < 200KB |
| **Format Web** | JPEG, WebP | WebP |

### Qualitäts-Checkliste

| Prüfpunkt | Akzeptabel | Nicht akzeptabel |
|-----------|------------|------------------|
| **Schärfe** | Gestochen scharf | Unscharf, verwackelt |
| **Belichtung** | Ausgewogen | Über-/Unterbelichtet |
| **Farben** | Natürlich, markenkonform | Verfälscht, grell |
| **Komposition** | Ausgewogen | Abgeschnitten, schief |

---

## Bildkategorie-Details

### Hero-Bilder

| Anforderung | Beschreibung |
|-------------|-------------|
| **Motiv** | Moderne Architektur, saubere Fassaden |
| **Stimmung** | Positiv, einladend, professionell |
| **Farben** | Harmonisch mit Grün und Grau |
| **Freiraum** | Links oder oben für Headlines |

### Fassadenbilder (Vorher/Nachher)

| Anforderung | Beschreibung |
|-------------|-------------|
| **Perspektive** | Identischer Winkel für Vergleich |
| **Beleuchtung** | Ähnliche Lichtverhältnisse |
| **Ausschnitt** | Gleicher Bildausschnitt |

### Teamfotos

| Anforderung | Beschreibung |
|-------------|-------------|
| **Kleidung** | Einheitlich, FassadenFix-Farben |
| **Hintergrund** | Neutral oder Firmenumgebung |
| **Ausdruck** | Freundlich, kompetent |

### Baustellenbilder

| Anforderung | Beschreibung |
|-------------|-------------|
| **Sicherheit** | Alle Sicherheitsausrüstung sichtbar |
| **Ordnung** | Aufgeräumte Baustelle |
| **Technik** | Moderne Ausrüstung im Fokus |

---

## Bildquellen (Priorisierung)

| Priorität | Quelle | Begründung |
|-----------|--------|------------|
| 1 | **Eigene Aufnahmen** | Authentizität, Einzigartigkeit |
| 2 | **KI-generiert** | Anpassbar, markenkonform |
| 3 | **Professioneller Fotograf** | Für wichtige Kampagnen |
| 4 | **Premium Stock** | Wenn eigene nicht verfügbar |
| 5 | **Kostenlose Stock** | Für sekundäre Verwendung |

---

## Bewertungsmatrix (0-10 Punkte)

| Kriterium | Gewichtung |
|-----------|------------|
| **Markenpassung** | 30% |
| **Technische Qualität** | 25% |
| **Emotionale Wirkung** | 20% |
| **Verwendbarkeit** | 15% |
| **Authentizität** | 10% |

**Mindestpunktzahl:** 7/10 für Verwendung

---

## Anwendungsbeispiele

### Landingpage
```
Wähle ein Hero-Bild für die Landingpage
→ Prüft: Moderne Architektur, Freiraum, Grün-Harmonie
```

### Referenz-Seite
```
Wähle Bilder für Vorher/Nachher-Vergleich
→ Prüft: Identische Perspektive, gleiche Beleuchtung
```

---

## Deaktivierung (Opt-Out)

```
--no-image-guidelines
--skip-fassadenfix-image-select
"ohne Bildrichtlinien"
```
