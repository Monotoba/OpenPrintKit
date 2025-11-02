# OpenPrintKit Benutzerhandbuch (Entwurf)

Dieser Text ist eine erste deutschsprachige Fassung. Die vollständige Referenz befindet sich in `docs/user-manual.md` (Englisch).

## Einführung

OpenPrintKit (OPK) definiert ein PDL und erzeugt daraus Profile für mehrere Slicer (Orca, Cura, Prusa/SuperSlicer, Bambu) inkl. Validierung und Regeln.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Häufige Aufgaben

- Validieren: `opk validate ...`
- Regeln: `opk rules --printer P --filament F --process S`
- Generieren: `opk gen --pdl datei.yaml --slicer orca --out outdir`
- Paket: `opk bundle --in src --out profil.orca_printer`
- Installation (Orca): `opk install --src src --dest pfad/presets`

## GUI

Start: `opk-gui` — Reiter für Druckbett, Extruder, Filamente, Maschinensteuerung, Peripherie, G‑code, usw.

---

Beiträge zur Übersetzung sind willkommen.
