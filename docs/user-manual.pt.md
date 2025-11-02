# Manual do Usuário do OpenPrintKit (Rascunho)

Este arquivo é um ponto de partida em português. Consulte `docs/user-manual.md` (inglês) para a referência completa.

## Introdução

OpenPrintKit (OPK) permite definir um PDL e gerar perfis para vários slicers (Orca, Cura, Prusa/SuperSlicer, Bambu) com validações e regras.

## Instalação

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

Executar: `opk-gui` — abas para área de impressão, extrusoras, filamentos, controle da máquina, periféricos, G‑code, etc.

---

Contribuições para a tradução são bem-vindas.
