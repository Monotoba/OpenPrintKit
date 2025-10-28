# 🧩 OpenPrintKit (OPK)

[![Build Status](https://github.com/YOUR_USERNAME/OpenPrintKit/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/OpenPrintKit/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20|%203.12%20|%203.13-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Chat](https://img.shields.io/badge/community-chat-brightgreen.svg)]()

[![Build Status](https://github.com/YOUR_USERNAME/OpenPrintKit/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/OpenPrintKit/actions)

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

“From open data to perfect first layers.”
— The OpenPrintKit Project


---

### 🔧 Next suggestions
Once you’ve added this file:
1. Replace `YOUR_USERNAME` in badge URLs with your GitHub username.
2. Add a simple `LICENSE` file (`MIT`) and push both:
   ```bash
   git add README.md LICENSE
   git commit -m "docs: add complete README with badges and project summary"
   git push
  ```
