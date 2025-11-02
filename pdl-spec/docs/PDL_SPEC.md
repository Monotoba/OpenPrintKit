# Printer Definition Language (PDL) Specification

**Version:** 1.0.0
**Status:** Draft
**Maintainer:** OpenPrintKit Project

---

## 1. Overview
PDL defines a structured model for describing 3D printer capabilities, kinematics,
firmware, and material behavior, independent of any slicer.

PDL aims to make printer definitions portable, verifiable, and shareable.

---

## 2. File Format
PDL is serialized as **YAML** or **JSON**.
File extension: `.yaml`, `.yml`, or `.json`.

Each PDL document must define:

| Key | Type | Required | Description |
|-----|------|-----------|-------------|
| `pdl_version` | string | ✅ | Schema/format version |
| `id` | string | ✅ | Unique machine identifier (e.g. `longer.lk5pro`) |
| `name` | string | ✅ | Human-readable name |
| `firmware` | string | ✅ | Firmware family (`marlin`, `klipper`, etc.) |
| `kinematics` | string | ✅ | Motion system type |
| `geometry` | object | ✅ | Bed shape (polygon) and Z height |
| `limits` | object | ❌ | Max speeds, travel, acceleration, jerk |
| `extruders` | array<object> | ❌ | One or more extruders/toolheads |
| `multi_material` | object | ❌ | Spool banks (e.g., AMS/MMU) and mixing |
| `features` | object | ❌ | Auto-bed leveling and probe details |
| `materials` | array<object> | ❌ | Filament/material presets embedded in PDL |
| `process_defaults` | object | ❌ | Baseline print settings |
| `gcode` | object | ❌ | Start/end/tool-change and custom macros |

---

## 3. Example

```yaml
pdl_version: 1.0.0
id: voron.24.350
name: Voron 2.4 (350)
firmware: klipper
kinematics: corexy
geometry:
  bed_shape: [[0,0],[350,0],[350,350],[0,350]]
  z_height: 350
extruders:
  - id: E0
    nozzle_diameter: 0.4
    nozzle_type: hardened_steel
    drive: direct
    max_nozzle_temperature: 300
  - id: E1
    nozzle_diameter: 0.6
    nozzle_type: brass
    drive: direct
multi_material:
  spool_banks:
    - name: AMS-1
      capacity: 4   # up to N; unlimited not enforced here
features:
  auto_bed_leveling: true
  probe:
    type: inductive
    mesh_size: [7, 7]
```

### 3.1 Extruders

An `extruders` array supports any number of extruders or toolheads. Each extruder may specify:

- `id`: Identifier (e.g., E0, Tool-1)
- `nozzle_diameter`: e.g., 0.4
- `nozzle_type`: brass | hardened_steel | stainless | ruby | tungsten | other
- `drive`: direct | bowden | other
- `max_nozzle_temperature`: temperature limit in °C
- `mixing_channels`: number of input channels for mixing nozzles (default 1)

### 3.2 Multi-Material and Color Capacity

Use `multi_material.spool_banks` to model banks/carousels such as AMS or MMU. Each bank defines a `capacity` (integer ≥ 1). Define as many banks as needed; the schema does not impose an upper bound, enabling effectively unlimited colors when hardware permits.

Mixing nozzles can be represented by setting `mixing_channels > 1` on an extruder.

### 3.3 Auto Bed Leveling (ABL) and Probes

The `features` object includes `auto_bed_leveling` and optional `probe` details:

- `probe.type`: inductive | bltouch | crt | strain_gauge | nozzle_contact | manual | other
- `probe.mesh_size`: [rows, cols] integer tuple
- `probe.active_low`: boolean for probe signal polarity

### 3.4 G-code Blocks and Macros

PDL captures reusable G-code sequences in the `gcode` object. The following keys are recognized:

- `start`: sequence run before printing
- `end`: sequence run after printing
- `tool_change`: sequence run when changing tools/extruders
- `layer_change`: sequence run at layer boundaries
- `pause` / `resume`: sequences used when pausing/resuming a print
- `filament_change`: sequence to handle manual filament changes
- `macros`: a map of arbitrary macro names to sequences; use for additional hooks (e.g. `purge_line`, `bed_mesh`, `preheat`)

All fields are arrays of strings (one command per entry). `macros` allows named reusable sequences.

For comprehensive lifecycle coverage, PDL additionally supports both explicit fields and a generic `hooks` map:

- Explicit optional fields include: `before_tool_change`, `after_tool_change`, `before_layer_change`, `after_layer_change`, `before_object`, `after_object`, `before_region`, `after_region`, `retraction`, `unretraction`, `travel_start`, `travel_end`, `bridge_start`, `bridge_end`, `top_layer_start`, `bottom_layer_start`, `support_interface_start`, `support_interface_end`, `before_heating`, `after_heating`, `before_cooling`, `on_abort`, `on_progress_percent`, `on_layer_interval`, `on_time_interval`, `before_snapshot`, `after_snapshot`, `power_loss_resume`, `auto_shutdown`.

- `hooks` is a free-form map: keys are lower-case identifiers (letters, digits, `_.-`) and values are command sequences. This supports future or custom events without schema changes. Example keys: `monitor.progress_25`, `env.lights_on`, `timelapse.before_snapshot`.

Tip: Use conditional templating and variables provided by your slicer (e.g., `{if ...}`, `{layer_z}`, `{filament_diameter[0]}`) inside sequences for dynamic behavior.

