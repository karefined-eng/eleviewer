---
name: image-optimizer
description: Optimiert Bilder durch Komprimierung und Größenänderung.
---

# Image Optimizer Skill

Dieser Skill optimiert Bilder, indem er eine Reihe von vordefinierten Schritten zur Komprimierung und Größenänderung anwendet. Er demonstriert einen Arbeitsablauf mit geringem Freiheitsgrad, bei dem die Operationen eng definiert sind, um konsistente Ergebnisse zu gewährleisten.

## Freiheitsgrad: Niedrig

Dieser Skill ist so konzipiert, dass er mit minimaler Konfiguration funktioniert. Die Optimierungsparameter sind im begleitenden Python-Skript `scripts/optimizer.py` festgelegt. Dies stellt sicher, dass alle Bilder einem standardisierten Optimierungsprozess unterzogen werden, was für Aufgaben, die eine hohe Konsistenz erfordern, unerlässlich ist.

## Anweisungen

Um diesen Skill zu verwenden, geben Sie den Pfad zu dem Bild an, das Sie optimieren möchten. Der Skill führt die folgenden Aktionen aus:

1.  Das Bild wird auf eine maximale Breite oder Höhe von 1024 Pixeln verkleinert, wobei das Seitenverhältnis erhalten bleibt.
2.  Das Bild wird mit einer Qualitätsstufe von 85 % komprimiert.
3.  Das optimierte Bild wird mit dem Suffix `_optimized` im selben Verzeichnis gespeichert.

Führen Sie den folgenden Befehl aus, um ein Bild zu optimieren:

```bash
python3 /home/ubuntu/skills/image-optimizer/scripts/optimizer.py --image_path PFAD_ZUM_BILD
```
