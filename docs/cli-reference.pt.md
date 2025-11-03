# Referência de CLI do OPK

Nota: original em inglês: `docs/cli-reference.md`.

## Conteúdo
- Comandos
- Bancos de dados de bobinas (spool)
- Substituições avançadas
- Dicas da GUI

Comandos:
- `opk validate {caminhos...}` — Valida perfis JSON pelo schema.
- `opk bundle --in SRC --out OUT.orca_printer` — Gera pacote Orca de `printers/`, `filaments/`, `processes/`.
- `opk rules [--printer P] [--filament F] [--process S]` — Executa regras (com resumo).
- `opk workspace init ROOT [--no-examples]` — Inicializa um workspace padrão.
- `opk install --src SRC --dest ORCA_PRESET_DIR [--backup BACKUP.zip] [--dry-run]` — Simula e instala nos presets do Orca.
- `opk convert --from cura|prusa|superslicer|ideamaker --in IN --out OUTDIR` — Converte para perfis OPK.
- `opk gcode-hooks --pdl PDL.yaml` — Lista hooks após mapeamento de firmware.
- `opk gcode-preview --pdl PDL.yaml --hook start --vars vars.json` — Renderiza um hook com variáveis.
- `opk gcode-validate --pdl PDL.yaml --vars vars.json` — Valida todos os hooks (placeholders não resolvidos).
- `opk pdl-validate --pdl PDL.yaml` — Valida o schema PDL + regras de machine_control.
- `opk tag-preview --pdl PDL.yaml` — Mostra o bloco OpenPrintTag no início.
- `opk gen-snippets --pdl PDL.yaml --out-dir OUT [--firmware FW]` — Gera `*_start.gcode` e `*_end.gcode`.
- `opk gen --pdl PDL.yaml --slicer orca|cura|prusa|ideamaker|bambu|superslicer|kisslicer --out OUTDIR [--bundle OUT]` — Gera perfis.
- `opk gui-screenshot --out OUTDIR [--targets ...]` — Captura telas da GUI sem exibição.
- `opk slice --slicer slic3r|prusaslicer|superslicer|curaengine --model MODEL.stl --profile PROFILE.ini --out OUT.gcode [--flags "..."]` — Fatiamento via CLI externo.
- `opk spool --source spoolman|tigertag|openspool|opentag3d --base-url URL --action create|read|update|delete|search [...]` — Operações em banco de dados de bobinas.

### Bancos de dados de bobinas
- Opções comuns: `--api-key`, `--id`, `--payload`, `--query`, `--page`, `--page-size`, `--format`, `--endpoints-*`.
- Política de retry configurável via preferências/variáveis (`OPK_NET_*`).

### Substituições avançadas
- `--bundle` — produz arquivo (Orca: `.orca_printer`; demais: `.zip`).
- Acelerações (`process_defaults.accelerations_mms2`):
  - `--acc-perimeter`, `--acc-infill`, `--acc-external`, `--acc-top`, `--acc-bottom`.

Veja também: `docs/overview.pt.md`, `docs/gcode-help.md`, `docs/firmware-mapping.md`.
