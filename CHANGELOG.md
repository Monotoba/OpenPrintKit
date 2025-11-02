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
  - GUI polish: persist last-used paths and better UX
    - Generate Profiles remembers slicer, output dir, optional PDL path, and bundle settings via QSettings (`gen_profiles/*`).
    - Auto-suggest bundle filenames when none provided (Orca → `.orca_printer`, others → `.zip`), adding suffixes if missing.
    - Enable bundle path only for supported slicers (orca/cura/prusa/ideamaker) and reflect that in the placeholder.
    - Generate Snippets remembers PDL and output dir (`gen_snippets/*`) and uses app defaults as fallback.
    - G-code Preview/Validate remember last PDL/vars and (Preview) last hook selection (`gcode_preview/*`, `gcode_validate/*`).
    - Add bundle “Browse…” button in Generate Profiles.
    - Build Bundle now remembers last bundle save path (`paths/last_bundle`).
- Rules:
  - Firmware guidance: GRBL/LinuxCNC coolant mapping (M7/M8/M9), Klipper camera mapping info, RRF SD logging mapping/filename spacing and named pin suggestion, Marlin numeric pin requirement.
  - Sanity checks for process_defaults (layer heights vs nozzle, cooling fan percent range and min layer time, non‑negative per‑section accelerations).
- Docs:
  - MkDocs site for pdl‑spec; docs added/updated (Overview, Firmware Mapping, G‑code Help, CLI Reference).
  - README badges and links (Build, Docs website).
  - Slicer Support Matrix page; CLI reference updated with new converters and slicing.
  - Converters (import): `opk convert --from prusa|superslicer|ideamaker|kisslicer`.
  - Generators (export): SuperSlicer and KISSlicer (best‑effort) added.
  - CLI slicing: `opk slice --slicer slic3r|prusaslicer|superslicer|curaengine ...`.

### Changed
- CLI: stabilized parser; removed duplicate subparser definitions.
- GUI: lazy‑import subdialogs; centralized PySide6 compat stubs for headless CI.
  - Clearer error messages in dialogs (include PDL filename on read errors; include slicer in generation/preview errors; clarify valid PDL extensions).

### CI
- Matrix: Python 3.10–3.14 (Windows exclusions for 3.13/3.14 where PySide6 wheels missing).
- Headless Qt: `QT_QPA_PLATFORM=offscreen`; import stubs for GUI modules.
- Docs build matrix (3.10–3.14) and deploy on 3.12 (GitHub Pages).

### Tests
- Coverage expanded to 51 tests including converters (Prusa/SuperSlicer/ideaMaker), generators (process/limits/overrides), CLI (overrides), firmware mapping/rules, GUI import smokes.

## [0.1.0] – 2025-10-28
- Initial public baseline: core schemas, CLI, basic GUI, and tests.
