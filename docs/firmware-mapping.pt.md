# Mapeamento de Firmware (resumo)

Esta é uma tradução resumida. Para detalhes completos, consulte o original em inglês: `docs/firmware-mapping.md`.

- Marlin
  - Log em SD: `M928` (início) / `M29` (fim)
  - RGB via `M150`
  - Pinos customizados: `M42 P<pino> S<val>`
- RepRapFirmware (RRF)
  - Log em SD: `M929 P"arquivo" S1` (parar: `M929 S0`)
  - Pinos nomeados (`out1`, etc.), ventiladores `M106/M107 P`
- Klipper
  - `M240` ↔ `M118 TIMELAPSE_TAKE_FRAME` por política
  - Ventiladores/LEDs muitas vezes como macros
- GRBL / LinuxCNC
  - Exaustão (refrigeração): `M7/M8` ligar / `M9` desligar

Veja o original para dicas por periféricos (luzes, câmera, ventiladores, exaustão) e políticas exatas.
