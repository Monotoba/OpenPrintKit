# System Notes — Current Session

This document captures key decisions, changes, and notes from the current development session.

## Summary of Major Changes

- Schema (PDL)
  - Added `limits` (print_speed_max, travel_speed_max, acceleration_max, jerk_max).
  - Added `materials` array (embedded filament presets).
  - Added `features.probe.active_low` and top-level `endstops` polarity (active_low per axis).
  - Expanded G-code hooks with comprehensive lifecycle coverage; added `macros` and generic `hooks` map.
  - Introduced structured `machine_control` (PSU, lights/RGB, fans, chamber, camera, SD logging, exhaust, aux_outputs, custom_peripherals).
  - Allowed string pins for RRF in `exhaust.pin` and `aux_outputs[].pin`.
  - Added `open_print_tag` metadata block support.

- Core (Generators/Utils)
  - `render_hooks_with_firmware` merges `gcode` + `machine_control` and applies firmware policies.
  - Firmware policies:
    - Klipper: map camera `M240` to `M118 TIMELAPSE_TAKE_FRAME`.
    - RRF: map SD logging `M928/M29` to `M929 P"file" S1 / M929 S0`; support named pins.
    - GRBL: exhaust → `M8` (on) / `M9` (off).
    - LinuxCNC: exhaust → `M7` (on) / `M9` (off).
  - `apply_machine_control` translates structured fields into hook sequences.
  - `generate_snippets` returns start/end G-code lists (firmware-ready).
  - Slicer generators expanded (Cura/Prusa/Bambu):
    - Map `process_defaults` layer heights and speeds (perimeter/infill/travel; external_perimeter; top/bottom where supported).
    - Map `process_defaults.extrusion_multiplier` (material_flow / extrusion_multiplier).
    - Map `process_defaults.cooling` (min layer time, fan min/max/always on).
    - Map `limits` acceleration/jerk (Cura: acceleration/jerk enabled + values; Prusa/Bambu: max_print/travel acceleration).
    - Per-section accelerations via `process_defaults.accelerations_mms2` (perimeter/infill/external/top/bottom) to slicer-specific keys.
  - Added `build_profile_bundle(files, out, slicer)` to package generated profiles (Cura/Prusa/ideaMaker) with a manifest.
  - G-code renderer supports dotted/array placeholders in preview.

- CLI
  - Added: `rules`, `workspace init`, `install`, `convert --from cura`, `gcode-hooks`, `gcode-preview`, `gcode-validate`, `pdl-validate`, `tag-preview`, `gen-snippets`.
  - CLI applies firmware-aware mapping when previewing/validating hooks.
  - `gen` now supports bundling for cura/prusa/ideamaker via `--bundle OUT.zip` (Orca bundling unchanged).
  - Added fine-grained acceleration overrides (merged into `process_defaults.accelerations_mms2`): `--acc-perimeter`, `--acc-infill`, `--acc-external`, `--acc-top`, `--acc-bottom`.
  - Stabilized/deduplicated subparser registrations; fixed earlier argparse conflicts.

- GUI
  - Tabbed PDL editor with tabs: Build Area (polygon bed + limits), Extruders, Multi-Material, Filaments, Features (probe active_low + endstops), Machine Control (standard lifecycle), Peripherals (lights, RGB, chamber, camera, fans, SD, exhaust, Aux Outputs, Custom Peripherals), OpenPrintTag, Logs.
  - Build menu added (Validate, Run Rules, Build Bundle). Keyboard shortcuts and tooltips/status tips added across menus.
  - Tools: G-code Preview; Validate Hook Variables; Generate Snippets; Generate Profiles (with Preview before write).
  - Generate Profiles dialog: supports in-editor PDL (no need to save); multi-file preview; bundle summary with open-folder.
  - Help: Overview, G-code Help, M-code Reference, Firmware Mapping.
  - Settings dialog (default slicer/firmware, output dir, variables JSON, policy toggles) via QSettings.
  - Dynamic firmware tips shown in Peripherals tab; targeted tooltips added throughout (RGB/chamber/camera/fans/exhaust/materials).
  - Added Issues tab with inline rule validation (Refresh/Copy), and status bar issue counts; editor wrapped in scroll area to reduce height.
  - Improved headless import robustness: centralized PySide6 compatibility stubs; lazy-imported subdialogs.

