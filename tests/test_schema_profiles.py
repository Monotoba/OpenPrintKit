from pathlib import Path
import json
from opk.core import schema as S

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "examples"

def load(rel): return json.loads((EX/rel).read_text())

def test_printer_valid():  S.validate("printer", load("printers/Longer_LK5_Pro_Marlin.json"))
def test_filament_valid(): S.validate("filament", load("filaments/PLA_Baseline_LK5Pro.json"))
def test_process_valid():  S.validate("process", load("processes/Standard_0p20_LK5Pro.json"))
