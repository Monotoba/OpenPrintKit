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
  - Improved headless import robustness: centralized PySide6 compatibility stubs; lazy-imported subdialogs.

- Rules & Validation
  - `pdl-validate` adds checks: exhaust pin vs fan ambiguity, camera triggers without command, duplicate aux pins, malformed custom_peripherals entries.

- Docs
  - Added pages: Firmware Mapping, Overview, G-code Help, CLI Reference (updated with bundling and overrides), M-code Reference (expanded), System Notes, Implementation Status.
  - pdl-spec: added mkdocs site with Material theme; requirements pinned; added missing schema and getting-started docs.
  - pdl-spec: documented `process_defaults.accelerations_mms2` and extended `speeds_mms` keys.
  - README updated with Docs badge, website link, and documentation links.

- Tests
  - Expanded coverage to 42 tests: schema, bundles, CLI, generators (process/limits/overrides), firmware mapping, OpenPrintTag, G-code utils, GUI import smokes.

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
