# OpenPrintKit Overview

This help page summarizes OPK concepts and UI:

- PDL (Printer Description Language) is the canonical source of truth.
- Tabs: Build Area, Extruders, Multi‑Material, Filaments, Features, Machine Control, Peripherals, G‑code, Logs.
- G‑code hooks, macros, and hooks map drive where commands are injected.
- Structured `machine_control` captures high‑level intent; generators translate this per firmware.
- Tools: G‑code Preview, Validate Hook Variables, M‑code Reference.
  - Generate Snippets: produce firmware‑ready start/end G‑code files from a PDL.
  - Generate Profiles: produce slicer profiles for Orca, Cura, Prusa, ideaMaker, Bambu (with Preview before writing).
- Settings: set default slicer/firmware, output directory, variables JSON, and firmware policies.

See also: `docs/firmware-mapping.md`, `docs/mcode-reference.md`, `docs/cli-reference.md`.

## PDL → Slicer Mapping (Highlights)

- process_defaults.layer_height_mm → slicer layer height
- process_defaults.first_layer_mm → first layer height
- process_defaults.speeds_mms.{perimeter,infill,travel} → perimeter/infill/travel speeds
- process_defaults.extrusion_multiplier → extrusion multiplier / material flow
- process_defaults.cooling.{min_layer_time_s,fan_*} → cooling and fan settings
- limits.acceleration_max → print/travel acceleration (where supported)
- limits.jerk_max → Cura jerk settings

## OpenPrintTag

Embed metadata in start G-code as comments for downstream tools. Configure under the OpenPrintTag tab; the generator inserts a `;BEGIN:OPENPRINTTAG` block with a JSON payload.

## Firmware-Specific Tips

The GUI surfaces firmware‑aware tips in the Peripherals tab based on the selected firmware:

- RRF: SD logging uses M929; named pins supported (use string pin names). Prefer M106/M107 P index for fans.
- Klipper: Camera M240 maps to `M118 TIMELAPSE_TAKE_FRAME` by default; customize camera command or use macros.
- GRBL: Exhaust maps to M8 (on)/M9 (off).
- LinuxCNC: Exhaust maps to M7 (on)/M9 (off).

See “Firmware Mapping” in the Help menu for details.
