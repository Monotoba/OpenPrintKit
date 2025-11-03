# OpenPrintKit Overview

This help page summarizes OPK concepts and UI:

- PDL (Printer Description Language) is the canonical source of truth.
- Tabs: Build Area, Extruders, Multi‑Material, Filaments, Features, Machine Control, Peripherals, G‑code, Logs.
- G‑code hooks, macros, and hooks map drive where commands are injected.
- Structured `machine_control` captures high‑level intent; generators translate this per firmware.
- Tools: G-code Preview, Validate Hook Variables, M-code Reference.
  - Generate Snippets: produce firmware-ready start/end G-code files from a PDL.
  - Generate Profiles: produce slicer profiles for Orca, Cura, Prusa, ideaMaker, Bambu (with Preview before writing).
- Settings: set default slicer/firmware, output directory, variables JSON, and firmware policies.

## Process Defaults

Use the Process Defaults tab in the GUI to set common parameters that map to multiple slicers:
- Heights: layer height, first layer height
- Speeds: perimeter, infill, travel, external, top/bottom
- Retraction: length and speed
- Adhesion: none/skirt/brim/raft
- Extrusion multiplier (material flow)
- Cooling: min layer time, fan min/max, fan always on
- Accelerations (where supported): perimeter, infill, external, top/bottom, travel

Click “Check…” to run rules and see inline hints for problematic values.

See also: `docs/firmware-mapping.md`, `docs/mcode-reference.md`, `docs/cli-reference.md`.

Quick links:

- User Manual: `docs/user-manual.md`
- GUI Screenshots: `docs/images/`

## Settings Controls (Highlights)

- Default slicer/firmware — used by generators and UI defaults.
- Output directory — suggested path for generated files.
- Variables JSON — default vars file for G‑code Preview.
- Vars Templates JSON — optional file with named variables templates used by G‑code dialogs.
- Network retry policy — limit/backoff/jitter for integrations (spool clients).
- Recent files limit — maximum number of recent PDL/Vars entries (per list) remembered by G‑code dialogs.

Tools → Clear Recent Files… clears recent PDL/Vars lists for G‑code dialogs. The same action exists in Preferences.

### Slicer Support

For a summary of supported slicers, import/export coverage, and mapping depth, see `docs/slicer-support.md`.

## PDL → Slicer Mapping (Highlights)

- process_defaults.layer_height_mm → slicer layer height
- process_defaults.first_layer_mm → first layer height
- process_defaults.speeds_mms.{perimeter,infill,travel} → perimeter/infill/travel speeds
- process_defaults.speeds_mms.external_perimeter → external perimeter speed
- process_defaults.speeds_mms.{top,bottom} → top/bottom solid infill speeds
- process_defaults.extrusion_multiplier → extrusion multiplier / material flow
- process_defaults.cooling.{min_layer_time_s,fan_*} → cooling and fan settings
- limits.acceleration_max → print/travel acceleration (where supported)
- limits.jerk_max → Cura jerk settings
- process_defaults.accelerations_mms2.{perimeter,infill,external_perimeter,top,bottom} → per-section acceleration (where supported)

## OpenPrintTag

Embed metadata in start G-code as comments for downstream tools. Configure under the OpenPrintTag tab; the generator inserts a `;BEGIN:OPENPRINTTAG` block with a JSON payload.

## Firmware-Specific Tips

The GUI surfaces firmware‑aware tips in the Peripherals tab based on the selected firmware:

- RRF: SD logging uses M929; named pins supported (use string pin names). Prefer M106/M107 P index for fans.
- Klipper: Camera M240 maps to `M118 TIMELAPSE_TAKE_FRAME` by default; customize camera command or use macros.
- GRBL: Exhaust maps to M8 (on)/M9 (off).
- LinuxCNC: Exhaust maps to M7 (on)/M9 (off).

See “Firmware Mapping” in the Help menu for details.
