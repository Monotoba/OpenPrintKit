# OpenPrintKit User Manual

This manual explains how to install, use, and troubleshoot OpenPrintKit (OPK) — a toolkit for defining, validating, generating, bundling, and installing 3D printer configurations across slicers. It consolidates the essentials from the codebase and docs into a single, task‑oriented guide.

## What Is OpenPrintKit?

Define once. Slice anywhere.
OPK introduces a structured Printer Description Language (PDL) plus schemas, rules, generators, and tools to manage printer, filament, and process profiles. It targets OrcaSlicer initially and extends to Cura, Prusa/SuperSlicer, Bambu Studio, and more.

- Printers: build area, kinematics, firmware, machine control.
- Filaments: materials, temperatures, retraction, cooling.
- Processes: layer heights, speeds, accelerations, adhesion.

OPK validates profiles, enforces rules, and produces reproducible, version‑controllable outputs.

## System Requirements

- Python 3.11+
- Optional: PySide6 for GUI (installed via project dependencies)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Project Structure (essentials)

- `opk/` — Core library, CLI, GUI
  - `core/` — schemas, rules, bundling, gcode utilities
  - `plugins/` — generators and converters (Orca, Cura, Prusa, Bambu, etc.)
  - `cli/` — command-line entry (`opk`)
  - `ui/` — GUI (`opk-gui`)
- `schemas/` — JSON schemas for profile validation
- `examples/` — sample profiles
- `docs/` — documentation (this manual and references)

## Core Concepts

- Profiles: JSON files for `printer`, `filament`, and `process` types.
- PDL (Printer Description Language): a structured model (JSON/YAML) that captures printer capabilities and hooks; generators map from PDL to slicer formats.
- Rules: schema‑independent checks (contextual tips, warnings, errors).
- Bundles: Orca‑compatible `.orca_printer` archives or `.zip` for other slicers.

## Quick Start (CLI)

Validate example profiles:
```bash
opk validate examples/printers/Longer_LK5_Pro_Marlin.json             examples/filaments/PLA_Baseline_LK5Pro.json             examples/processes/Standard_0p20_LK5Pro.json
```

Run rule checks across profiles:
```bash
opk rules   --printer  examples/printers/Longer_LK5_Pro_Marlin.json   --filament examples/filaments/PLA_Baseline_LK5Pro.json   --process  examples/processes/Standard_0p20_LK5Pro.json
```

Bundle for Orca:
```bash
opk bundle --in examples --out dist/LK5Pro_OrcaProfile_v1.orca_printer
```

Initialize a workspace with standard folders:
```bash
opk workspace init ./my-workspace
```

## Generating Profiles From PDL

Generate target slicer profiles from a PDL file:
```bash
opk gen --pdl my_printer.pdl.yaml --slicer orca --out ./outdir [--bundle ./out.orca_printer]
```
Supported `--slicer` values: `orca`, `cura`, `prusa`, `ideamaker`, `bambu`, `superslicer`, `kisslicer`.

Acceleration overrides (optional) — merged into `process_defaults.accelerations_mms2`:
```bash
opk gen --pdl my.pdl.yaml --slicer prusa --out ./outdir   --acc-perimeter 1000 --acc-infill 1200 --acc-top 800
```

## Converters

Convert existing configs to OPK profiles (best‑effort):
```bash
opk convert --from cura        --in CURA_FILE_OR_DIR --out OUT_DIR
opk convert --from prusa       --in INPUT.ini        --out OUT_DIR
opk convert --from superslicer --in INPUT.ini        --out OUT_DIR
opk convert --from ideamaker   --in INPUT.cfg        --out OUT_DIR
```

## Install to Orca Presets

Dry run and install (with optional backup):
```bash
opk install --src ./profiles --dest ~/AppData/Roaming/OrcaSlicer/user/default/presets   --backup ./backup_orca_presets.zip --dry-run
# then without --dry-run to write
```

## G‑code Tools

- List hooks after firmware policy mapping:
  ```bash
  opk gcode-hooks --pdl my.pdl.yaml
  ```
- Preview a hook with variables:
  ```bash
  opk gcode-preview --pdl my.pdl.yaml --hook start --vars vars.json
  ```
- Validate all hooks against variables:
  ```bash
  opk gcode-validate --pdl my.pdl.yaml --vars vars.json
  ```

## Spool Databases (Basic)

