# 3D Printer Definition Language

A.K.A.: (PDL, 3D-PDL)

---

1. a richer **landing page** (`pdl-spec/docs/index.md`) with a clear **PDL → IR → Slicer** diagram (Mermaid), and
2. a hands-on **Getting Started Authoring a PDL** guide (`pdl-spec/docs/getting-started.md`) with validation steps, examples, and common pitfalls.

You can paste these files as-is.

---

## 1) `pdl-spec/docs/index.md` (landing page)

````markdown
# Printer Definition Language (PDL)

**PDL** is an open, slicer-agnostic format that defines 3D printers, materials, and processes in a structured, human-readable way (YAML/JSON).
It is the *single source of truth*: define once → generate profiles for multiple slicers.

> **Goal:** Deterministic, reproducible slicing across ecosystems (OrcaSlicer today; Cura/PrusaSlicer next).

---

## Why PDL?

- **Portable:** Move definitions across slicers without reauthoring.
- **Auditable:** Plain-text, version-controlled data with schema validation.
- **Deterministic:** Same inputs → same generated profiles.
- **Extensible:** Optional sections for ABL, multi-extruder, custom G-code.

---

## Architecture

```mermaid
flowchart LR
  A[PDL (YAML/JSON)<br>Printer, Materials, Process Defaults] --> B[OPK Loader & Validation<br>(JSON Schema + Rule Checks)]
  B --> C[Intermediate Representation (IR)]
  C --> D1[Emitter: OrcaSlicer JSON]
  C --> D2[Emitter: Prusa/SuperSlicer INI]
  C --> D3[Emitter: Cura CFG/JSON]
  D1 --> E[Bundle (.orca_printer)]
  D2 --> E2[Profiles/Configs]
  D3 --> E3[Profiles/Configs]
````

PDL documents are validated with **JSON Schema** and additional **rule checks** (e.g., layer height ≤ 80% nozzle).
Validated data becomes a normalized **IR**, then slicer-specific emitters generate the final profiles.

---

## Minimal Example

```yaml
pdl_version: 1.0.0
id: vendor.model
name: Vendor Model
firmware: marlin
kinematics: cartesian
geometry:
  bed_shape: [[0,0],[220,0],[220,220],[0,220]]
  z_height: 250
```

See the **full example**: [Longer LK5 Pro](examples/full_lk5pro.yaml).

---

## What’s in a PDL?

| Section                  | Required | Purpose                                 |
| ------------------------ | :------: | --------------------------------------- |
| `pdl_version`            |     ✅    | Schema version (SemVer)                 |
| `id`, `name`             |     ✅    | Unique identifier + human name          |
| `firmware`, `kinematics` |     ✅    | Firmware family, motion system          |
| `geometry`               |     ✅    | Bed polygon + Z height                  |
| `limits`                 |     —    | Speed/accel bounds                      |
| `extruder`               |     —    | Nozzle, filament, style (direct/bowden) |
| `abl`                    |     —    | ABL type (none/bltouch/inductive/mesh)  |
| `materials`              |     —    | Material envelopes (temps, retract)     |
| `process_defaults`       |     —    | Baseline process settings               |
| `gcode`                  |     —    | Start/end templates                     |

---

## Get Started

* Read: **[Getting Started Authoring a PDL](getting-started.md)**
* Spec: **[PDL Spec (v1.0.0)](PDL_SPEC.md)**
* Schema: **[`pdl.schema.json`](schema/pdl.schema.json)**
* Examples: **[Minimal](examples/minimal.yaml)** • **[LK5 Pro](examples/full_lk5pro.yaml)**

---

````

---

## 2) `pdl-spec/docs/getting-started.md` (authoring guide)

```markdown
# Getting Started Authoring a PDL

This guide walks you from a blank file to a validated **PDL** for your printer.

> **Prerequisites:** any editor, basic YAML/JSON familiarity.

---

## 1) Start from a template

Create `my_printer.yaml`:

