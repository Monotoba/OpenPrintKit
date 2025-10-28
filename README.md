# OpenPrintKit (OPK)

Open, deterministic toolkit to define printers (PDL), generate slicer profiles (Orca first), bundle, and install.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
pytest -q
opk validate examples/printers/Longer_LK5_Pro_Marlin.json
opk bundle --in examples --out dist/LK5Pro_OrcaProfile_v1.orca_printer
