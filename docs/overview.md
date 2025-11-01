# OpenPrintKit Overview

This help page summarizes OPK concepts and UI:

- PDL (Printer Description Language) is the canonical source of truth.
- Tabs: Build Area, Extruders, Multi‑Material, Filaments, Features, Machine Control, Peripherals, G‑code, Logs.
- G‑code hooks, macros, and hooks map drive where commands are injected.
- Structured `machine_control` captures high‑level intent; generators translate this per firmware.
- Tools: G‑code Preview, Validate Hook Variables, M‑code Reference.
- Settings: set default slicer/firmware, output directory, variables JSON, and firmware policies.

See also: `docs/firmware-mapping.md`, `docs/mcode-reference.md`, `docs/cli-reference.md`.

## OpenPrintTag

Embed metadata in start G-code as comments for downstream tools. Configure under the OpenPrintTag tab; the generator inserts a `;BEGIN:OPENPRINTTAG` block with a JSON payload.

## Firmware-Specific Tips

The GUI surfaces firmware‑aware tips in the Peripherals tab based on the selected firmware:

- RRF: SD logging uses M929; named pins supported (use string pin names). Prefer M106/M107 P index for fans.
- Klipper: Camera M240 maps to `M118 TIMELAPSE_TAKE_FRAME` by default; customize camera command or use macros.
- GRBL: Exhaust maps to M8 (on)/M9 (off).
- LinuxCNC: Exhaust maps to M7 (on)/M9 (off).

See “Firmware Mapping” in the Help menu for details.