### 3.5 Canonical Hooks Reference

PDL defines common, optional hook fields to cover a full-featured slicer lifecycle. If a hook is not present in `gcode`, it’s simply ignored.

- Global lifecycle: `start`, `end`, `on_abort`, `pause`, `resume`, `power_loss_resume`, `auto_shutdown`
- Tool/filament: `tool_change`, `before_tool_change`, `after_tool_change`, `filament_change`
- Layer: `layer_change`, `before_layer_change`, `after_layer_change`, `top_layer_start`, `bottom_layer_start`
- Object/region: `before_object`, `after_object`, `before_region`, `after_region`
- Motion/extrusion: `retraction`, `unretraction`, `travel_start`, `travel_end`, `bridge_start`, `bridge_end`
- Temperature/env: `before_heating`, `after_heating`, `before_cooling`
- Monitoring/timelapse: `on_progress_percent`, `on_layer_interval`, `on_time_interval`, `before_snapshot`, `after_snapshot`
- Support/material: `support_interface_start`, `support_interface_end`

For additional or proprietary events, use the generic `gcode.hooks` map with lower-case keys (letters/digits/`_.-`), for example:

```yaml
gcode:
  hooks:
    monitor.progress_25: ["M117 25%"]
    env.lights_on: ["M150 R255 G255 B255"]
```

Minimal example snippet using placeholders and macros:

```yaml
gcode:
  start:
    - M140 S{bed}
    - M104 S{nozzle}
    - G28
  before_tool_change: ["G10 ; retract"]
  after_tool_change: ["G11 ; unretract", "M117 Tool {tool}"]
  macros:
    purge_line: ["G92 E0", "G1 X0 Y0 F6000", "G1 E10 F300", "G92 E0"]
```

### 3.5 Process Defaults

Keys under `process_defaults` include:

- `layer_height_mm`, `first_layer_mm`
- `speeds_mms`: object of speeds (mm/s)
  - `perimeter`, `infill`, `travel`
  - optional: `external_perimeter`, `top`, `bottom`
- `accelerations_mms2`: object of accelerations (mm/s²)
  - optional: `perimeter`, `infill`, `external_perimeter`, `top`, `bottom`
- `extrusion_multiplier`: scalar where 1.0 = 100%
- `cooling`:
  - `min_layer_time_s`: integer seconds
  - `fan_min_percent`, `fan_max_percent`: 0–100
  - `fan_always_on`: boolean

### 3.6 Limits

Top-level machine limits that may guide generator outputs:

- `acceleration_max` (mm/s²), `jerk_max` (Cura)

---

## 4. Versioning

- PDL follows Semantic Versioning (SemVer):

- Increment MAJOR when breaking schema changes occur.

- Increment MINOR when fields are added.

- Increment PATCH for typo or clarifications.

---
### 3.6 Materials (Embedded Filament Presets)

PDL may embed an array of filament/material presets under `materials`. Each entry typically includes:

- `name`, `filament_type`, optional `filament_diameter`
- Temperature/cooling: `nozzle_temperature`, `bed_temperature`, `fan_speed`
- Retraction: `retraction_length`, `retraction_speed`
- Color metadata: `color` or `color_hex`

This is complementary to standalone Filament profiles (FDL). Use embedded presets for turnkey printer bundles, and standalone FDL for shared libraries.
### 3.7 Endstops (Limit Switches)

Use the top‑level `endstops` object to declare per‑axis limit switch polarity:

```yaml
endstops:
  x_min_active_low: true
  x_max_active_low: false
  y_min_active_low: true
  y_max_active_low: false
  z_min_active_low: true
  z_max_active_low: false
```

If omitted, slicers or firmware defaults apply.
## 4. Machine-Control M-Codes (Reference)

For common machine-control M-codes (power, lighting, fans, probes, camera, safety, etc.) and firmware compatibility notes, see:

- `docs/mcode-reference.md` in the repository root.

PDL expresses these through G-code hooks and macros; use the hooks to place M-codes at appropriate lifecycle events (start/end, layer, tool-change, etc.).
### 3.8 Machine Control (Structured)

PDL can capture high-level machine control intent under `machine_control`. Generators translate this into G-code hooks for specific slicers or firmware:

```yaml
machine_control:
  psu_on_start: true     # → M80 in start
  psu_off_end: true      # → M81 in end
  light_on_start: true   # → M355 S1 in start
  light_off_end: true    # → M355 S0 in end
  rgb_start: { r: 16, g: 16, b: 16 }  # → M150
  chamber: { temp: 30, wait: true }   # → M141 / M191
  enable_mesh_start: true             # → M420 S1
  z_offset: -0.05                     # → M851 Z-0.05
  start_custom: ["M117 Startup"]
  end_custom:   ["M117 Finished"]
  # Peripherals
  camera: { use_before_snapshot: true, command: "M240" }
  sd_logging: { enable_start: true, filename: "log.gco", stop_at_end: true }
  fans: { part_start_percent: 50, aux_index: 1, aux_start_percent: 75, off_at_end: true }
  exhaust: { enable_start: true, speed_percent: 100, off_at_end: true, pin: 10 }
  aux_outputs:
    - { label: Aux1, pin: 11, start_value: 255, end_value: 0 }
    - { label: Aux2, pin: 12, start_value: 128 }
```

Tooling merges `machine_control` with explicit `gcode` hooks at generation time.
