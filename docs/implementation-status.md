# Implementation Status

This document tracks major features, their implementation status, and next steps.

## Feature Matrix

- PDL Schema
  - [x] Core profiles (printer/filament/process) via JSON Schema
  - [x] Limits (speed/accel/jerk)
  - [x] Materials (embedded filament presets)
  - [x] Features → probe.active_low and endstops polarity
  - [x] Comprehensive G-code hooks + macros + generic hooks map
  - [x] Structured machine_control (PSU, lights/RGB, fans, chamber, camera, SD logging, exhaust, aux_outputs, custom_peripherals)
  - [x] OpenPrintTag metadata
  - [x] RRF-friendly string pins for outputs

- Core/Generators
  - [x] Render hooks with machine_control
  - [x] Firmware policies (Marlin/RRF/Klipper/GRBL/LinuxCNC)
  - [x] OpenPrintTag injection
  - [x] Generate start/end snippets
  - [x] Slicer-specific generators (initial mappings): Orca, Cura, Prusa, Bambu, SuperSlicer, ideaMaker, KISSlicer

- CLI
  - [x] validate, rules, bundle, install, convert(cura)
  - [x] gcode-hooks, gcode-preview, gcode-validate
  - [x] pdl-validate (schema + rules)
  - [x] tag-preview
  - [x] gen-snippets
  - [x] gen (PDL→slicer profiles) with optional bundle output for orca/cura/prusa/ideamaker and acceleration overrides

- GUI
  - [x] Tabbed PDL editor (Build Area/Extruders/Multi-Material/Filaments/Features/Machine Control/Peripherals/OpenPrintTag)
  - [x] Polygon bed editor + limits group
  - [x] Peripherals: lights, camera, fans, SD, exhaust, aux outputs
  - [x] Custom Peripherals list (Add/Remove) with dynamic hook selector
  - [x] G-code tools (Preview, Validate)
  - [x] Settings dialog (defaults + policies)
  - [x] Help pages (Overview, G-code Help, Firmware Mapping, M-code Reference)
  - [x] Tools → Generate Snippets… (invoke CLI core with defaults)
  - [x] Generate Profiles dialog persistence (slicer/out dir/PDL/bundle) and bundle UX improvements
  - [x] Issues tab: Level and Path filters (machine_control, process_defaults, gcode)
  - [x] Rules dialog: Path and text filters
  - [x] Inline hints near camera triggers, exhaust conflicts, aux outputs
  - [ ] Project-level config management (optional)

- Rules & Validation
  - [x] Basic rules for machine_control consistency
  - [x] Expanded rules per firmware (initial set; add more per-target nuance over time)

- Docs
  - [x] Firmware Mapping, Overview, G-code Help, CLI Reference, M-code Reference
  - [x] System Notes (this session) and Implementation Status
  - [x] Translations: Spanish, French, German, Portuguese (manuals + CLI/Overview)
  - [x] Exact generator keys automation (`scripts/extract_generator_keys.py`) and CI check
  - [ ] Slicer generator documentation (once implemented)

## Achievements

- Established robust schema for PDL including lifecycle hooks, machine control, and metadata.
- Built GUI editor with comprehensive tabs and contextual firmware tips.
- Added firmware-aware generation policies and CLI tools to preview/validate and produce snippets.
- Implemented working slicer generators (Orca, Cura, Prusa, Bambu, SuperSlicer, ideaMaker, KISSlicer) and CLI `gen` with bundling support (where applicable).
- Documented the system (firmware mapping, G-code usage, CLI reference) and integrated help into GUI.
- Ensured changes are tested and committed incrementally.

## Next Steps

1. Refine PDL→slicer mappings
   - Expand coverage of advanced settings per slicer; align with evolving PDL fields.
   - Add normalization or version notes where slicer formats diverge.

2. Extend firmware mappings
   - Bambu and Repetier/Smoothie nuanced behaviors.
   - GUI tips reflecting those nuances.

3. GUI Enhancements
  - Tools → Generate Snippets… action using Settings.
  - Optional project-level config files for per-project defaults.
  - Process Defaults editor tab with inline hints (layer heights, speeds, cooling)

4. Validation & Rules
   - Expand rule checks for more firmware-specific guidance.
   - Lint common pitfalls (e.g., mismatched nozzle/filament diameters).

5. Packaging & Distribution
  - CLI/GUI packaging guidance, CI workflows, and release notes.
  - Pre-commit config and lint workflow (ruff + black) in CI.
