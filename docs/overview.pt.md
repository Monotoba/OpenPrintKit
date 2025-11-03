# Visão Geral do OpenPrintKit

Nota: original em inglês: `docs/overview.md`.

Esta página resume os conceitos e a interface do OPK:

- PDL (Printer Description Language) é a fonte de verdade.
- Abas: Área de Impressão, Extrusoras, Multi‑Material, Filamentos, Recursos, Controle da Máquina, Periféricos, G‑code, Logs.
- Hooks de G‑code, macros e o mapa de hooks definem onde comandos são inseridos.
- `machine_control` captura intenção de alto nível; geradores traduzem por firmware.
- Ferramentas: Pré‑visualização de G‑code, Validação de Variáveis, Referência de M‑code.
  - Gerar trechos: cria arquivos start/end G‑code prontos para o firmware.
  - Gerar perfis: produz perfis para Orca, Cura, Prusa, ideaMaker, Bambu (com Pré‑visualização antes de gravar).
- Configurações: slicer/firmware padrão, diretório de saída, JSON de variáveis, políticas de firmware.

Veja também: `docs/firmware-mapping.md`, `docs/mcode-reference.md`, `docs/cli-reference.md`.

Links rápidos:
- Manual do Usuário: `docs/user-manual.pt.md`
- Capturas da GUI: `docs/images/`

## Destaques das Configurações
- Slicer/firmware padrão — usado pelos geradores e pela UI.
- Diretório de saída — caminho sugerido para arquivos gerados.
- Variáveis (JSON) — valores padrão para a Pré‑visualização de G‑code.
- Modelos de variáveis — arquivo opcional com modelos nomeados.
- Política de retry de rede — limite/backoff/jitter para integrações.
- Arquivos recentes — número máximo de PDL/Vars lembrados.

## Mapeamento PDL → Slicer (destaques)
- process_defaults.layer_height_mm → altura de camada
- process_defaults.first_layer_mm → primeira camada
- process_defaults.speeds_mms.{perimeter,infill,travel} → velocidades
- process_defaults.extrusion_multiplier → multiplicador / fluxo de material
- process_defaults.cooling.{min_layer_time_s,fan_*} → refrigeração/ventiladores
- limits.acceleration_max → aceleração de impressão/viagem
- limits.jerk_max → jerk (Cura)
- process_defaults.accelerations_mms2.{...} → aceleração por seção

## OpenPrintTag
Metadados no G‑code inicial (`;BEGIN:OPENPRINTTAG` com JSON).

## Dicas específicas de firmware
- RRF: M929 para log em SD; pinos nomeados suportados.
- Klipper: M240 ↔ `M118 TIMELAPSE_TAKE_FRAME` por padrão.
- GRBL: exaustão = M8 (ligar) / M9 (desligar).
- LinuxCNC: exaustão = M7 (ligar) / M9 (desligar).
