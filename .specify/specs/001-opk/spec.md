# Spec — OpenPrintKit (OPK)
Goal: Load/edit/validate PDL + generate slicer configs (Orca/Prusa-family first), bundle, and install.

MVP:
- PDL schema + loader → normalized IR
- Orca generator (printer/filament/process JSON) + `.orca_printer` bundler
- CLI: `opk validate|bundle|pdl-validate|gen`
- PySide6 GUI shell with validation
- Tests: schema pass; bundle round-trip
