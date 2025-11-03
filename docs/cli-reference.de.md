# OPK CLI Referenz

Hinweis: englisches Original: `docs/cli-reference.md`.

## Inhaltsverzeichnis
- Befehle
- Spulendatenbanken
- Erweiterte Overrides
- GUI‑Tipps

Befehle:
- `opk validate {pfade...}` — Validiert JSON‑Profile gegen das Schema.
- `opk bundle --in SRC --out OUT.orca_printer` — Erstellt Orca‑Bundle aus `printers/`, `filaments/`, `processes/`.
- `opk rules [--printer P] [--filament F] [--process S]` — Führt Regelprüfungen aus (mit Zusammenfassung).
- `opk workspace init ROOT [--no-examples]` — Initialisiert ein Standard‑Workspace.
- `opk install --src SRC --dest ORCA_PRESET_DIR [--backup BACKUP.zip] [--dry-run]` — Trockenlauf und Installation in Orca‑Presets.
- `opk convert --from cura|prusa|superslicer|ideamaker --in IN --out OUTDIR` — Konvertiert in OPK‑Profile.
- `opk gcode-hooks --pdl PDL.yaml` — Listet G‑code‑Hooks nach Firmware‑Mapping.
- `opk gcode-preview --pdl PDL.yaml --hook start --vars vars.json` — Rendert einen Hook mit Variablen.
- `opk gcode-validate --pdl PDL.yaml --vars vars.json` — Validiert alle Hooks (unaufgelöste Platzhalter).
- `opk pdl-validate --pdl PDL.yaml` — Validiert PDL‑Schema + machine_control‑Regeln.
- `opk tag-preview --pdl PDL.yaml` — Zeigt den OpenPrintTag‑Block am Start.
- `opk gen-snippets --pdl PDL.yaml --out-dir OUT [--firmware FW]` — Generiert `*_start.gcode` und `*_end.gcode`.
- `opk gen --pdl PDL.yaml --slicer orca|cura|prusa|ideamaker|bambu|superslicer|kisslicer --out OUTDIR [--bundle OUT]` — Generiert Profile.
- `opk gui-screenshot --out OUTDIR [--targets ...]` — GUI‑Screenshots im Offscreen.
- `opk slice --slicer slic3r|prusaslicer|superslicer|curaengine --model MODEL.stl --profile PROFILE.ini --out OUT.gcode [--flags "..."]` — Slicing via externes CLI.
- `opk spool --source spoolman|tigertag|openspool|opentag3d --base-url URL --action create|read|update|delete|search [...]` — Spool‑Datenbankoperationen.

### Spulendatenbanken
- Häufige Optionen: `--api-key`, `--id`, `--payload`, `--query`, `--page`, `--page-size`, `--format`, `--endpoints-*`.
- Retry‑Richtlinie via Einstellungen/Umgebungsvariablen (`OPK_NET_*`).

### Erweiterte Overrides
- `--bundle` — erstellt Archiv (Orca: `.orca_printer`; andere: `.zip`).
- Beschleunigungen (`process_defaults.accelerations_mms2`):
  - `--acc-perimeter`, `--acc-infill`, `--acc-external`, `--acc-top`, `--acc-bottom`.

Siehe auch: `docs/overview.de.md`, `docs/gcode-help.md`, `docs/firmware-mapping.md`.
