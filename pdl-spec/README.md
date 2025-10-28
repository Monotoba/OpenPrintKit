# 🧩 Printer Definition Language (PDL)

**PDL** is an open, slicer-agnostic format that defines 3D printers, materials, and processes
in a structured, human-readable way.

This project is currently developed as part of [OpenPrintKit (OPK)](../README.md),
and will be extracted into its own repository once the core specification stabilizes.

---

## 📖 Purpose

PDL describes:

- Geometry, limits, and firmware of 3D printers
- Extruder and filament characteristics
- Default process parameters (layer height, speed, retraction)
- Standard G-code sequences (start/end)
- Material temperature and speed envelopes

PDL enables **deterministic, reproducible slicing** across different slicers
(Orca, Cura, Prusa, etc.) and acts as the canonical data source for OPK’s generators.

---

## 📘 Docs

See [`docs/PDL_SPEC.md`](docs/PDL_SPEC.md) for the formal specification.

---

## 🛠️ Dev Notes

To validate a PDL file:

```bash
python -m jsonschema -i examples/full_lk5pro.yaml schemas/pdl.schema.json
````

Or use the OPK CLI once installed:

```bash
opk pdl-validate opk/pdl/registry/longer/lk5pro.yaml
```

---

## 🪶 License

Released under the MIT License © 2025 The OpenPrintKit Contributors.


---

## 4. Versioning

PDL follows **Semantic Versioning (SemVer)**:

* Increment **MAJOR** when breaking schema changes occur.
* Increment **MINOR** when fields are added.
* Increment **PATCH** for typo or clarifications.

---

## 5. License

Licensed under MIT (see `../LICENSE`).


---

## 🌐 6. Later: Split it out cleanly

When you’re ready to publish as a standalone project:
```bash
git subtree split --prefix=pdl-spec -b pdl-spec-branch
git push origin pdl-spec-branch:pdl
```

To create a new GitHub repo (e.g. **PrinterDefinitionLanguage** or **PDL-Spec**) and push that branch.

---

## ✅ Summary

We now have:

* A **subproject** `pdl-spec/` within OpenPrintKit
* `.gitignore` exclusions for its build artifacts
* README + spec skeleton + schema
* Ready path to **split it** into its own repo + GitHub Pages docs

---
