from __future__ import annotations
from pathlib import Path
from typing import Iterable

DEFAULT_DIRS: tuple[str, ...] = (
    "profiles/printers",
    "profiles/filaments",
    "profiles/processes",
    "bundles",
    "logs",
)

GITIGNORE = """# OpenPrintKit workspace
bundles/
logs/
dist/
__pycache__/
*.pyc
"""

EXAMPLE_PRINTER = {
    "type": "printer",
    "name": "Example Printer",
    "nozzle_diameter": 0.4,
    "filament_diameter": 1.75,
    "build_volume": [220, 220, 250]
}
EXAMPLE_FILAMENT = {
    "type": "filament",
    "name": "PLA Baseline - Example",
    "filament_type": "PLA",
    "nozzle_temperature": 205,
    "bed_temperature": 60
}
EXAMPLE_PROCESS = {
    "type": "process",
    "name": "Standard 0.20 mm - Example",
    "layer_height": 0.20,
    "first_layer_height": 0.28,
    "print_speed": 60,
    "travel_speed": 180,
    "wall_count": 3,
    "infill_density": 20,
    "adhesion_type": "skirt"
}

def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def _write_json(path: Path, obj: dict) -> None:
    import json
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def init_workspace(root: Path, with_examples: bool = True, extra_dirs: Iterable[str] | None = None) -> Path:
    root = Path(root)
    (root).mkdir(parents=True, exist_ok=True)
    for rel in DEFAULT_DIRS + tuple(extra_dirs or ()):
        (root / rel).mkdir(parents=True, exist_ok=True)
    gi = root / ".gitignore"
    if not gi.exists():
        _write_text(gi, GITIGNORE)

    if with_examples:
        _write_json(root / "profiles/printers/Example_Printer.json", EXAMPLE_PRINTER)
        _write_json(root / "profiles/filaments/PLA_Baseline_Example.json", EXAMPLE_FILAMENT)
        _write_json(root / "profiles/processes/Standard_0p20_Example.json", EXAMPLE_PROCESS)

    readme = root / "README.opk-workspace.md"
    if not readme.exists():
        _write_text(
            readme,
            "# OpenPrintKit Workspace\n\n"
            "- `profiles/` — JSON profiles (printer/filament/process)\n"
            "- `bundles/` — output `.orca_printer` files\n"
            "- `logs/` — local validation/build logs\n"
        )
    return root
