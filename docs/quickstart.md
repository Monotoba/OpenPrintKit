# OpenPrintKit Quickstart

This guide gets you running the OPK CLI locally to validate profiles, run rule checks, bundle for OrcaSlicer, and scaffold a workspace.

## 1) Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 2) Validate Example Profiles

```bash
opk validate examples/printers/Longer_LK5_Pro_Marlin.json \
             examples/filaments/PLA_Baseline_LK5Pro.json \
             examples/processes/Standard_0p20_LK5Pro.json
```

## 3) Run Rule Checks

Rule checks add heuristics beyond schema validation.

```bash
opk rules \
  --printer  examples/printers/Longer_LK5_Pro_Marlin.json \
  --filament examples/filaments/PLA_Baseline_LK5Pro.json \
  --process  examples/processes/Standard_0p20_LK5Pro.json
```

Exit codes: 0 on success (no errors), 2 if any error-level issues are found.

## 4) Build an Orca Bundle

```bash
mkdir -p dist
opk bundle --in examples --out dist/LK5Pro_OrcaProfile_v1.orca_printer
```

Output is a `.orca_printer` ZIP containing `printers/`, `filaments/`, `processes/`, and `manifest.json`.

## 5) Initialize a Workspace

```bash
opk workspace init ./my-workspace        # includes example profiles by default
# or
opk workspace init ./my-workspace --no-examples

tree -a ./my-workspace || ls -R ./my-workspace
```

Workspace layout:

```
my-workspace/
  profiles/{printers,filaments,processes}
  bundles/
  logs/
  README.opk-workspace.md
```

## 6) Run Tests (optional)

```bash
PYTHONPATH=. pytest -q
```

## Troubleshooting

- If `pytest` can’t import `opk`, prepend `PYTHONPATH=.` as shown above.
- If `opk` is not found, ensure your virtual environment is active and `pip install -e .` completed successfully.

## GUI (Optional)

Launch the desktop app:

```bash
opk-gui
```

Available from the menu:

- Validate JSON files against schema
- Run rule checks
- Build Orca bundle
- Initialize a workspace
- Set default Orca presets path in Preferences
- Drag-and-drop `.json` files onto the window to validate
- Tools → G-code Preview: pick a hook and render with `pdl-spec/examples/vars.sample.json`
- Tools → Validate Hook Variables: scan all hooks for unresolved placeholders

## CLI Install to Orca Presets (Optional)

Dry-run a plan and then install with backup:

```bash
opk install --src ./examples --dest ~/AppData/Roaming/OrcaSlicer/user/  --dry-run   # Windows example path
opk install --src ./examples --dest ~/.config/OrcaSlicer/user/ --backup ./backup_orca.zip
```

Note: Destination path varies by OS and Orca version. Use a dry run first to see planned changes.

## G-code Helpers (Optional)

```bash
# List hooks in a PDL
opk gcode-hooks --pdl pdl-spec/examples/prusa_mk3s.yaml

# Render a hook with variables
opk gcode-preview --pdl pdl-spec/examples/prusa_mk3s.yaml --hook start --vars pdl-spec/examples/vars.sample.json

# Validate all hooks for unresolved placeholders
opk gcode-validate --pdl pdl-spec/examples/voron_24_350.yaml --vars pdl-spec/examples/vars.sample.json

## PDL Validation (Schema + Rules)

```bash
opk pdl-validate --pdl pdl-spec/examples/prusa_mk3s.yaml
```
Checks PDL schema and machine_control rules (e.g., ambiguous exhaust config, duplicate aux pins, missing camera command when triggers enabled).
```
