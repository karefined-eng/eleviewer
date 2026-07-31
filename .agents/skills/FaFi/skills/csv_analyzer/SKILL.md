---
name: csv-analyzer
description: Analysiert CSV-Dateien in einem sequentiellen Workflow (Laden, Validieren, Analysieren, Visualisieren).
---

Dieser Skill führt eine sequentielle Analyse von CSV-Dateien durch. Der Workflow ist in vier Schritte unterteilt, die nacheinander ausgeführt werden müssen.

## Freiheitsgrad
**Mittel:** Der Skill bietet einen strukturierten Workflow, erfordert aber vom Benutzer die Angabe des Pfads zur CSV-Datei und die Interpretation der Ergebnisse.

## Workflow

### 1. Daten laden

Führe das `load.py`-Skript aus, um die Daten aus einer CSV-Datei zu laden. Das Skript speichert die Daten in einer temporären Datei (`data.pkl`) für den nächsten Schritt.

**Befehl:**
```bash
python3 scripts/load.py PFAD_ZUR_CSV
```
*Ersetze `PFAD_ZUR_CSV` durch den tatsächlichen Pfad zu deiner CSV-Datei.*

### 2. Daten validieren

Führe das `validate.py`-Skript aus, um die geladenen Daten zu validieren. Dieses Skript prüft auf grundlegende Probleme wie fehlende Werte.

**Befehl:**
```bash
python3 scripts/validate.py
```

### 3. Daten analysieren

Führe das `analyze.py`-Skript aus, um eine deskriptive statistische Analyse der validierten Daten durchzuführen.

**Befehl:**
```bash
python3 scripts/analyze.py
```

### 4. Ergebnisse visualisieren

Führe das `visualize.py`-Skript aus, um die Analyseergebnisse zu visualisieren. Das Skript erstellt ein Boxplot und speichert es als `visualization.png`.

**Befehl:**
```bash
python3 scripts/visualize.py
```

## Ressourcen

*   `scripts/load.py`: Lädt die CSV-Daten.
*   `scripts/validate.py`: Validiert die Daten.
*   `scripts/analyze.py`: Führt die Datenanalyse durch.
*   `scripts/visualize.py`: Visualisiert die Ergebnisse.

