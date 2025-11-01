# 🧩 OpenPrintKit (OPK)

[![Build Status](https://github.com/YOUR_USERNAME/OpenPrintKit/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/OpenPrintKit/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20|%203.12%20|%203.13-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Chat](https://img.shields.io/badge/community-chat-brightgreen.svg)]()

---

### Define once. Slice anywhere.
**OpenPrintKit (OPK)** is an open-source toolkit for defining, validating, and bundling 3D printer configurations into slicer-ready packages — starting with **OrcaSlicer**, and expanding to Cura, PrusaSlicer, and beyond.

It introduces a structured, machine-readable **Printer Description Language (PDL)** for defining:
- 🖨️ **Printers** — build volume, firmware, kinematics, and G-code templates
- 🧵 **Filaments** — materials, temperatures, and retraction behavior
- ⚙️ **Processes** — layer heights, speeds, infill, and adhesion strategies

OPK’s schema-driven validation ensures configuration correctness, portability, and version control — enabling truly **deterministic, reproducible slicing**.

---

## 🚀 Quickstart

For a step-by-step guide with more detail, see `docs/quickstart.md`.

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in editable mode
pip install -e .

# Validate individual profiles
opk validate examples/printers/Longer_LK5_Pro_Marlin.json
opk validate examples/filaments/PLA_Baseline_LK5Pro.json
opk validate examples/processes/Standard_0p20_LK5Pro.json

# Bundle into an Orca-compatible archive
opk bundle --in examples --out dist/LK5Pro_OrcaProfile_v1.orca_printer

# Run rules checks across profiles (schema-independent sanity checks)
opk rules \
  --printer  examples/printers/Longer_LK5_Pro_Marlin.json \
  --filament examples/filaments/PLA_Baseline_LK5Pro.json \
  --process  examples/processes/Standard_0p20_LK5Pro.json

# Initialize a new workspace (with examples)
opk workspace init ./my-workspace
ls ./my-workspace
```

✅ Example profiles validate successfully; full test suite passes locally.

### Documentation

- Overview: docs/overview.md
- Quickstart: docs/quickstart.md
- CLI Reference: docs/cli-reference.md
- Firmware Mapping Guide: docs/firmware-mapping.md
- G-code Help: docs/gcode-help.md
- M-code Reference: docs/mcode-reference.md
- Creator Intro: docs/OpenPrintKit_Creator_Intro.md
- Manufacturer Intro: docs/OpenPrintKit_Manufacturer_Intro.md
- Project Spec: docs/project-spec.md
- Project Status: docs/project-status.md
- Implementation Status: docs/implementation-status.md
- System Notes: docs/system_notes.md

🧠 Why OPK?

Problem	OPK Solution

Slicer configs are siloed and fragile	Schema-based, versioned JSON profiles

Sharing printer profiles is error-prone	Portable .orca_printer bundles

Inconsistent calibration across slicers	Unified Printer Description Language (PDL)

Manual tweaking wastes time	Deterministic generation and validation

Profiles lost in GUI exports	Git-friendly source files + reproducible build

🧰 Project Structure
```
OpenPrintKit/
├─ opk/                   # Core Python package
│  ├─ core/               # Schemas, validation, bundling
│  ├─ cli/                # CLI entry point (opk)
│  └─ ui/                 # GUI scaffolding (PySide6)
├─ schemas/               # JSON schemas for printer/filament/process/bundle
├─ examples/              # Example JSON profiles (LK5 Pro)
├─ tests/                 # Pytest unit tests
 └─ dist/                  # Output bundles (.orca_printer)
```

### CLI Overview

- `opk validate {paths...}` — Schema validation for JSON profiles
- `opk rules [--printer P] [--filament F] [--process S]` — Rule checks (warnings/errors) with summary and exit code 2 on errors
- `opk bundle --in SRC --out OUT.orca_printer` — Build Orca bundle from `printers/`, `filaments/`, `processes/`
- `opk workspace init ROOT [--no-examples]` — Scaffold a standard workspace
- `opk install --src SRC --dest ORCA_PRESET_DIR [--backup BACKUP.zip] [--dry-run]` — Dry-run and install profiles to Orca presets
- `opk convert --from cura --in INPUT --out OUTDIR` — Convert Cura definitions to OPK printer profiles
- `opk gcode-hooks --pdl PDL.yaml` — List available G-code hooks in a PDL file
- `opk gcode-preview --pdl PDL.yaml --hook start --vars vars.json` — Render a hook with provided variables
- `opk gcode-validate --pdl PDL.yaml --vars vars.json` — Validate all hooks for unresolved placeholders
- `opk pdl-validate --pdl PDL.yaml` — Validate PDL schema and machine-control rules
- `opk gen-snippets --pdl PDL.yaml --out-dir OUTDIR [--firmware marlin|klipper|rrf|grbl|linuxcnc]` — Generate start/end G-code files
- `opk gen --pdl PDL.yaml --slicer orca|cura|prusa|ideamaker|bambu --out OUTDIR [--bundle BUNDLE.orca_printer]` — Generate slicer profiles
- `opk spool --source spoolman|tigertag|openspool|opentag3d --base-url URL --action create|read|update|delete|search [...]` — Spool DB stubs

### GUI

- Launch with `opk-gui`
- Menu actions: Validate, Run Rules, Build Bundle, Workspace Init, Install to Orca, Preferences
- Toolbar with quick-access icons for common actions
- Drag-and-drop `.json` files onto the window to validate them
- Tools → G-code Preview: open a PDL YAML/JSON, select a hook (start, layer_change, etc.), define variables, and preview rendered G-code
- Tools → Validate Hook Variables: open a PDL and variables JSON to scan all hooks for unresolved placeholders
- Help → Overview: high-level concepts and UI
- Help → G-code Help: hooks, macros, placeholders
- Help → M-code Reference: machine-control M-codes

If the app exits immediately, try:

- `OPK_DEBUG=1 python -m opk.ui.main_window` (prints platform + screen count)
- Set platform explicitly: `QT_QPA_PLATFORM=xcb` or `QT_QPA_PLATFORM=wayland`
- Ensure you have a display/session (X11/Wayland) available

### Development

- Requirements: Python 3.11+ (see `pyproject.toml`)
- Setup:
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install -e .`
- Run tests: `PYTHONPATH=. pytest -q`
- CLI help: `python -m opk.cli --help`
- GUI: `opk-gui` or `python -m opk.ui.main_window`

🧩 Features

✅ JSON-Schema validation for all profiles

🧵 Modular PDL model (Printer / Filament / Process)

🧰 CLI for validation, bundling, and conversion

🧪 Automated testing (pytest + GitHub Actions)

🧠 Extensible to multiple slicers (Orca, Cura, Prusa)

🔧 Planned GUI editor and install wizard (PySide6)

🧱 Roadmap
Phase	Feature	Status
1	Baseline CLI + schemas + examples	✅ Complete
2	PDL intermediate model + converters	🚧 In progress
3	GUI Editor (PySide6)	🔜 Planned
4	Multi-slicer export (Cura, Prusa, SuperSlicer)	🔜 Planned
5	Online registry of printer definitions	🧩 Future milestone
🧾 License

This project is licensed under the MIT License — see LICENSE
 for details.

🤝 Contributing

Pull requests welcome!
If you’d like to contribute:

Fork the repo

Create a feature branch (git checkout -b feature/add-printer-registry)

Run tests (pytest -q)

Submit a PR

For major changes, open an issue first to discuss your ideas.

💬 Community
Resource	Link
Issues / Bug reports	GitHub Issues

Feature Requests	Discussions

Chat / Collaboration	Coming soon (Matrix or Discord)

— The OpenPrintKit Project


---
