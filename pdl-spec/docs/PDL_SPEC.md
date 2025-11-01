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
| `geometry` | object | ✅ | Bed shape and Z height |
| `limits` | object | ❌ | Max speeds, accelerations |
| `extruders` | array<object> | ❌ | One or more extruders/toolheads |
| `multi_material` | object | ❌ | Spool banks (e.g., AMS/MMU) and mixing |
| `features` | object | ❌ | Auto-bed leveling and probe details |
| `materials` | object | ❌ | Material definitions |
| `process_defaults` | object | ❌ | Baseline print settings |
| `gcode` | object | ❌ | Start/end scripts |

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

## 4. Versioning

- PDL follows Semantic Versioning (SemVer):

- Increment MAJOR when breaking schema changes occur.

- Increment MINOR when fields are added.

- Increment PATCH for typo or clarifications.

---
