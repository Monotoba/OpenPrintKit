# OPK CLI Reference

Commands:

- `opk validate {paths...}` — Schema validation for JSON profiles.
- `opk bundle --in SRC --out OUT.orca_printer` — Build Orca bundle from `printers/`, `filaments/`, `processes/`.
- `opk rules [--printer P] [--filament F] [--process S]` — Run rule checks (warnings/errors) with summary.
- `opk workspace init ROOT [--no-examples]` — Scaffold a standard workspace.
- `opk install --src SRC --dest ORCA_PRESET_DIR [--backup BACKUP.zip] [--dry-run]` — Dry‑run and install profiles to Orca presets.
- `opk convert --from cura --in CURA_FILE_OR_DIR --out OUT_DIR` — Convert Cura definitions to OPK printers.
- `opk convert --from prusa --in INPUT.ini --out OUT_DIR` — Convert PrusaSlicer INI to OPK printer profile(s).
- `opk convert --from superslicer --in INPUT.ini --out OUT_DIR` — Convert SuperSlicer INI to OPK printer profile(s).
- `opk convert --from ideamaker --in INPUT.cfg --out OUT_DIR` — Convert ideaMaker CFG to OPK printer profile(s).
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
- `opk gen --pdl PDL.yaml --slicer superslicer --out OUTDIR` — Generate a minimal SuperSlicer `.ini` profile.
- `opk gen --pdl PDL.yaml --slicer kisslicer --out OUTDIR` — Generate a minimal KISSlicer `.ini` profile (best‑effort).

### Spool databases

- `opk spool --source spoolman|tigertag|openspool|opentag3d --base-url URL --action create|read|update|delete|search` — Basic CRUD/search against spool databases.
  - Common flags:
    - `--api-key TOKEN` — Optional API key.
    - `--id ID` — Item ID for read/update/delete.
    - `--payload JSON` — JSON payload for create/update.
    - `--query Q` — Search term.
    - `--page N` and `--page-size N` — Pagination hints for search.
    - `--format items|normalized` — List of items or normalized envelope including `total`, `count`, `page`, `page_size`.
    - `--endpoints-file FILE.json` — Per‑source endpoint overrides as JSON.
    - `--endpoints-json JSON` — Inline JSON overrides (takes precedence over file).
  - Output format:
    - `--format items` (default): prints raw items/dicts, and `[OK] delete=True/False` for delete.
    - `--format normalized`: envelopes the output uniformly:
      - create: `{ "source", "action": "create", "item": {...} }`
      - read: `{ "source", "action": "read", "id", "item": {...} }`
      - update: `{ "source", "action": "update", "id", "item": {...} }`
      - delete: `{ "source", "action": "delete", "id", "ok": true }`
      - search: `{ "source", "query", "page", "page_size", "items", "count", "total" }`
  - Retry policy: HTTP operations retry on 408/429/5xx up to the system preference “Network retry limit” (default 5). Override via env `OPK_NET_RETRY_LIMIT` or App Settings.
  - Backoff & jitter:
    - Base backoff seconds: QSettings `net/retry_backoff` (default 0.5s), env `OPK_NET_RETRY_BACKOFF`.
    - Jitter seconds: QSettings `net/retry_jitter` (default 0.25s), env `OPK_NET_RETRY_JITTER`.
    - Sleep between retries = `backoff * (2^attempt)` + `rand(0, jitter)`.

### Advanced Overrides

- `opk gen ... [--bundle OUT.zip]` — For cura/prusa/ideamaker, bundles generated files with a manifest (use `.zip`).
- Acceleration overrides (merged into `process_defaults.accelerations_mms2`):
  - `--acc-perimeter N` — perimeter acceleration (mm/s²)
  - `--acc-infill N` — infill acceleration (mm/s²)
  - `--acc-external N` — external perimeter acceleration (mm/s²)
  - `--acc-top N` — top solid infill acceleration (mm/s²)
  - `--acc-bottom N` — bottom solid infill acceleration (mm/s²)

See also: `docs/overview.md`, `docs/gcode-help.md`, `docs/firmware-mapping.md`.
- `opk slice --slicer slic3r|prusaslicer|superslicer|curaengine --model MODEL.stl --profile PROFILE.ini --out OUT.gcode [--flags "..."]` — Slice via external CLI (binary must be on PATH; CuraEngine requires `--flags` with `-j` and settings).

## GUI Tips

- Persistence: Dialogs remember last-used fields via QSettings.
  - Generate Profiles: slicer, output directory, PDL path (when used), bundle enabled/path (`gen_profiles/*`).
  - Generate Snippets: PDL path and output directory (`gen_snippets/*`).
  - Build Bundle: last saved bundle path (`paths/last_bundle`).
- Recents & templates:
  - Generate Profiles: recent output directories and recent bundle outputs (Settings → Recent files limit; clear in Tools or Preferences).
  - G-code Preview/Validate: recent PDL/Vars dropdowns and Clear; optional Variables Templates JSON in Settings.
- Keyboard shortcuts (G-code dialogs):
  - Preview: Ctrl+O (Open PDL), Ctrl+L (Load Vars), Ctrl+S (Save Vars As…), Ctrl+T (Insert Template…), Ctrl+R (Render).
  - Validate: Ctrl+O (Open PDL), Ctrl+L (Open Vars), Ctrl+T (Template…), Ctrl+V (Validate).
- Bundling from Generate Profiles:
  - Supported slicers: Orca, Cura, Prusa, ideaMaker.
  - If bundle path is empty, a sensible filename is suggested; required suffix is auto-added (`.orca_printer` for Orca; `.zip` otherwise).
  - Use the bundle “…” button to set the path explicitly.