```yaml
pdl_version: 1.0.0
id: vendor.model           # e.g., creality.ender3-v1
name: Vendor Model
firmware: marlin           # marlin | klipper | reprap | rrf | smoothie
kinematics: cartesian      # cartesian | corexy | corexz | delta | scara | polar
geometry:
  bed_shape: [[0,0],[220,0],[220,220],[0,220]]
  z_height: 250
limits:
  print_speed_max: 120
  travel_speed_max: 200
extruder:
  style: bowden            # direct | bowden
  default_nozzle_mm: 0.4
  filament_mm: 1.75
abl:
  type: none               # none | bltouch | inductive | manual | mesh
gcode:
  start: |
    M140 S{first_layer_bed_temperature}
    M104 S{first_layer_temperature}
    M190 S{first_layer_bed_temperature}
    M109 S{first_layer_temperature}
    G28
    G92 E0
  end: |
    M104 S0
    M140 S0
    G91
    G1 Z10 F1200
    G90
    M84
materials:
  pla:
    nozzle_temp_c: [200, 210]
    bed_temp_c: [55, 60]
    retract_mm: 0.8
    retract_speed_mms: 40
process_defaults:
  standard:
    layer_height_mm: 0.20
    first_layer_mm: 0.28
    speeds_mms:
      perimeter: 40
      external_perimeter: 30
      infill: 60
      travel: 150
    adhesion: brim
````

---

## 2) Validate with the schema

From the repo root (OPK), using the embedded copy of the schema:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r pdl-spec/requirements.txt

# Validate with jsonschema CLI
python -m jsonschema -i pdl-spec/docs/examples/full_lk5pro.yaml pdl-spec/docs/schema/pdl.schema.json

# Or validate your file
python -m jsonschema -i my_printer.yaml pdl-spec/docs/schema/pdl.schema.json
```

Or with OPK once installed:

```bash
opk pdl-validate my_printer.yaml
```

**Pass criteria:** no errors reported.

---

## 3) Generate slicer profiles (optional, via OPK)

If you have **OpenPrintKit (OPK)** installed:

```bash
# Generate OrcaSlicer profiles from your PDL
opk gen --pdl my_printer.yaml --slicer orca --out dist/my_printer-orca

# Bundle into an Orca-compatible archive
opk bundle --in dist/my_printer-orca --out dist/MyPrinter.orca_printer
```

Open the bundle in OrcaSlicer, or copy profiles to your user preset directory.

---

## 4) Recommended authoring practices

* **Units:** use millimeters (mm) and °C by default. Name fields accordingly.
* **Bed shape:** ensure the polygon is **valid** (non-self-intersecting, clockwise/CCW consistent).
* **Layer heights:** keep defaults ≤ `0.8 × nozzle_diameter`.
* **Retraction:** bowden > direct (e.g., 1.5–5.0 mm vs 0.4–1.2 mm); TPU uses shorter/slower.
* **ABL consistency:** if `abl.type != none`, ensure your **start G-code** probes or loads a mesh.
* **Material envelopes:** provide **ranges** (e.g., `[200, 210]`) for recommended tuning windows.
* **IDs:** `vendor.model[-variant]` (lowercase, dot-separated) for stability in URLs and filenames.
* **Versioning:** bump `pdl_version` using SemVer when breaking changes occur.

---

## 5) Common validation errors & fixes

| Error                                    | Likely Cause         | Fix                                                            |
| ---------------------------------------- | -------------------- | -------------------------------------------------------------- |
| `geometry.bed_shape: minItems`           | Too few vertices     | Use ≥ 3 points; rectangle needs 4 corners                      |
| `kinematics: not in enum`                | Typo                 | One of: `cartesian, corexy, corexz, delta, scara, polar`       |
| `extruder.style: not in enum`            | Typo/unknown         | Use `direct` or `bowden`                                       |
| Start G-code placeholders not recognized | Wrong variable names | Use placeholders that your slicer supports or emitters replace |
| Rule warning: layer height too big       | >80% of nozzle       | Lower `layer_height_mm` or increase nozzle size                |

---

## 6) Example: LK5 Pro (full)

See **[examples/full_lk5pro.yaml](examples/full_lk5pro.yaml)** for a complete, validated document that drives OPK’s Orca generator.

---

## 7) Submit & collaborate

When PDL becomes its own repo:

* Open PRs with a **minimal** and **full** example per printer
* Include a “test slice” screenshot or generated profile diff
* Keep discussions constructive; align to the spec and rules

---

## 8) Next steps

* Extend the spec with multiple extruders and IDEX examples
* Add more rule checks (e.g., TPU-specific retraction limits)
* Publish via GitHub Pages using MkDocs Material

````

---

## Optional: Add the new page to your MkDocs nav

Update `pdl-spec/mkdocs.yml`:

```yaml
nav:
  - Overview: index.md
  - Getting Started: getting-started.md
  - Specification:
      - PDL Spec (v1.0.0): PDL_SPEC.md
  - Examples:
      - Minimal: examples/minimal.yaml
      - LK5 Pro (full): examples/full_lk5pro.yaml
  - Schema:
      - pdl.schema.json: schema/pdl.schema.json
  - Contributing: contributing.md
  - License: license.md
````

---