- Rules & Validation
  - `pdl-validate` adds checks: exhaust pin vs fan ambiguity, camera triggers without command, duplicate aux pins, malformed custom_peripherals entries.
  - Firmware guidance:
    - GRBL/LinuxCNC: coolant mapping (M7/M8/M9), recommend off_at_end; raw pin ignored for exhaust.
    - Klipper: camera M240 mapping info to TIMELAPSE_TAKE_FRAME.
    - RRF: SD logging mapped to M929 with quoted filename; warn about spaces; prefer named pins; aux fan needs off_at_end.
    - Marlin: M42 requires numeric pin, warn on string pins in exhaust.
  - Process defaults sanity checks: layer heights vs nozzle, cooling fan range and min layer time, non‑negative per‑section accelerations.

- Docs
  - Added pages: Firmware Mapping, Overview, G-code Help, CLI Reference (updated with bundling and overrides), M-code Reference (expanded), System Notes, Implementation Status.
  - pdl-spec: added mkdocs site with Material theme; requirements pinned; added missing schema and getting-started docs.
  - pdl-spec: documented `process_defaults.accelerations_mms2` and extended `speeds_mms` keys.
  - README updated with Docs badge, website link, and documentation links.

- Tests
  - Expanded coverage to 46 tests: schema, bundles, CLI (including overrides), generators (process/limits/overrides), firmware mapping, OpenPrintTag, G‑code utils, GUI import smokes, firmware rules.

- CI/CD
  - CI matrix expanded to Python 3.10–3.14 on Ubuntu/Windows (exclude Windows+3.13/3.14 due to PySide6 wheels); QT_QPA_PLATFORM=offscreen.
  - Headless PySide6 import stubs and lazy imports eliminate GUI plugin issues on runners.
  - Docs workflow builds with MkDocs (3.10–3.14), deploys (3.12). Badges fixed; Pages configured to use GitHub Actions.
  - Fixed Windows shell compatibility and stabilized workflows.

## Rationale & Decisions

- Keep PDL slicer-agnostic: model high-level `machine_control` and derive G-code via generators per firmware.
- Separate common Machine Control (lifecycle) from Peripherals (vendor-/device-specific), reducing UI clutter.
- Provide firmware-aware guidance (GUI tips + mapping docs) to reduce surprises for end users.
- Use QSettings for app-level settings (simple, cross-platform). Project-level config can be added if needed.

## Notable TODOs / Future Work

- Add deeper mappings and hints for Bambu/Repetier/Smoothieware (beyond pass-through).
- Add GUI Tools → Generate Snippets… (uses Settings defaults).
- Support named pins thoroughly in UI for RRF (string input with validation).
- Add project-level settings file (`.opk-project.yml/json`) for per-project defaults (optional).
- Implement PDL→slicer generators (Orca, Cura, Prusa, Bambu): emit full profiles and bundles.
- Expand printer examples (Prusa XL, Voron variants, Bambu X1C, etc.) with matching filaments/processes.
- CI enhancements, packaging, and distribution notes.

---

## Session Timeline (2025-11-01 → 2025-11-02)

2025-11-02
- ui: Help menu shortcuts (F1/F2/F3), Restore Defaults + Help per tab, broad tooltips and status tips. [8f8636e]
- ui: Build menu introduced; moved Validate/Rules/Bundle; shortcuts for Snippets/Profiles; tooltips. [9d2c80c]
- docs(system-notes) backfilled with full session updates. [71dd84e]
 - ui: Issues tab with inline rule validation + status bar counts; scrollable editor. [54a1fad]
 - rules: firmware guidance (RRF, Marlin) and process_defaults sanity checks; tests added. [4aeda7a]

