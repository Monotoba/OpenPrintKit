# Aide G‑code (résumé)

Version abrégée en français. Voir l’original (anglais) : `docs/gcode-help.md`.

- Hooks disponibles : start, end, before_layer_change, after_layer_change, on_progress_percent, before_snapshot, after_snapshot, etc.
- Macros : blocs nommés réutilisables.
- Placeholders : variables remplacées au rendu (`{nozzle}`, `{bed}`, `{layer}`, `{tool}`, etc.).

Outils CLI :
```bash
opk gcode-hooks --pdl mon.yaml
opk gcode-preview --pdl mon.yaml --hook start --vars vars.json
opk gcode-validate --pdl mon.yaml --vars vars.json
```
