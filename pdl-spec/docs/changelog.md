# Changelog

This is a copy of the project changelog for convenience in the docs site.

For the canonical, always up‑to‑date version, see the repository root: CHANGELOG.md

## Unreleased

- Generators (Cura/Prusa/Bambu): extended mappings from `process_defaults` (layers, speeds, extrusion multiplier, cooling) and `limits` (acceleration/jerk); per‑section accelerations.
- Bundlers: added `build_profile_bundle` for cura/prusa/ideamaker.
- CLI: `gen --bundle` for non‑Orca; fine‑grained `--acc-*` overrides merged into `process_defaults.accelerations_mms2`.
- GUI: Build menu with shortcuts; Generate Profiles with Preview and bundle summary; in‑editor PDL support.
- Docs: MkDocs site for pdl‑spec; updated CLI and mapping docs; README badges/links.
- CI: matrix for Python 3.10–3.14 (Windows exclusions); offscreen Qt; docs matrix + deploy.
- Tests: expanded to 42 tests including generators and CLI overrides.

