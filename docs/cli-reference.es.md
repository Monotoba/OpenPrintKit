# Referencia CLI (resumen)

Consulte `docs/cli-reference.md` para la referencia completa en inglés.

Comandos principales: validate, rules, bundle, workspace, install, convert, gcode-hooks, gcode-preview, gcode-validate, pdl-validate, gen-snippets, gen, spool.

Ejemplos:

```bash
opk validate perfiles/*.json
opk gen --pdl mi_printer.yaml --slicer orca --out ./outdir
opk install --src ./perfiles --dest ruta/presets
```
