---
name: fassadenfix-copywriting
description: "Erstellt Texte nach FassadenFix Markentonalität und Kommunikationsrichtlinien. Verwenden für: Headlines, CTAs, Angebote, E-Mails, Social Media, Website-Texte, Werbetexte."
default_enabled: true
priority: 80
scope: global
platforms:
  - claude
  - manus
  - chatgpt_codex
  - gemini
  - antigravity
related_skills:
  - fassadenfix-identity
  - fassadenfix-branding
---

# FassadenFix Copywriting Skill

## Übersicht

Dieser Skill stellt Textbausteine, Vorlagen und Richtlinien für die Erstellung von FassadenFix-konformen Texten bereit. Er basiert auf der Markentonalität aus dem `fassadenfix-identity` Skill.

**Status:** STANDARD-SKILL (Opt-Out-Prinzip)
**Priorität:** Hoch (80)
**Geltungsbereich:** Global - alle Texterstellung

---

## ⚠️ VERPFLICHTENDE CI-REGELN FÜR TEXTE

> **WICHTIG:** Alle Texte müssen den FassadenFix CI-Richtlinien entsprechen. Die folgenden Regeln sind **STRIKT EINZUHALTEN**.

### Verpflichtende Markenfarben in Texten (Bestätigt durch Logo-Finale.pdf)

Bei formatierten Texten (HTML, Markdown, Dokumente):

| Element | Farbe | Pantone | HEX | RGB |
|---------|-------|---------|-----|-----|
| **Überschriften** | FassadenFix Grün | **368 C** | `#77bc1f` | R119 G188 B31 |
| **Fließtext** | Dunkelgrau | **445 C** | `#4e5758` | R78 G87 B88 |
| **Links/CTAs** | FassadenFix Grün | **368 C** | `#77bc1f` | R119 G188 B31 |

### Verpflichtende Typografie (Bestätigt durch Logo-Finale.pdf)

| Element | Schriftart | Gewicht | Regel |
|---------|------------|---------|-------|
| **Logo** | Raleway | **Bold (700)** | Offizielle CI |
| **Überschriften** | Raleway | Bold (700) | Empfohlen |
| **Fließtext** | Raleway | Regular (400) | **PFLICHT** - Keine Alternativen |

### Verpflichtende Logo-Verwendung in Dokumenten

> **Ausschließlich** die offiziellen Logo-Dateien aus `fassadenfix-assets` verwenden.
> Pfad: `/home/ubuntu/skills/fassadenfix-assets/templates/logos/`

| Dokumenttyp | Logo-Datei |
|-------------|------------|
| **Angebote/Briefe** | `FassadenFix_Logo_bunt_1000px.png` |
| **E-Mail-Signatur** | `FassadenFix_Logo_400x80.png` |
| **Präsentationen** | `FassadenFix_Logo_bunt_transparent_300px.png` |

---

## Tonalität & Stimme

### Kernprinzipien

| Prinzip | Beschreibung | Beispiel |
|---------|--------------|----------|
| **Persönlich** | Direkte Ansprache, nahbar | "Ich lade Sie ein..." |
| **Selbstbewusst** | Stärke mit Werten | "Unsere Qualität spricht für sich" |
| **Partnerschaftlich** | Beziehung statt Transaktion | "Gemeinsam für Ihre Fassade" |
| **Ehrlich** | Transparent und offen | "Wir sagen Ihnen ehrlich..." |

### Sprachliche Dos and Don'ts

| ✅ DO | ❌ DON'T |
|-------|----------|
| "Ihr sicherer Weg zur sauberen Fassade" | "Wir reinigen Fassaden" |
| "Partnerschaft auf Augenhöhe" | "Wir sind der Dienstleister" |
| "Garantierte Ergebnisse" | "Wir versuchen unser Bestes" |
| "Transparente Preise" | "Günstige Angebote" |
| "Nachhaltige Lösung" | "Schnelle Reinigung" |

---

## Headlines & Claims

### Hauptclaim

> **"Ihr sicherer Weg zur sauberen Fassade"**

### Alternative Claims

| Claim | Verwendung |
|-------|------------|
| "Keine versteckten Kosten, keine halben Sachen" | Preistransparenz |
| "Garantiert sauber. Garantiert fair." | Qualitätsversprechen |
| "Unser Herz schlägt grün" | Nachhaltigkeit |
| "Statt Worte lassen wir Taten sprechen" | Kompetenz |

### Headline-Formeln

| Formel | Beispiel |
|--------|----------|
| **Nutzen + Garantie** | "Saubere Fassade – 5 Jahre garantiert" |
| **Problem + Lösung** | "Algen auf der Fassade? Wir haben die Lösung." |
| **Frage + Antwort** | "Warum FassadenFix? Weil Qualität zählt." |
| **Zahl + Nutzen** | "1.800+ zufriedene Kunden seit 2016" |

