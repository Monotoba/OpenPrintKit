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
| `extruder` | object | ❌ | Extruder config |
| `abl` | object | ❌ | Auto-bed leveling type |
| `materials` | object | ❌ | Material definitions |
| `process_defaults` | object | ❌ | Baseline print settings |
| `gcode` | object | ❌ | Start/end scripts |

---

## 3. Example

```yaml
pdl_version: 1.0.0
id: longer.lk5pro
name: Longer LK5 Pro
firmware: marlin
kinematics: cartesian
geometry:
  bed_shape: [[0,0],[300,0],[300,300],[0,300]]
  z_height: 400
limits:
  print_speed_max: 120
  travel_speed_max: 200
extruder:
  style: bowden
  default_nozzle_mm: 0.4
  filament_mm: 1.75
materials:
  pla:
    nozzle_temp_c: [200, 210]
    bed_temp_c: [55, 60]

```

## 4. Versioning

- PDL follows Semantic Versioning (SemVer):

- Increment MAJOR when breaking schema changes occur.

- Increment MINOR when fields are added.

- Increment PATCH for typo or clarifications.

---
