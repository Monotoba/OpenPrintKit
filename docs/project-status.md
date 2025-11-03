# OpenPrintKit (OPK) toolchain**

To get us back on track, I want to clarify where we left off and what “the tools” likely refer to, so we can re-enter
structured development efficiently.

---

## 🔍 Recap of Current State

We now have:

* ✅ **OpenPrintKit (OPK)** base project (schemas, CLI, tests all green)
* ✅ CI/CD with GitHub Actions (test + bundle)
* ✅ PDL subproject (`pdl-spec/`) as a reference spec & docs base
* ✅ Working slicer generators + CLI `opk gen`:
  - Orca (JSON profiles + `.orca_printer` bundle)
  - Cura (CFG) with bundling (`.zip`)
  - Prusa/SuperSlicer/Bambu (INI) with bundling (`.zip` for Prusa)
  - ideaMaker (CFG) with bundling (`.zip`)
* ✅ GUI “Generate Profiles…” dialog with preview, bundle picker, recents (out/bundle), and suffix validation

---

## 🧰 “Tools” Layer — What We Planned

Earlier, we discussed building a **Python/PySide6 GUI toolchain** to *create, edit, validate, and bundle slicer configurations* — essentially the **OpenPrintKit Tools Suite**.

This suite should manage:

1. **Profile Management**

   * Load/edit/save individual configs (`printer`, `filament`, `process`)
   * Combine them into bundles (`.orca_printer`, `.zip`, etc.)
2. **PDL Integration**

   * Load or generate from PDL
   * Validate with schema
   * Compare versions (diff, patch)
3. **Converter Utilities**

   * Convert from **Cura**, **Prusa**, or **Marlin** configs → PDL or OPK bundle
4. **Bundle Wizard**

   * Step-by-step generator for slicer profiles
   * Export, preview, install
5. **Testing / Validation Tools**

   * Validate schema compliance and rule checks
   * Compare generated vs imported profiles
6. **CLI + GUI parity**

   * All features callable via `opk` CLI **and** GUI

---

## ⚙️ Tool Architecture Overview

```text
OpenPrintKit/
├─ opk/
│  ├─ cli/                  ← CLI commands
│  ├─ core/                 ← schema, io, validation
│  ├─ gui/                  ← PySide6 app (new)
│  │   ├─ main.py
│  │   ├─ widgets/
│  │   ├─ models/
│  │   ├─ editors/
│  │   ├─ resources/
│  │   └─ themes/
│  └─ plugins/slicers/      ← Orca, Cura, Prusa emitters/converters
├─ tests/
├─ examples/
└─ requirements.txt
```

---

## 🧱 Next Steps for the Tools

| Step | Description                                                  | Deliverable                           |
|------|--------------------------------------------------------------|---------------------------------------|
| 1    | Create base **PySide6 app skeleton** with menu + dock layout | `opk/gui/main.py`                     |
| 2    | Implement **Config Editor** for Orca/PDL JSON files          | `opk/gui/editors/config_editor.py`    |
| 3    | Implement **Bundle Manager** (open/save bundles)             | `opk/gui/tools/bundle_manager.py`     |
| 4    | Integrate **Validator/Schema Test Tool**                     | reuse `opk.core.schema`               |
| 5    | Add **Cura → Orca Converter UI**                             | wraps converter logic                 |
| 6    | Add **CLI/GUI integration**                                  | menu → call same backend as `opk gen` |
| 7    | Add tests for GUI logic                                      | `pytest-qt` or mock-based tests       |

---

## 🚀 Proposed Name

Let’s call the GUI app **“OpenPrintKit Studio”** — it’s your cross-slicer, open-source configuration studio.

---

### ✅ Decision Point

Before generating code and project files, I need confirmation on **how you want to proceed**:

Do you want me to:

let's first design a **functional spec** for each tool (e.g., Bundle Manager, PDL Editor, Converter) before coding?

This will give us fine control and ensures completeness.