---

## Call-to-Actions (CTAs)

### Primäre CTAs

| CTA | Verwendung |
|-----|------------|
| "Jetzt Angebot anfordern" | Hauptkonversion |
| "Kostenlose Beratung sichern" | Erstgespräch |
| "Zur FassadenFix Website" | Navigation |
| "Mehr erfahren" | Informationsseiten |

### Sekundäre CTAs

| CTA | Verwendung |
|-----|------------|
| "Referenzen ansehen" | Vertrauensaufbau |
| "Unsere Garantien entdecken" | USP-Kommunikation |
| "Team kennenlernen" | Persönlichkeit |

---

## Textbausteine nach Kategorie

### Angebote

**Einleitung:**
> "Vielen Dank für Ihr Interesse an einer professionellen Fassadenreinigung. Gerne unterbreiten wir Ihnen folgendes Angebot:"

**Garantie-Hinweis:**
> "Unser Angebot beinhaltet unsere 5-Jahres-Garantie auf Algenfreiheit sowie die jährliche kostenfreie Inspektion."

**Abschluss:**
> "Bei Fragen stehe ich Ihnen persönlich zur Verfügung. Rufen Sie mich einfach an."

### E-Mails

**Begrüßung:**
> "Guten Tag [Name],"

**Verabschiedung:**
> "Mit freundlichen Grüßen und den besten Wünschen für Ihre Immobilie"

### Website-Texte

**Über uns Intro:**
> "FassadenFix steht für professionelle Fassadenreinigung mit Garantie. Seit 2016 vertrauen uns über 1.800 Kunden – und das aus gutem Grund."

**USP-Teaser:**
> "5 Jahre Garantie. Jährliche Inspektion. Pauschalfestpreis. Das ist unser Versprechen an Sie."

---

## Social Media Vorlagen

### LinkedIn

**Unternehmenspost:**
> "🏢 Fassadenreinigung mit Verantwortung\n\nBei FassadenFix bedeutet Qualität mehr als nur saubere Fassaden. Es bedeutet:\n✅ 5 Jahre Garantie\n✅ Transparente Preise\n✅ Nachhaltiges Arbeiten\n\n#Fassadenreinigung #Nachhaltigkeit #Qualität"

### Instagram

**Vorher/Nachher:**
> "📸 Der Unterschied, den professionelle Fassadenreinigung macht!\n\nSwipe für das Ergebnis ➡️\n\n#FassadenFix #VorherNachher #Fassadenreinigung"

---

## Kennzahlen für Texte

| Kennzahl | Wert | Textbaustein |
|----------|------|-------------|
| Garantiedauer | 5 Jahre | "5 Jahre Garantie auf Algenfreiheit" |
| Ablehnungsquote | 9,2% | "9,2% der Fassaden lehnen wir ab" |
| Aufträge | 1.800+ | "Über 1.800 zufriedene Kunden" |
| Garantiefälle | 13 | "Nur 13 Garantiefälle seit 2016" |
| Wassereinsparung | 80%+ | "Über 80% Wassereinsparung" |
| Musterfläche | 1.000 m² | "1.000 m² kostenfreie Musterfläche" |

---

## Zitate von Alexander Retzlaff

| Zitat | Verwendung |
|-------|------------|
| "Unser Anspruch war und ist bis heute, dass wir FassadenFix jederzeit selbst beauftragen würden." | Qualität, Vertrauen |
| "Sie sehen uns als Handwerker – wir uns als Ihr Dienstleister!" | Positionierung |
| "Statt Bilder und Worte lassen wir Taten sprechen." | Kompetenz |
| "Nachhaltigkeit ist nicht nur ein Ziel, sondern unsere Verpflichtung." | Umwelt |

---

## Anwendungsbeispiele

### Angebot schreiben
```
Erstelle ein Angebot für Wohnungsgenossenschaft
→ Verwendet Angebots-Textbausteine
→ Integriert Garantie-Hinweise
→ Persönliche Ansprache
```

### Social Media Post
```
Erstelle einen LinkedIn-Post über Nachhaltigkeit
→ Verwendet Social Media Vorlage
→ Integriert Kennzahlen
→ Fügt passende Hashtags hinzu
```

### Website-Text
```
Schreibe Text für die Startseite
→ Verwendet Hauptclaim
→ Integriert USP-Teaser
→ Fügt CTAs hinzu
```

---

## Deaktivierung (Opt-Out)

```
--no-copywriting
--skip-fassadenfix-copywriting
"ohne Textrichtlinien"
"eigene Texte"
```

---

## Quelle

Alle Textbausteine basieren auf dem **FassadenFix Katalog 2025** und dem `fassadenfix-identity` Skill.