2025-11-01
- Generators: process_defaults mapping (layers/speeds), extrusion multiplier, cooling, limits; per-section accelerations; multi-file preview; bundling (Cura/Prusa/ideaMaker). [028e098, 75a358c, 17c5c1b, d50a072]
- CLI: fine-grained `--acc-*` overrides; argparse conflicts resolved. [027d134, d50a072]
- GUI: headless-safe imports; profile preview; bundle summary. [0eb2d59, d50a072]
- Docs: mkdocs setup for pdl-spec, requirements, schema/getting-started; README docs badge + website link. [cf59d28, 976843f, c5abe7d, bbac34d, 4342f1a]
- CI: expand Python matrix to 3.10–3.14 with exclusions; offscreen Qt; docs build matrix and deploy on 3.12. [2d49b73, 5fc7f99]

## Recent Commits

- 71dd84e (2025-11-02) docs(system-notes): backfill session updates (generators, CLI bundling/overrides, GUI menus/preview, docs site, CI matrix, tests)
- 8f8636e (2025-11-02) ui: Help menu shortcuts (F1/F2/F3), status tips; add Restore Defaults + Help buttons in Build Area, Machine Control, Peripherals; add more field tooltips
- 9d2c80c (2025-11-02) ui: Build menu shortcuts, status tips; add tooltips across tabs (materials, camera, fans, RGB, chamber, exhaust); shortcuts for Snippets/Profiles
- 693364d (2025-11-02) feat(GUI): richer Preview (size/modified) and bundle summary; test(CLI): verify --acc-* overrides; docs(PDL): document accelerations_mms2 and extended speeds_mms
- d50a072 (2025-11-01) feat: multi-file preview in GUI; bundle summary with open-folder; CLI gen: add fine-grained acceleration overrides; expand generator per-section mappings
- 17c5c1b (2025-11-01) feat(generators): support ext/top/bottom speeds and per-section accelerations; GUI: multi-file Preview and bundling preview; docs: mapping details
- 75a358c (2025-11-01) feat(generators): map extrusion multiplier + cooling and acceleration/jerk (Cura) and acceleration (Prusa/Bambu); GUI: add Preview in Generate Profiles; docs: update overview with mapping highlights
- 028e098 (2025-11-01) feat(generators): map process_defaults into Cura/Prusa/Bambu; add tests; ui: clarify Endstops label '(Checked = Active Low)'
- 4342f1a (2025-11-01) docs(README): add website link in Documentation section
- bbac34d (2025-11-01) docs(README): add docs badge linking to published site (GitHub Pages)
- c5abe7d (2025-11-01) docs(pages): remove deploy continue-on-error; set mkdocs site_url/repo_url to Monotoba/OpenPrintKit
- 027d134 (2025-11-01) fix(cli): remove duplicate gcode/PDL subparser registrations causing argparse conflicts
- ddadeb1 (2025-11-01) ci(headless): use Qt compat layer in preferences/app settings dialogs; lazy-import these in main_window to avoid headless import failures
- 85d6efa (2025-11-01) ci: make UI subdialog imports lazy in main_window; add workspace init fallback to support 3.10 source runs
- 0eb2d59 (2025-11-01) ci(headless): centralize PySide6 stubs (_qt_compat) and use in UI modules; fix workspace init import; make docs deploy non-blocking if Pages disabled
- 5fc7f99 (2025-11-01) docs(ci): add Python version matrix (3.10–3.14) to docs build; deploy only on 3.12
- 976843f (2025-11-01) docs(pdl-spec): add mkdocs requirements and missing docs files (schema/, getting-started.md); fix nav targets
- cf59d28 (2025-11-01) docs(ci): fix docs build by adding mkdocs dependencies and schema path; pin docs workflow to Python 3.12
- 2d49b73 (2025-11-01) ci: expand matrix to Python 3.10–3.14; use source-run deps for edge versions; set PYTHONPATH for module runs; keep Qt offscreen
- 7bfa8d9 (2025-11-01) ci(headless): add Qt import stubs in main_window to allow import-only tests without Qt plugins; stabilizes CI on headless runners
