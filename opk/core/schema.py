from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict
from jsonschema import Draft202012Validator

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"

def _load(name: str) -> Dict[str, Any]:
    with open(SCHEMA_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)

PRINTER = Draft202012Validator(_load("printer.schema.json"))
FILAMENT = Draft202012Validator(_load("filament.schema.json"))
PROCESS = Draft202012Validator(_load("process.schema.json"))
BUNDLE  = Draft202012Validator(_load("bundle.schema.json"))
PDL     = Draft202012Validator(_load("pdl.schema.json"))

def validate(kind: str, obj: Dict[str, Any]) -> None:
    {"printer": PRINTER, "filament": FILAMENT, "process": PROCESS,
     "bundle": BUNDLE, "pdl": PDL}[kind].validate(obj)
