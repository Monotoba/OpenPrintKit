# Manual do Usuário do OpenPrintKit (Rascunho)

Este arquivo é um ponto de partida em português. Consulte `docs/user-manual.md` (inglês) para a referência completa.

## Introdução

OpenPrintKit (OPK) permite definir um PDL e gerar perfis para vários slicers (Orca, Cura, Prusa/SuperSlicer, Bambu) com validações e regras.

## Instalação

Uso (PyPI):
```bash
pip install openprintkit
# com GUI
pip install 'openprintkit[gui]'
```

Desenvolvimento (editable):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Tarefas comuns

- Validar: `opk validate ...`
- Regras: `opk rules --printer P --filament F --process S`
- Gerar: `opk gen --pdl arquivo.yaml --slicer orca --out outdir`
- Empacotar: `opk bundle --in src --out perfil.orca_printer`
- Instalar (Orca): `opk install --src src --dest caminho/presets`

## GUI

Executar: `opk-gui`

Abas: Área de Impressão, Extrusoras, Multi‑Material, Filamentos, Recursos, Controle da Máquina, Periféricos, G‑code.

Dicas:
- Diálogos lembram últimos caminhos (QSettings).
- Ferramentas → Pré‑visualizar G‑code / Validar Variáveis.
- Gerar perfis (pré‑visualização antes de gravar) e trechos start/end.

---

Contribuições para a tradução são bem-vindas.

## Início Rápido (CLI)

Validar exemplos:
```bash
opk validate examples/printers/Longer_LK5_Pro_Marlin.json \
             examples/filaments/PLA_Baseline_LK5Pro.json \
             examples/processes/Standard_0p20_LK5Pro.json
```

Executar regras:
```bash
opk rules --printer examples/printers/Longer_LK5_Pro_Marlin.json \
          --filament examples/filaments/PLA_Baseline_LK5Pro.json \
          --process  examples/processes/Standard_0p20_LK5Pro.json
```

Bundle para Orca:
```bash
opk bundle --in examples --out dist/LK5Pro.orca_printer
```

Workspace:
```bash
opk workspace init ./meu-projeto
```

## Gerar a partir de um PDL
```bash
opk gen --pdl minha_impressora.yaml --slicer orca --out outdir [--bundle out.orca_printer]
```
Slicers: orca, cura, prusa, ideamaker, bambu, superslicer, kisslicer.

## Conversores
```bash
opk convert --from cura --in ARQ_OU_DIR --out OUTDIR
opk convert --from prusa --in INPUT.ini --out OUTDIR
```

## Ferramentas de G‑code
- Hooks: `opk gcode-hooks --pdl meu.yaml`
- Pré‑visualizar: `opk gcode-preview --pdl meu.yaml --hook start --vars vars.json`
- Validar: `opk gcode-validate --pdl meu.yaml --vars vars.json`

## Solução de Problemas
- GUI fecha? Tente: `OPK_DEBUG=1 python -m opk.ui.main_window` e `QT_QPA_PLATFORM=xcb|wayland`.
- Binário de slicer ausente? Verifique o PATH (ex. `CuraEngine`).
- Regras: use “Check…” na UI para ver dicas em linha.

## Variáveis de Ambiente
- `OPK_NET_RETRY_LIMIT/BACKOFF/JITTER` — política de rede.
- `OPK_DEBUG` — logs extras da GUI.

## Referências
- CLI: `docs/cli-reference.pt.md`
- Visão Geral: `docs/overview.pt.md`
- Ajuda de G‑code: `docs/gcode-help.md`

## Capturas da GUI

![Janela principal](images/main_window.png)

![Diálogo de Regras](images/rules_dialog.png)

![Gerar perfis](images/generate_profiles.png)

![Gerar trechos](images/generate_snippets.png)

![Configurações do app](images/app_settings.png)

![Preferências](images/preferences.png)
