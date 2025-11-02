# PDL Schema Reference (Practical)

This reference summarizes the common PDL (Printer Description Language) fields used by OPK. It complements JSON Schema files and code paths (opk/ui/pdl_editor.py, opk/core/*, opk/plugins/slicers/*).

## Top Level

- `name` (string) — Human‑readable printer name.
- `firmware` (string) — `marlin`, `rrf` (RepRapFirmware), `klipper`, `grbl`, `linuxcnc`, `smoothieware`, `repetier`, `bambu`, etc.
- `geometry` (object)
  - `bed_shape` (list[list[number]]) — Polygon points; rectangle can be [ [0,0], [X,0], [X,Y], [0,Y] ].
  - `z_height` (number) — Max Z.

## Extruders

- `extruders` (array)
  - `nozzle_diameter` (number)
  - `nozzle_type` (string) — e.g., `brass`, `hardened_steel`.
  - `drive` (string) — `direct` or `bowden`.
  - `max_nozzle_temp` (number)
  - `mixing_channels` (integer)

## Materials (Filaments)

- `materials` (array)
  - `name` (string)
  - `filament_type` (string) — e.g., `PLA`, `PETG`.
  - `filament_diameter` (number) — e.g., 1.75 or 2.85.
  - `nozzle_temperature` (number °C)
  - `bed_temperature` (number °C)
  - `retraction_length` (number mm)
  - `retraction_speed` (number mm/s)
  - `fan_speed` (number percent)
  - `color_hex` (string `#RRGGBB`)

## Process Defaults

- `process_defaults` (object)
  - `layer_height_mm` (number)
  - `first_layer_mm` (number)
  - `speeds_mms` (object)
    - `perimeter`, `infill`, `travel`, `external_perimeter`, `top`, `bottom` (numbers)
  - `accelerations_mms2` (object)
    - `perimeter`, `infill`, `external_perimeter`, `top`, `bottom` (numbers)
  - `adhesion` (string) — `skirt` | `brim` | `raft` | `none`.
  - `extrusion_multiplier` (number) — e.g., 1.00 → 100% flow.
  - `retract_mm` (number) / `retract_speed_mms` (number)
  - `cooling` (object)
    - `min_layer_time_s` (integer)
    - `fan_min_percent` (integer 0–100)
    - `fan_max_percent` (integer 0–100)
    - `fan_always_on` (bool)

## Limits

- `limits` (object)
  - `print_speed_max` (number)
  - `travel_speed_max` (number)
  - `acceleration_max` (number)
  - `jerk_max` (number) — mainly for Cura.

## Machine Control

- `machine_control` (object)
  - `psu_on_start` (bool), `psu_off_end` (bool)
  - `enable_mesh_start` (bool)
  - `z_offset` (number) — M851.
  - `start_custom`, `end_custom` (list of strings)
  - `lights`: `on_start`, `off_end` (bools)
  - `rgb_start` (object) — `{ r, g, b }` (0–255)
  - `chamber` (object) — `{ temp, wait }`
  - `camera` (object) — `{ use_before_snapshot, use_after_snapshot, command }`
  - `fans` (object)
    - `part_start_percent` (int)
    - `aux_index` (int)
    - `aux_start_percent` (int)
    - `off_at_end` (bool)
  - `sd_logging` (object)
    - `enable_start` (bool)
    - `filename` (string)
    - `stop_at_end` (bool)
  - `exhaust` (object)
    - `enable_start` (bool)
    - `speed_percent` (int)
    - `off_at_end` (bool)
    - `pin` (int|string)
    - `fan_index` (int)
  - `aux_outputs` (array) — `{ label, pin, start_value?, end_value? }`
  - `custom_peripherals` (array) — `{ label, hook, sequence:list }`

## G‑code

- `gcode` (object)
  - Explicit hooks — `start`, `end`, `pause`, `resume`, `before_layer_change`, etc. (array of strings)
  - `macros` — name → sequence (array of strings)
- `hooks` (object) — free‑form extra hooks (name → sequence)

## OpenPrintTag

- `open_print_tag` (object)
  - `id`, `version`, `url`, `manufacturer`, `model`, `serial`, `notes`, `data` (map)

## Examples

Minimal layout (YAML):
```yaml
name: My Printer
firmware: marlin
geometry:
  bed_shape: [[0,0],[220,0],[220,220],[0,220]]
  z_height: 250
extruders:
  - nozzle_diameter: 0.4
materials:
  - name: PLA
    filament_type: PLA
    filament_diameter: 1.75
process_defaults:
  layer_height_mm: 0.2
  first_layer_mm: 0.28
  speeds_mms:
    perimeter: 40
    infill: 60
    travel: 150
machine_control:
  camera:
    use_before_snapshot: true
    command: M240
```
