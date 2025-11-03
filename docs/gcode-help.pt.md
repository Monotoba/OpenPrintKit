# Ajuda de G‑code (resumo)

Resumo em português. Original completo (inglês): `docs/gcode-help.md`.

- Hooks disponíveis: start, end, before_layer_change, after_layer_change, on_progress_percent, before_snapshot, after_snapshot, etc.
- Macros: blocos nomeados reutilizáveis.
- Placeholders: variáveis substituídas ao renderizar (`{nozzle}`, `{bed}`, `{layer}`, `{tool}`, etc.).

Ferramentas de CLI:
```bash
opk gcode-hooks --pdl meu.yaml
opk gcode-preview --pdl meu.yaml --hook start --vars vars.json
opk gcode-validate --pdl meu.yaml --vars vars.json
```
