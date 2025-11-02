# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog. Dates are YYYY-MM-DD.

## [Unreleased]

### Added
- Generators (Cura/Prusa/Bambu):
  - Map `process_defaults` layer heights and speeds (perimeter/infill/travel; external_perimeter; top/bottom where supported).
  - Map `process_defaults.extrusion_multiplier` and `process_defaults.cooling` (min layer time, fan min/max/always on).
  - Map `limits` acceleration/jerk (Cura acceleration/jerk; Prusa/Bambu max print/travel acceleration).
  - Per‑section accelerations via `process_defaults.accelerations_mms2`.
- Bundlers:
  - New `build_profile_bundle(files, out, slicer)` for Cura/Prusa/ideaMaker; Orca bundling unchanged.
- CLI:
  - `gen --bundle OUT.zip` for cura/prusa/ideamaker; `--acc-*` overrides merged into `process_defaults.accelerations_mms2`.
  - Commands: `rules`, `workspace init`, `install`, `convert --from cura`, `gcode-hooks`, `gcode-preview`, `gcode-validate`, `pdl-validate`, `tag-preview`, `gen-snippets`.
- GUI:
  - Build menu (Validate, Run Rules, Build Bundle) with keyboard shortcuts and tooltips.
  - Generate Profiles dialog supports in‑editor PDL, multi‑file Preview, and bundle summary with open‑folder.
  - Extensive field tooltips and status tips; Restore Defaults + Help buttons in key tabs.
  - Issues tab with inline rules validation (Refresh/Copy) and status bar issue counts; editor wrapped in scroll area to reduce height.
- Rules:
  - Firmware guidance: GRBL/LinuxCNC coolant mapping (M7/M8/M9), Klipper camera mapping info, RRF SD logging mapping/filename spacing and named pin suggestion, Marlin numeric pin requirement.
  - Sanity checks for process_defaults (layer heights vs nozzle, cooling fan percent range and min layer time, non‑negative per‑section accelerations).
- Docs:
  - MkDocs site for pdl‑spec; docs added/updated (Overview, Firmware Mapping, G‑code Help, CLI Reference).
  - README badges and links (Build, Docs website).

### Changed
- CLI: stabilized parser; removed duplicate subparser definitions.
- GUI: lazy‑import subdialogs; centralized PySide6 compat stubs for headless CI.

### CI
- Matrix: Python 3.10–3.14 (Windows exclusions for 3.13/3.14 where PySide6 wheels missing).
- Headless Qt: `QT_QPA_PLATFORM=offscreen`; import stubs for GUI modules.
- Docs build matrix (3.10–3.14) and deploy on 3.12 (GitHub Pages).

### Tests
- Coverage expanded to 51 tests including converters (Prusa/SuperSlicer/ideaMaker), generators (process/limits/overrides), CLI (overrides), firmware mapping/rules, GUI import smokes.

## [0.1.0] – 2025-10-28
- Initial public baseline: core schemas, CLI, basic GUI, and tests.
- Converters (import):
  - `opk convert --from prusa|superslicer` — Convert Prusa/SuperSlicer INI to OPK printer profiles.
  - `opk convert --from ideamaker` — Convert ideaMaker CFG to OPK printer profiles.
- Generators (export):
  - SuperSlicer generator added; ideaMaker mapping deepened (layers/speeds).
