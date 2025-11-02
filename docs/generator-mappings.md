# Generator Mappings (Detailed)

This document summarizes how OPK maps PDL fields to slicer profile formats. For ground truth, see `opk/plugins/slicers/*.py` and the extracted key lists in `exact-generator-keys.md`.

Conventions:
- PDL path uses dot notation (e.g., `geometry.bed_shape`).
- Output key is the target setting name (CFG/INI/JSON).

## OrcaSlicer

Emits printer/filament/process JSON plus start/end sequences from hooks. Bundling to `.orca_printer` is supported via `opk bundle`.

Examples (non‑exhaustive):

| PDL path | Output file | Output key |
|---|---|---|
| `geometry.bed_shape` / `geometry.z_height` | `printer.json` | build volume, origin |
| `extruders[0].nozzle_diameter` | `printer.json` | nozzle diameter |
| `materials[0].filament_diameter` | `filament.json` | diameter |
| `materials[0].nozzle_temperature` | `filament.json` | temperature |
| `materials[0].bed_temperature` | `filament.json` | bed temp |
| `process_defaults.layer_height_mm` | `process.json` | layer height |
| `process_defaults.first_layer_mm` | `process.json` | first layer height |
| `gcode.start` / `gcode.end` | merged | start_gcode / end_gcode |

## Cura (CFG)

| PDL path | CFG key |
|---|---|
| `geometry.bed_shape` → width/depth, `geometry.z_height` | `machine_width`, `machine_depth`, `machine_height` |
| `extruders[0].nozzle_diameter` | `machine_nozzle_size` |
| `materials[0].filament_diameter` | `material_diameter` |
| `materials[0].nozzle_temperature` | `material_print_temperature` |
| `materials[0].bed_temperature` | `material_bed_temperature` |
| `process_defaults.layer_height_mm` | `layer_height` |
| `process_defaults.first_layer_mm` | `initial_layer_height` |
| `extruders[0].nozzle_diameter` | `line_width` |
| `process_defaults.speeds_mms.perimeter` | `speed_wall` |
| `process_defaults.speeds_mms.external_perimeter` | `speed_wall_0` |
| `process_defaults.speeds_mms.infill` | `speed_infill` |
| `process_defaults.speeds_mms.travel` | `speed_travel` |
| `process_defaults.retract_mm` | `retraction_amount` (with `retraction_enable=1`) |
| `process_defaults.retract_speed_mms` | `retraction_speed` |
| `process_defaults.adhesion` | `adhesion_type` |
| `process_defaults.extrusion_multiplier` | `material_flow` (percent) |
| `process_defaults.cooling.min_layer_time_s` | `cool_min_layer_time` |
| `process_defaults.cooling.fan_*` | `cool_fan_enabled`, `cool_fan_speed`, `cool_fan_speed_min` |
| `limits.acceleration_max` | mapped to Cura acceleration if present |

Source: `opk/plugins/slicers/cura.py`.

## Prusa / SuperSlicer / Bambu (INI)

| PDL path | INI section | INI key |
|---|---|---|
| `geometry.bed_shape` | `[printer:<name>]` | `bed_shape` |
| `extruders[0].nozzle_diameter` | `[printer:<name>]` | `nozzle_diameter` |
| `gcode.start`, `gcode.end` | `[printer:<name>]` | `start_gcode`, `end_gcode` |
| `materials[0].filament_diameter` | `[filament:<name>]` | `filament_diameter` |
| `materials[0].nozzle_temperature` | `[filament:<name>]` | `temperature` |
| `materials[0].bed_temperature` | `[filament:<name>]` | `bed_temperature` |
| `process_defaults.extrusion_multiplier` | `[filament:<name>]` | `extrusion_multiplier` |
| `process_defaults.layer_height_mm` | `[print:<name>]` | `layer_height` |
| `process_defaults.first_layer_mm` | `[print:<name>]` | `first_layer_height` |
| `process_defaults.speeds_mms.perimeter` | `[print:<name>]` | `perimeter_speed` |
| `process_defaults.speeds_mms.infill` | `[print:<name>]` | `infill_speed` |
| `process_defaults.speeds_mms.travel` | `[print:<name>]` | `travel_speed` |
| `process_defaults.speeds_mms.external_perimeter` | `[print:<name>]` | `external_perimeter_speed` (if present) |
| `process_defaults.speeds_mms.top` | `[print:<name>]` | `top_solid_infill_speed` |
| `process_defaults.speeds_mms.bottom` | `[print:<name>]` | `bottom_solid_infill_speed` |
| `process_defaults.accelerations_mms2.*` | `[print:<name>]` | per‑section acceleration if supported |
| `process_defaults.cooling.min_layer_time_s` | `[print:<name>]` | `min_layer_time` |
| `process_defaults.cooling.fan_min_percent` | `[print:<name>]` | `min_fan_speed` |
| `process_defaults.cooling.fan_max_percent` | `[print:<name>]` | `max_fan_speed` |

Sources: `opk/plugins/slicers/prusa.py`, `superslicer.py`, `bambu.py`.

## ideaMaker / KISSlicer

| PDL path | Output |
|---|---|
| `geometry.bed_shape`, `geometry.z_height` | machine dimensions |
| `extruders[0].nozzle_diameter` | nozzle diameter |
| `process_defaults.layer_height_mm`, `first_layer_mm` | layer heights |
| `process_defaults.speeds_mms.*` | major speed hints |
| `gcode.start`, `gcode.end` | start/end sequences |

Sources: `opk/plugins/slicers/ideamaker.py`, `kisslicer.py`.

## Notes

- Generators are best‑effort seeds; fine‑tune in slicers as needed.
- CLI acceleration overrides merge into `process_defaults.accelerations_mms2` before generation.
- Entry points: `opk/cli/__main__.py`; hook rendering: `opk/core/gcode.py`.
