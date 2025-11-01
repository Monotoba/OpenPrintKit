from pathlib import Path
import json
from opk.plugins.slicers.orca import generate_orca


def test_generate_orca(tmp_path: Path):
    pdl = {
        'name': 'TestPrinter',
        'firmware': 'marlin',
        'kinematics': 'cartesian',
        'geometry': {'bed_shape': [[0,0],[220,0],[220,220],[0,220]], 'z_height': 220},
        'extruders': [{'nozzle_diameter': 0.4}],
        'materials': [{'name':'PLA','filament_type':'PLA','filament_diameter':1.75,'nozzle_temperature':205,'bed_temperature':60}]
    }
    out = generate_orca(pdl, tmp_path)
    assert (tmp_path / 'printers').exists()
    assert (tmp_path / 'filaments').exists()
    assert (tmp_path / 'processes').exists()
    # validate JSON structure
    pr = json.loads((out['printer']).read_text(encoding='utf-8'))
    assert pr['type'] == 'printer'