Perform CRUD/search operations against spool databases (Spoolman, TigerTag, OpenSpool/OpenTag3D):
```bash
# items (raw) output
opk spool --source spoolman --base-url http://host --action search --query PLA --page 1 --page-size 25 --format items

# normalized output (envelope)
opk spool --source tigertag --base-url https://api --action read --id 123 --format normalized
```

Endpoint overrides and pagination:
```bash
# Inline JSON or file-based overrides
opk spool --source openspool --base-url https://api   --action read --id 123   --endpoints-json '{"read":[["/custom/spool/{id}", null]]}'
```

Retries/backoff (defaults shown):
- Retry limit: 5
- Backoff: 0.5s base, Jitter: 0.25s
- Set via GUI Settings, or env vars: `OPK_NET_RETRY_LIMIT`, `OPK_NET_RETRY_BACKOFF`, `OPK_NET_RETRY_JITTER`.

## The GUI (OPK Studio)

Launch the application:
```bash
opk-gui
```

Main areas:
- Build Area: geometry, firmware, limits.
- Extruders, Multi‑Material, Filaments.
- Features: ABL, probe, endstops.
- Machine Control: PSU, mesh, Z offset, custom start/end.
- Peripherals: lights, RGB, chamber, camera, fans, SD logging, exhaust, aux outputs, custom peripherals.
- G‑code: lifecycle, layer, tool/filament, motion, temperature/env, monitoring hooks; macros and additional hooks.
- OpenPrintTag: metadata block embedded into start G‑code.
- Issues: results from rule checks with filters.

Helpful actions:
- Check… on various tabs runs rules and focuses relevant issues.
- Help… buttons open domain docs (Overview, Firmware Mapping, G‑code Help, M‑code Reference).
- Issues tab filters by level and search text.
- Inline hint icons appear near fields when rules apply (hover for tips).

## Firmware‑Specific Guidance (summary)

- Marlin:
  - SD logging via `M928` start / `M29` stop.
  - RGB via `M150` requires LED/NeoPixel support.
  - `M42` expects numeric pins; prefer fan `M106/M107` or numeric `P`.
- RRF (RepRapFirmware):
  - SD logging via `M929 P"filename" S1` (stop: `M929 S0`).
  - Prefer named pins (e.g., `out1`); fans use `M106/M107 P`.
  - RGB via `M150 R/G/B`.
- Klipper:
  - `M240` maps to `M118 TIMELAPSE_TAKE_FRAME` by policy.
  - Fans often implemented as macros; ensure `printer.cfg` defines them.
- GRBL/LinuxCNC:
  - Exhaust maps to coolant: `M7/M8` on / `M9` off.
  - Fans not standard; prefer coolant or custom peripherals.
- Bambu:
  - Keep start/end minimal; prefer printer‑side macros.

The Issues tab and inline hints surface contextual tips based on the selected firmware.

## Workspaces

Initialize a workspace with common directories:
```bash
opk workspace init ./my-workspace
```
Creates:
- `profiles/printers`, `profiles/filaments`, `profiles/processes`
- `bundles`, `logs`
- Gitignore for bundles/logs/pyc

## Troubleshooting

- Profiles fail schema: run `opk validate` and check error messages.
- Rules show warnings: open the GUI, press “Check…” on related tabs to see hints inline.
- Orca install path: varies by OS and Orca version — try a dry run to confirm.
- Slicing with external CLI: ensure slicer binaries are on PATH (e.g., `CuraEngine`).
- Network operations (spool): adjust retry/backoff/jitter in Settings or env vars if needed.
- GUI exits immediately: try `OPK_DEBUG=1 python -m opk.ui.main_window` and set `QT_QPA_PLATFORM` (`xcb`/`wayland`) if necessary.

## Environment Variables

- `OPK_NET_RETRY_LIMIT` — integer retries (default 5)
- `OPK_NET_RETRY_BACKOFF` — base backoff seconds (default 0.5)
- `OPK_NET_RETRY_JITTER` — jitter seconds (default 0.25)
- `OPK_SPOOL_ENDPOINTS` — JSON overrides per source
- `OPK_DEBUG` — if set, prints additional GUI debug info (platform/screens)

## References

- CLI Reference: `docs/cli-reference.md`
- Firmware Mapping: `docs/firmware-mapping.md`
- G‑code Help: `docs/gcode-help.md`
- M‑code Reference: `docs/mcode-reference.md`
- Project Overview: `docs/overview.md`
- Implementation Status: `docs/implementation-status.md`
