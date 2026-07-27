# FassadenFix Angebotsgenerator

Webbasiertes Tool zur Erstellung von Angeboten für die FassadenFix Systemreinigung.

## Schnellstart

1. `index.html` im Browser öffnen
2. Kundendaten eingeben
3. Immobilie(n) hinzufügen
4. Positionen aus Artikelkatalog wählen
5. PDF exportieren

## Projektstruktur

```
angebotsgenerator/
├── index.html              # Haupt-Anwendung
├── css/                    # Stylesheets
├── js/                     # JavaScript-Module
├── data/
│   ├── artikel.json        # Artikelkatalog
│   └── preisstufen.json    # Preisstaffelung
├── docs/                   # Dokumentation
└── assets/                 # Logos, Bilder
```

## Daten anpassen

### Artikelkatalog
Bearbeite `data/artikel.json` um Artikel hinzuzufügen/ändern.

### Preisstaffelung
Bearbeite `data/preisstufen.json` für m²-Preise und Rabatte.

## Multi-Tool-Arbeit

Dieses Projekt ist Git-versioniert und kann mit verschiedenen AI-Tools bearbeitet werden:
- **Antigravity** (Google)
- **Claude** (Anthropic)
- **GitHub Copilot**

Bei Änderungen: `git add -A && git commit -m "Beschreibung"`
