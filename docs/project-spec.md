# OpenPrintKit Studio — Functional Spec (v1)

## Scope

A desktop + CLI toolchain for creating, validating, converting, diffing, bundling, and installing 3D printer profiles. Canonical data source is **PDL** (Printer Definition Language). Slicers supported initially: **OrcaSlicer** (emit and bundle). Cura/Prusa planned.
Eventually, an industry-wide Open Definition Language for defining 3D Printers, Filament, processes, etc. and a toolset to all the easy generation of definition files containing the properties of the target printer.

This project makes use of universal intermediate languages:

- PDL (Printer Definition Language)
- FDL (Filament Definition Language)

These languages allow users and manufacturers to create and share definition files. This project is a toolset for creating, and bundling these files
into slicer specific formats.

---

## Global Non-Functional Requirements

* **Deterministic**: same inputs → same outputs (bundle hashing + stable sort).
* **Validation-first**: schema + rules gate every write/bundle/install.
* **Testable**: unit tests + golden tests; GUI logic separable from UI (MVVM).
* **CLI/GUI parity**: all GUI actions wrap CLI-exposed functions.
* **Cross-platform**: Win/Linux; macOS best-effort.
* **No network**: local-first; future updates opt-in.
* **Secure by default**: never execute code from profiles; sanitize paths.
* **Performance**: typical operations <200 ms; large bundles <2 s.

---

## A. Workspace & Project Model

### Goals

Single folder “Workspace” containing sources (PDL, profiles) and outputs (generated configs, bundles).

### User Stories

* As a user, I can **open a workspace** (existing folder) or **init** a new one with standard subfolders.
* As a user, I can **track changes** and see a status panel (dirty files, validation state).
* As a user, I can **configure paths** (Orca preset directories).

### Data Model

```
workspace/
  pdl/registry/<vendor>/<model>.yaml
  profiles/
    printers/*.json
    filaments/*.json
    processes/*.json
  bundles/*.orca_printer
  logs/*.jsonl
  settings.json  # GUI state, paths (per-machine), not committed
```

### Acceptance Criteria

* Initialization scaffolds folders and `.gitignore` entries.
* “Status” shows counts: valid/invalid files; last bundle hash/date.

---

## B. Editors

### B1. PDL Editor

* **Purpose**: Edit `.yaml` PDL with schema + rule validation and live diagnostics.

**Features**

* YAML editor with schema autocompletion (optional), side diagnostics.
* Form view for common fields (geometry, extruder, materials).
* Validate button (schema + rules) → issues panel with line/field refs.
* Save guarded by “no errors” (warnings allowed).

**Acceptance**

* Invalid PDL highlights exact fields; cannot save invalid unless “force” with reason (logged).

**Edge Cases**

* Non-simple polygons for `bed_shape` → rule warning.
* Missing `pdl_version` → schema error.

### B2. Orca Profile Editors (Printer/Filament/Process JSON)

* **Purpose**: Edit native profile JSONs.

**Features**

* Form + JSON side-by-side; sync edits.
* Constraints (e.g., `layer_height ≤ 0.8 × nozzle`) raise rule warnings.

**Acceptance**

* On save, schema validation passes (specific to type).
* Diff view available against last committed version or file on disk.

---

## C. Validators

### C1. Schema Validator

* Select file(s) → Validate against appropriate JSON Schema.
* Batch mode: entire workspace.

### C2. Rules Validator

* Run rules: nozzle/layer, temps ranges per material, adhesion types, retraction vs extruder type, ABL/G-code consistency.

**Acceptance**

* Produces structured report (JSON) with severity (error/warn/info), path, message.

---

## D. Converters

### D1. Cura → Orca Converter

* **Input**: Cura INI/JSON/3MF fragments.
* **Output**: OPK process/filament/printer JSON approximations.
* **Mapping**: YAML-driven transforms + Python code hooks.

**UI**

* File picker; show mapping coverage %; diagnostics panel for unmapped keys; “Open mapping YAML” button for edits.

**Acceptance**

