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

✅ All example profiles validate successfully (4 tests passed).

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
├─ tests/                 # Pytest unit tests (4 passing)
└─ dist/                  # Output bundles (.orca_printer)
```

### CLI Overview

- `opk validate {paths...}` — Schema validation for JSON profiles
- `opk rules [--printer P] [--filament F] [--process S]` — Rule checks (warnings/errors) with summary and exit code 2 on errors
- `opk bundle --in SRC --out OUT.orca_printer` — Build Orca bundle from `printers/`, `filaments/`, `processes/`
- `opk workspace init ROOT [--no-examples]` — Scaffold a standard workspace

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
