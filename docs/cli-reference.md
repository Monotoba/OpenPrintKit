# OPK CLI Reference

Commands:

- `opk validate {paths...}` — Schema validation for JSON profiles.
- `opk bundle --in SRC --out OUT.orca_printer` — Build Orca bundle from `printers/`, `filaments/`, `processes/`.
- `opk rules [--printer P] [--filament F] [--process S]` — Run rule checks (warnings/errors) with summary.
- `opk workspace init ROOT [--no-examples]` — Scaffold a standard workspace.
- `opk install --src SRC --dest ORCA_PRESET_DIR [--backup BACKUP.zip] [--dry-run]` — Dry‑run and install profiles to Orca presets.
- `opk convert --from cura --in CURA_FILE_OR_DIR --out OUT_DIR` — Convert Cura definitions to OPK printers.
- `opk gcode-hooks --pdl PDL.yaml` — List G‑code hooks in a PDL (after applying machine_control and firmware mapping).
- `opk gcode-preview --pdl PDL.yaml --hook start --vars vars.json` — Render a hook with provided variables.
- `opk gcode-validate --pdl PDL.yaml --vars vars.json` — Validate all hooks for unresolved placeholders.
- `opk pdl-validate --pdl PDL.yaml` — Validate PDL schema and machine_control rules.
- `opk tag-preview --pdl PDL.yaml` — Print the OpenPrintTag block that is injected at start.
- `opk gen-snippets --pdl PDL.yaml --out-dir OUT [--firmware FW]` — Generate firmware-ready `*_start.gcode` and `*_end.gcode` files.
- `opk gen --pdl PDL.yaml --slicer orca --out OUTDIR [--bundle OUT.orca_printer]` — Generate OPK profiles for Orca bundling.
- `opk gen --pdl PDL.yaml --slicer cura --out OUTDIR` — Generate a minimal Cura `.cfg` profile.
- `opk gen --pdl PDL.yaml --slicer prusa --out OUTDIR` — Generate a minimal Prusa `.ini` profile.
- `opk gen --pdl PDL.yaml --slicer ideamaker --out OUTDIR` — Generate a minimal ideaMaker `.cfg` profile.
- `opk gen --pdl PDL.yaml --slicer bambu --out OUTDIR` — Generate a minimal Bambu Studio `.ini`-style profile.

### Advanced Overrides

- `opk gen ... [--bundle OUT.zip]` — For cura/prusa/ideamaker, bundles generated files with a manifest (use `.zip`).
- Acceleration overrides (merged into `process_defaults.accelerations_mms2`):
  - `--acc-perimeter N` — perimeter acceleration (mm/s²)
  - `--acc-infill N` — infill acceleration (mm/s²)
  - `--acc-external N` — external perimeter acceleration (mm/s²)
  - `--acc-top N` — top solid infill acceleration (mm/s²)
  - `--acc-bottom N` — bottom solid infill acceleration (mm/s²)

See also: `docs/overview.md`, `docs/gcode-help.md`, `docs/firmware-mapping.md`.