* Produces valid process JSON (schema pass) or fails with actionable diagnostics.
* Logs unmapped keys with suggestions.

**Edge Cases**

* Conflicting Cura settings (e.g., multiple vendor overrides) → warning; choose precedence per policy.

### D2. PDL → Orca Generator

* **Input**: PDL file.
* **Output**: `/profiles/{printers,filaments,processes}` + bundle.

**Acceptance**

* Generated files validate (schema pass).
* Bundle hash remains stable given same inputs.

---

## E. Bundling

### Bundle Manager

* Select source directory → build `.orca_printer`.
* Manifest generated (counts, timestamp, tool version, checksum).

**Acceptance**

* Bundle contains `printers/`, `filaments/`, `processes/`, `manifest.json`.
* Schema pass for manifest; explicit plural→singular mapping (tested).

**Edge Cases**

* Empty category → error with remediation hint.

---

## F. Install Wizard

### Scope

Install generated profiles to Orca user presets (with **backup** and **dry-run**).

**Features**

* Detect Orca preset path (configurable).
* Dry-run diff (added/updated/unchanged).
* One-click backup (timestamped ZIP) + install.

**Acceptance**

* Dry-run shows file list + diffs.
* Install writes files; backup path retained; rollback option reverts.

**Edge Cases**

* Permission denied → clear message and instructions.

---

## G. Matrix & Templates

### G1. Matrix Generators

* Generate **speed** and **temperature** variants from a base process/filament.

**UI**

* Input base file; list of speeds/temps; output directory.

**Acceptance**

* N variants created; all validate; names normalized.

### G2. Templates

* Create from wizard: minimal PDL, printer/filament/process skeletons.

---

## H. Diff & Compare

**Features**

* JSON structural diff (ignore ordering).
* Side-by-side display; copy chunk to right/left; export patch.

**Acceptance**

* Works for any profile types and PDL files; whitespace-insensitive.

---

## I. Telemetry & Logging (Local Only)

* **Local audit log** (`logs/actions.jsonl`): action, inputs, outputs, durations, errors.
* No network; optional anonymized metrics toggle (default OFF).

---

## J. CLI Parity

| GUI Action          | CLI Command                                                                                                                       |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Validate files      | `opk validate {paths...}`                                                                                                         |
| Bundle              | `opk bundle --in SRC --out OUT.orca_printer`                                                                                      |
| PDL validate        | `opk pdl-validate {pdl.yaml ...}`                                                                                                 |
| Generate from PDL   | `opk gen --pdl FILE --slicer orca --out DIR`                                                                                      |
| Matrix speed/temp   | `opk matrix-speed --base BASE.json --speeds 40,50 --out OUTDIR`<br>`opk matrix-temp --base FIL.json --temps 195,200 --out OUTDIR` |
| Cura → Orca convert | `opk convert --from cura --in CURA_FILE --out DIR`                                                                                |
| Install             | `opk install --src DIR --dest ORCA_PRESET_DIR --backup BACKUP.zip --dry-run`                                                      |

---

### CLI Usage Examples

```bash
# Validate individual profiles
opk validate examples/printers/Longer_LK5_Pro_Marlin.json \
             examples/filaments/PLA_Baseline_LK5Pro.json \
             examples/processes/Standard_0p20_LK5Pro.json

# Run rule-based checks (heuristics beyond schema)
opk rules \
  --printer  examples/printers/Longer_LK5_Pro_Marlin.json \
  --filament examples/filaments/PLA_Baseline_LK5Pro.json \
  --process  examples/processes/Standard_0p20_LK5Pro.json

# Build an Orca bundle
opk bundle --in examples --out dist/LK5Pro_OrcaProfile_v1.orca_printer

# Initialize a workspace (with examples by default)
opk workspace init ./my-workspace

# Install to Orca presets (dry-run and backup)
opk install --src ./examples --dest ~/.config/OrcaSlicer/user/ --dry-run
opk install --src ./examples --dest ~/.config/OrcaSlicer/user/ --backup ./backup_orca.zip
```

