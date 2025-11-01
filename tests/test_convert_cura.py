from pathlib import Path
import json
from opk.core import schema as S
from opk.plugins.converters.cura import convert_cura_definition


def test_convert_cura_minimal(tmp_path: Path):
    cura = {
        "name": "Sample Printer",
        "overrides": {
            "machine_width": {"value": 235},
            "machine_depth": {"value": 235},
            "machine_height": {"value": 250},
            "machine_nozzle_size": {"value": 0.4},
            "machine_heated_bed": {"value": True}
        }
    }
    src = tmp_path / "sample.def.json"
    src.write_text(json.dumps(cura, indent=2), encoding="utf-8")
    opk_printer = convert_cura_definition(src)
    # Valid per our printer schema
    S.validate("printer", opk_printer)
    assert opk_printer["name"] == "Sample Printer"
    assert opk_printer["build_volume"] == [235.0, 235.0, 250.0]
    assert opk_printer["nozzle_diameter"] == 0.4
    assert opk_printer["filament_diameter"] == 1.75

