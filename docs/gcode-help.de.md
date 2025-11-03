# G‑code Hilfe (Kurzfassung)

Kurzfassung auf Deutsch. Vollständiges Original (Englisch): `docs/gcode-help.md`.

- Verfügbare Hooks: start, end, before_layer_change, after_layer_change, on_progress_percent, before_snapshot, after_snapshot, …
- Makros: benannte, wiederverwendbare Blöcke.
- Platzhalter: Variablen beim Rendern (`{nozzle}`, `{bed}`, `{layer}`, `{tool}`, …).

CLI‑Werkzeuge:
```bash
opk gcode-hooks --pdl mein.yaml
opk gcode-preview --pdl mein.yaml --hook start --vars vars.json
opk gcode-validate --pdl mein.yaml --vars vars.json
```
