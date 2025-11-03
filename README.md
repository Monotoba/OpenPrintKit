# 🧩 OpenPrintKit (OPK)

[![Build Status](https://github.com/Monotoba/OpenPrintKit/actions/workflows/ci.yml/badge.svg)](https://github.com/Monotoba/OpenPrintKit/actions)
[![Docs](https://img.shields.io/badge/docs-site-blue.svg)](https://monotoba.github.io/OpenPrintKit/)
[![Release](https://github.com/Monotoba/OpenPrintKit/actions/workflows/release.yml/badge.svg)](https://github.com/Monotoba/OpenPrintKit/actions/workflows/release.yml)
[![User Manual](https://img.shields.io/badge/User%20Manual-read-blue.svg)](https://monotoba.github.io/OpenPrintKit/user-manual/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20|%203.12%20|%203.13-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Chat](https://img.shields.io/badge/community-chat-brightgreen.svg)]()
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)

---

## Table of Contents

- [Quickstart](#quickstart)
- [Documentation](#documentation)
- [CLI Overview](#cli-overview)
- [Slicer Support](#slicer-support)
- [GUI](#gui)
  - [GUI Tips](#gui-tips)
- [Development](#development)
- [Translations](#translations)
- [Features](#features)
- [Roadmap](#roadmap)
- [License](#license)
- [Contributing](#contributing)
- [Community](#community)

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

# End-user install (PyPI)
pip install openprintkit
# or include the GUI
pip install 'openprintkit[gui]'

# Dev install (editable)
pip install -e .
# Optional dev extras
pip install -e '.[gui]'
pip install -e '.[nfc]'
pip install -e '.[docs]'

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

- Website: https://monotoba.github.io/OpenPrintKit/
- Changelog: CHANGELOG.md
- Overview: [docs/overview.md](docs/overview.md)
- Quickstart: [docs/quickstart.md](docs/quickstart.md)
- CLI Reference: [docs/cli-reference.md](docs/cli-reference.md)
- User Manual: [docs/user-manual.md](docs/user-manual.md)
- Firmware Mapping Guide: [docs/firmware-mapping.md](docs/firmware-mapping.md)
- G-code Help: [docs/gcode-help.md](docs/gcode-help.md)
- M-code Reference: [docs/mcode-reference.md](docs/mcode-reference.md)
- Creator Intro: [docs/OpenPrintKit_Creator_Intro.md](docs/OpenPrintKit_Creator_Intro.md)
- Manufacturer Intro: [docs/OpenPrintKit_Manufacturer_Intro.md](docs/OpenPrintKit_Manufacturer_Intro.md)
- Project Spec: [docs/project-spec.md](docs/project-spec.md)
- Project Status: [docs/project-status.md](docs/project-status.md)
- Implementation Status: [docs/implementation-status.md](docs/implementation-status.md)
- System Notes: [docs/system_notes.md](docs/system_notes.md)

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
- `opk gui-screenshot --out OUTDIR [--targets main,rules,profiles,snippets,settings,preferences]` — Capture offscreen GUI screenshots for docs
- `opk slice --slicer slic3r|prusaslicer|superslicer|curaengine --model MODEL.stl --profile PROFILE.ini --out OUT.gcode [--flags "..."]` — Slice via external CLI (binary must be on PATH)
- `opk spool --source spoolman|tigertag|openspool|opentag3d --base-url URL --action create|read|update|delete|search [--query Q] [--page N] [--page-size N] [--format items|normalized] [--endpoints-file FILE.json] [--endpoints-json JSON]` — Spool DB ops with pagination and endpoint overrides. Default retry limit: 5 attempts (configurable in App Settings or `OPK_NET_RETRY_LIMIT`).

### Slicer Support

| Slicer        | Generate | Bundle |
|---------------|----------|--------|
| OrcaSlicer    | ✅ JSON  | ✅ `.orca_printer` |
| Cura          | ✅ CFG   | ✅ `.zip`         |
| PrusaSlicer   | ✅ INI   | ✅ `.zip`         |
| SuperSlicer   | ✅ INI   | ❌ seed only      |
| Bambu Studio  | ✅ INI   | ❌ seed only      |
| ideaMaker     | ✅ CFG   | ✅ `.zip`         |
| KISSlicer     | ✅ INI   | ❌ seed only      |

See full details in docs/project-status.md.

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

#### GUI Tips

- Dialogs remember last-used paths and fields (QSettings):
  - Generate Profiles: slicer, output dir, PDL path (when applicable), and bundle settings.
  - Generate Snippets: PDL path and output dir.
  - Build Bundle: last bundle save location.
- Recents & templates:
  - Generate Profiles: recent output directories and recent bundle outputs (limit in Settings → Recent files limit). Clear via Tools → Clear Recent Files… or Preferences.
  - G-code Preview/Validate: recent PDL/Vars dropdowns and Clear; configurable Variables Templates JSON (Settings) in addition to built-ins.
- Keyboard shortcuts (G-code dialogs):
  - Preview: Ctrl+O (Open PDL), Ctrl+L (Load Vars), Ctrl+S (Save Vars As…), Ctrl+T (Insert Template…), Ctrl+R (Render).
  - Validate: Ctrl+O (Open PDL), Ctrl+L (Open Vars), Ctrl+T (Template…), Ctrl+V (Validate).
- Bundling from Generate Profiles:
  - Supported for Orca, Cura, Prusa, ideaMaker; auto-suggests a filename if empty.
  - Suffix is added automatically (`.orca_printer` for Orca, `.zip` for others).
 - Use the “…” button to pick a bundle path directly.
 - Issues tab filters:
   - Level filter (ALL, ERROR+WARN, ERROR, WARN, INFO) and a Path filter (ALL, machine_control, process_defaults, gcode) help focus diagnostics quickly.
  - Rules dialog filters:
    - Path dropdown (built from detected field prefixes) and a text Filter box let you narrow results by path prefix and search terms (path/message).

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

Dev notes:
- Update extracted output keys: `python scripts/extract_generator_keys.py` (writes `docs/exact-generator-keys.md`).
- Pre-commit hook (optional):
  - `pip install pre-commit && pre-commit install`
  - Runs a check to ensure `docs/exact-generator-keys.md` is up to date when generator code changes.

## Translations

- Español
  - Manual de Usuario: [docs/user-manual.es.md](docs/user-manual.es.md)
  - CLI: [docs/cli-reference.es.md](docs/cli-reference.es.md)
  - Resumen: [docs/overview.es.md](docs/overview.es.md)
- Français
  - Guide Utilisateur: [docs/user-manual.fr.md](docs/user-manual.fr.md)
  - CLI: [docs/cli-reference.fr.md](docs/cli-reference.fr.md)
  - Aperçu: [docs/overview.fr.md](docs/overview.fr.md)
- Deutsch
  - Benutzerhandbuch: [docs/user-manual.de.md](docs/user-manual.de.md)
  - CLI: [docs/cli-reference.de.md](docs/cli-reference.de.md)
  - Überblick: [docs/overview.de.md](docs/overview.de.md)
- Português
  - Manual do Usuário: [docs/user-manual.pt.md](docs/user-manual.pt.md)
  - CLI: [docs/cli-reference.pt.md](docs/cli-reference.pt.md)
  - Visão Geral: [docs/overview.pt.md](docs/overview.pt.md)

🧩 Features

✅ JSON-Schema validation for all profiles

🧵 Modular PDL model (Printer / Filament / Process)

🧰 CLI for validation, bundling, and conversion

🧪 Automated testing (pytest + GitHub Actions)

🧠 Extensible to multiple slicers (Orca, Cura, Prusa)

🖥️ PySide6 GUI editor, tools, and install wizard (OPK Studio)

🧱 Roadmap
Phase	Feature	Status
1	Baseline CLI + schemas + examples	✅ Complete
2	PDL intermediate model + converters	✅ Initial
3	GUI Editor (PySide6)	✅ Complete
4	Multi-slicer export (Cura, Prusa, SuperSlicer)	✅ Initial
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

Recommended:
- Enable pre-commit to keep docs/exact-generator-keys.md current:
  - `pip install pre-commit && pre-commit install`
  - The hook runs `scripts/extract_generator_keys.py` on changes to generator modules and fails if the keys doc is stale.

💬 Community
Resource	Link
Issues / Bug reports	GitHub Issues

Feature Requests	Discussions

Chat / Collaboration	Coming soon (Matrix or Discord)

— The OpenPrintKit Project


---