## K. UX Flows (Happy Paths)

### Generate from PDL, bundle, install

1. Open PDL in Editor → Validate (green).
2. **Generate** (Orca) → Profiles folder created.
3. **Bundle** → `.orca_printer` produced.
4. **Install** → dry-run diff → backup → install.
5. Confirm message with next steps.

### Convert Cura → Profiles → Bundle

1. Pick Cura file(s) → Convert (shows coverage).
2. Review/adjust fields in Process Editor.
3. Validate → Bundle → Install.

---

## L. File Formats & Contracts

* **PDL**: YAML/JSON; schema `pdl.schema.json`; SemVer field `pdl_version`.
* **Profiles**: JSON; types `printer|filament|process`; strict schemas.
* **Bundle**: ZIP `.orca_printer` with `manifest.json`.
* **Logs**: `.jsonl` NDJSON.

---

## M. Error Handling (Examples)

* Schema error → modal with first N issues + link to full report.
* Rules warning → non-blocking banner; save allowed.
* Bundle failure (empty category) → blocking error with “Open source dir” action.
* Install permission error → suggest “Run as admin” or change destination.

---

## N. Security

* Never execute profile content.
* Sanitize file names (no `..`, no absolute paths).
* No network unless user explicitly enables in settings (future).
* Backups do not include secrets; only profile data.

---

## O. Testing Strategy

### Unit

* Schema validators (positive/negative).
* Rules (nozzle/layer, temps, adhesion).
* Converters (fixtures + expected dict subsets).
* Bundle builder (stable contents + manifest).

### Integration

* PDL → IR → Orca emitter → schema pass.
* CLI round-trips (validate, gen, bundle).
* Install dry-run vs actual install (temp dir).

### GUI

* Model tests decoupled from widgets.
* Smoke tests for actions (pytest-qt optional, but can mock event handling).

### Golden Tests

* Known inputs → expected outputs checksummed (allowlist of key paths).

---

## P. Extensibility

* Plugin interfaces:

  * `opk.plugins.slicers.<name>.gen.py` → emitters
  * `opk.plugins.converters.<name>.py` → importers
* Mapping files for converters (YAML) loaded at runtime.
* Rule engine accepts custom rule modules via entry points (future).

---

## Q. Performance Targets

* Validate PDL <100 ms typical.
* Convert Cura profile <500 ms.
* Bundle build <2 s with ≤100 files.

---

## R. Packaging & Distribution

* `pipx` compatible CLI.
* Optional `PyInstaller` mode for a single-file GUI app (later).
* Wheel includes **no** GUI resources unless requested (keep size down).

---

## S. Milestones & Git Discipline

**M1 (1–2 days):**

* Workspace scaffolding, validators (schema + rules), CLI parity for validate/bundle.
* Tests: schema, bundle, rules.

**M2 (2–3 days):**

* PDL editor (text + diagnostics), generator (Orca), GUI shell.
* Tests: PDL→IR→Orca integration.

**M3 (2–3 days):**

* Cura→Orca converter (core mappings), matrix tools, install wizard (dry-run + backup).
* Tests: converter fixtures, install round-trip.

**Commits**: granular, conventional commits (`feat:`, `fix:`, `test:`, `docs:`).
**PRs**: include tests and README updates.

---

## T. Acceptance Checklist (Exit Criteria v1.0)

* CLI: `validate`, `pdl-validate`, `gen --slicer orca`, `bundle`, `matrix-*`, `install`, `convert --from cura`.
* GUI: PDL editor (validate), profile editor, generator, bundle, install, converter, matrix tools, diff.
* Tests: ≥90% of core paths; all green in CI.
* Docs: README, quickstart, tool help, troubleshooting.

---

### Ready to Build?

If this spec meets your expectations, I’ll generate:

* the **GUI skeleton** (menus, tool registry, dockable panels),
* stubs for each tool module with TODOs and test scaffolds, and
* initial fixtures for converters, rules, and golden tests.

Just say “go build M1,” and I’ll output the code scaffolding and tests for Milestone 1.
